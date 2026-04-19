# -*- coding: utf-8 -*-
"""
ace scripts: version_manager.py
用途：项目交付版本管理 — 快照/列表/对比
日期：2026-03-28 (v4.0)

用法：
  python version_manager.py snapshot              # 快照当前交付成果为 v1/v2/...
  python version_manager.py snapshot --tag "初版"   # 带标签
  python version_manager.py list                   # 列出所有版本
  python version_manager.py diff v1 v2             # 对比两个版本
  python version_manager.py restore v1             # 从v1恢复到交付成果/
"""
import sys
import os
import re
import glob
import shutil
import json
import datetime

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.getcwd()


def get_next_version(base_dir):
    """自动计算下一个版本号"""
    existing = []
    for d in os.listdir(base_dir):
        m = re.match(r'^v(\d+)$', d)
        if m and os.path.isdir(os.path.join(base_dir, d)):
            existing.append(int(m.group(1)))
    return max(existing) + 1 if existing else 1


def snapshot(base_dir, tag=''):
    """将交付成果/快照为新版本文件夹"""
    src = os.path.join(base_dir, '交付成果')
    if not os.path.exists(src):
        print('ERROR: 交付成果/ not found')
        return None

    # Check if there are any files
    files = [f for f in os.listdir(src)
             if not f.startswith('.') and not os.path.isdir(os.path.join(src, f))]
    if not files:
        print('ERROR: 交付成果/ is empty')
        return None

    ver_num = get_next_version(base_dir)
    ver_name = f'v{ver_num}'
    dst = os.path.join(base_dir, ver_name)

    # Copy all files (not subdirs like .step_meta or .backup_*)
    os.makedirs(dst, exist_ok=True)
    copied = []
    for f in files:
        src_f = os.path.join(src, f)
        if os.path.isfile(src_f):
            shutil.copy2(src_f, os.path.join(dst, f))
            copied.append(f)

    # Write version metadata
    meta = {
        'version': ver_name,
        'created': datetime.datetime.now().isoformat(),
        'tag': tag,
        'files': copied,
        'file_count': len(copied),
    }
    with open(os.path.join(dst, '.version_meta.json'), 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    # Also append to CHANGELOG if exists
    cl_path = os.path.join(base_dir, 'CHANGELOG.md')
    if os.path.exists(cl_path):
        ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        entry = f'\n---\n\n## [{ver_name}] {ts} - {tag or "版本快照"}\n'
        entry += f'- 文件数: {len(copied)}\n'
        entry += f'- 目录: {ver_name}/\n'
        with open(cl_path, 'a', encoding='utf-8') as f:
            f.write(entry)

    print(f'\n=== Snapshot: {ver_name} ===')
    if tag:
        print(f'  Tag: {tag}')
    print(f'  Files: {len(copied)}')
    for f in copied:
        size_kb = os.path.getsize(os.path.join(dst, f)) // 1024
        print(f'    {f} ({size_kb}KB)')
    print(f'  Dir: {dst}')
    return ver_name


def list_versions(base_dir):
    """列出所有版本"""
    versions = []
    for d in sorted(os.listdir(base_dir)):
        m = re.match(r'^v(\d+)$', d)
        if m and os.path.isdir(os.path.join(base_dir, d)):
            meta_path = os.path.join(base_dir, d, '.version_meta.json')
            meta = {}
            if os.path.exists(meta_path):
                with open(meta_path, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
            versions.append((d, meta))

    if not versions:
        print('No versions found')
        return

    print(f'\n=== Versions ({len(versions)}) ===\n')
    for ver, meta in versions:
        tag = meta.get('tag', '')
        created = meta.get('created', '')[:16]
        count = meta.get('file_count', '?')
        tag_str = f' [{tag}]' if tag else ''
        print(f'  {ver}{tag_str}  ({count} files)  {created}')

    # Also show current 交付成果/
    src = os.path.join(base_dir, '交付成果')
    if os.path.exists(src):
        cur_files = [f for f in os.listdir(src) if not f.startswith('.') and os.path.isfile(os.path.join(src, f))]
        print(f'\n  [current] 交付成果/ ({len(cur_files)} files)')


def diff_versions(base_dir, v1, v2):
    """对比两个版本的文件差异"""
    d1 = os.path.join(base_dir, v1)
    d2 = os.path.join(base_dir, v2)

    if not os.path.exists(d1):
        print(f'ERROR: {v1}/ not found')
        return
    if not os.path.exists(d2):
        print(f'ERROR: {v2}/ not found')
        return

    files1 = set(f for f in os.listdir(d1) if not f.startswith('.'))
    files2 = set(f for f in os.listdir(d2) if not f.startswith('.'))

    only_v1 = files1 - files2
    only_v2 = files2 - files1
    common = files1 & files2

    print(f'\n=== Diff: {v1} vs {v2} ===\n')

    if only_v1:
        print(f'  Only in {v1}:')
        for f in sorted(only_v1):
            print(f'    - {f}')

    if only_v2:
        print(f'  Only in {v2}:')
        for f in sorted(only_v2):
            print(f'    + {f}')

    # Compare common files by size
    changed = []
    unchanged = []
    for f in sorted(common):
        s1 = os.path.getsize(os.path.join(d1, f))
        s2 = os.path.getsize(os.path.join(d2, f))
        if s1 != s2:
            changed.append((f, s1, s2))
        else:
            unchanged.append(f)

    if changed:
        print(f'  Changed:')
        for f, s1, s2 in changed:
            print(f'    ~ {f} ({s1//1024}KB -> {s2//1024}KB)')

    if unchanged:
        print(f'  Unchanged: {len(unchanged)} files')


def restore_version(base_dir, ver):
    """从某个版本恢复到交付成果/"""
    src = os.path.join(base_dir, ver)
    dst = os.path.join(base_dir, '交付成果')

    if not os.path.exists(src):
        print(f'ERROR: {ver}/ not found')
        return

    # Backup current first
    if os.path.exists(dst):
        cur_files = [f for f in os.listdir(dst) if os.path.isfile(os.path.join(dst, f)) and not f.startswith('.')]
        if cur_files:
            ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            bak = os.path.join(dst, f'.backup_{ts}')
            os.makedirs(bak, exist_ok=True)
            for f in cur_files:
                shutil.copy2(os.path.join(dst, f), os.path.join(bak, f))
            print(f'  Backed up current to {bak}')

    # Copy version files to 交付成果/
    copied = 0
    for f in os.listdir(src):
        if f.startswith('.'):
            continue
        sf = os.path.join(src, f)
        if os.path.isfile(sf):
            shutil.copy2(sf, os.path.join(dst, f))
            copied += 1

    print(f'\n=== Restored {ver} -> 交付成果/ ({copied} files) ===')


def init_requirements_dir(base_dir):
    """初始化需求整理文件夹"""
    req_dir = os.path.join(base_dir, '需求整理')
    os.makedirs(req_dir, exist_ok=True)
    readme = os.path.join(req_dir, 'README.md')
    if not os.path.exists(readme):
        with open(readme, 'w', encoding='utf-8') as f:
            f.write('# 需求整理\n\n')
            f.write('> 将客户的需求文档、截图、参考论文放在这里。\n\n')
            f.write('## 文件清单\n')
            f.write('- （在此列出客户提供的文件）\n\n')
            f.write('## 分析要求摘要\n')
            f.write('- （在此整理客户的分析要求）\n')
    print(f'  ok 需求整理/')
    return req_dir


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Version manager for ace projects')
    parser.add_argument('action', choices=['snapshot', 'list', 'diff', 'restore', 'init-req'],
                        help='Action to perform')
    parser.add_argument('args', nargs='*', help='Additional arguments')
    parser.add_argument('--tag', default='', help='Version tag for snapshot')
    parser.add_argument('--dir', default='.', help='Project directory')
    args = parser.parse_args()

    project_dir = os.path.abspath(args.dir)

    if args.action == 'snapshot':
        snapshot(project_dir, args.tag)
    elif args.action == 'list':
        list_versions(project_dir)
    elif args.action == 'diff':
        if len(args.args) < 2:
            print('Usage: version_manager.py diff v1 v2')
            sys.exit(1)
        diff_versions(project_dir, args.args[0], args.args[1])
    elif args.action == 'restore':
        if len(args.args) < 1:
            print('Usage: version_manager.py restore v1')
            sys.exit(1)
        restore_version(project_dir, args.args[0])
    elif args.action == 'init-req':
        init_requirements_dir(project_dir)
