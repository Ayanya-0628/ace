# -*- coding: utf-8 -*-
"""
ace scripts: diff_steps.py
用途：智能重跑受影响的步骤 + 自动备份 + 自动合并
日期：2026-03-28 (v4.0 新增)

用法：
  python diff_steps.py --steps 04 06          # 只重跑指定步骤
  python diff_steps.py --changed step00       # 自动分析影响范围并重跑
  python diff_steps.py --all                  # 全部重跑
  python diff_steps.py --stale                # 只重跑过期步骤
  python diff_steps.py --list                 # 查看项目步骤状态
"""
import sys
import os
import glob
import json
import shutil
import subprocess
import datetime

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.getcwd()
CODE_LIB = r'C:\Users\16342\.antigravity\skills\ace\code_library'
sys.path.insert(0, CODE_LIB)


def find_step_scripts(base_dir):
    """找到所有 stepXX_*.py 脚本并按编号排序"""
    pattern = os.path.join(base_dir, 'step[0-9][0-9]_*.py')
    scripts = sorted(glob.glob(pattern))
    result = {}
    for s in scripts:
        name = os.path.basename(s)
        num = name[4:6]
        result[f'step{num}'] = s
    return result


def backup_outputs(base_dir, step_nums):
    """备份将被重跑的步骤的输出文件"""
    output_dir = os.path.join(base_dir, '交付成果')
    if not os.path.exists(output_dir):
        return

    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = os.path.join(output_dir, f'.backup_{ts}')
    backed_up = []

    for f in os.listdir(output_dir):
        if not f.endswith('.docx'):
            continue
        # 检查是否属于要重跑的步骤
        for num in step_nums:
            if f.startswith(f'{num}_'):
                os.makedirs(backup_dir, exist_ok=True)
                src = os.path.join(output_dir, f)
                dst = os.path.join(backup_dir, f)
                shutil.copy2(src, dst)
                backed_up.append(f)
                break

    if backed_up:
        print(f'\n  Backup -> {backup_dir}')
        for b in backed_up:
            print(f'    {b}')
    return backup_dir if backed_up else None


def run_step(script_path):
    """运行一个步骤脚本"""
    name = os.path.basename(script_path)
    print(f'\n  Running: {name} ...', end='', flush=True)
    env = os.environ.copy()
    env['PYTHONUTF8'] = '1'
    result = subprocess.run(
        ['python', script_path],
        cwd=os.path.dirname(script_path),
        capture_output=True, text=True, encoding='utf-8', env=env
    )
    if result.returncode == 0:
        print(f' OK')
        return True
    else:
        print(f' FAILED')
        print(f'    stderr: {result.stderr[:500]}')
        return False


def run_merge(base_dir):
    """运行合并脚本"""
    merge_script = os.path.join(base_dir, 'merge_all.py')
    if os.path.exists(merge_script):
        print(f'\n  Running: merge_all.py ...', end='', flush=True)
        env = os.environ.copy()
        env['PYTHONUTF8'] = '1'
        result = subprocess.run(
            ['python', merge_script],
            cwd=base_dir,
            capture_output=True, text=True, encoding='utf-8', env=env
        )
        if result.returncode == 0:
            print(f' OK')
        else:
            print(f' FAILED')
            print(f'    stderr: {result.stderr[:500]}')


def save_run_meta(base_dir, step_nums):
    """保存每个重跑步骤的元数据"""
    try:
        from impact_analyzer import ImpactAnalyzer
        analyzer = ImpactAnalyzer(base_dir)
        for num in step_nums:
            output_file = glob.glob(os.path.join(base_dir, '交付成果', f'{num}_*.docx'))
            out = output_file[0] if output_file else ''
            analyzer.save_step_meta(num, out)
    except Exception:
        pass


def append_changelog(base_dir, step_nums, description=''):
    """追加 CHANGELOG.md 记录"""
    cl_path = os.path.join(base_dir, 'CHANGELOG.md')
    if not os.path.exists(cl_path):
        return

    ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    entry = f'\n---\n\n## [auto] {ts} - Rerun steps: {", ".join(step_nums)}\n'
    if description:
        entry += f'- {description}\n'
    entry += f'- Steps rerun: {", ".join(step_nums)}\n'

    with open(cl_path, 'a', encoding='utf-8') as f:
        f.write(entry)


def list_status(base_dir):
    """查看项目所有步骤的状态"""
    scripts = find_step_scripts(base_dir)
    meta_dir = os.path.join(base_dir, '交付成果', '.step_meta')

    print(f'\n=== Project Steps: {os.path.basename(base_dir)} ===\n')

    for step_id, script_path in sorted(scripts.items()):
        name = os.path.basename(script_path)
        num = step_id.replace('step', '')

        # 检查输出文件
        outputs = glob.glob(os.path.join(base_dir, '交付成果', f'{num}_*.docx'))
        has_output = bool(outputs)

        # 检查元数据
        meta_file = os.path.join(meta_dir, f'step{num}_last_run.json')
        last_run = ''
        stale = False
        if os.path.exists(meta_file):
            with open(meta_file, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            last_run = meta.get('last_run', '')[:16]

        status = 'OK' if has_output else 'NO OUTPUT'
        print(f'  {step_id}: {name}')
        print(f'         output: {status}  last_run: {last_run or "never"}')

    # 检查过期步骤
    try:
        from impact_analyzer import ImpactAnalyzer
        analyzer = ImpactAnalyzer(base_dir)
        stale = analyzer.check_stale_steps()
        if stale:
            print(f'\n  WARNING: Stale steps (data changed): {stale}')
    except Exception:
        pass


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Smart step re-runner for ace projects')
    parser.add_argument('--steps', nargs='+', help='Step numbers to rerun (e.g., 04 06)')
    parser.add_argument('--changed', help='Analyze impact of changing a step (e.g., step00)')
    parser.add_argument('--all', action='store_true', help='Rerun all steps')
    parser.add_argument('--stale', action='store_true', help='Rerun only stale steps')
    parser.add_argument('--list', action='store_true', help='List project step status')
    parser.add_argument('--no-merge', action='store_true', help='Skip merge after rerun')
    parser.add_argument('--no-backup', action='store_true', help='Skip backup before rerun')
    parser.add_argument('--dir', default='.', help='Project directory')
    parser.add_argument('--desc', default='', help='Description for changelog')
    args = parser.parse_args()

    project_dir = os.path.abspath(args.dir)
    all_scripts = find_step_scripts(project_dir)

    if not all_scripts:
        print(f'No step scripts found in {project_dir}')
        sys.exit(1)

    if args.list:
        list_status(project_dir)
        return

    # Determine which steps to run
    steps_to_run = []

    if args.all:
        steps_to_run = sorted(all_scripts.keys(), key=lambda s: s.replace('step', ''))

    elif args.changed:
        try:
            from impact_analyzer import ImpactAnalyzer
            analyzer = ImpactAnalyzer(project_dir)
            steps_to_run = analyzer.get_affected_steps(args.changed)
            analyzer.print_rerun_plan(steps_to_run)
        except ImportError:
            print('impact_analyzer not found, running all steps')
            steps_to_run = sorted(all_scripts.keys())

    elif args.stale:
        try:
            from impact_analyzer import ImpactAnalyzer
            analyzer = ImpactAnalyzer(project_dir)
            stale_nums = analyzer.check_stale_steps()
            steps_to_run = [f'step{n}' for n in stale_nums if f'step{n}' in all_scripts]
        except ImportError:
            print('impact_analyzer not found')
            sys.exit(1)

    elif args.steps:
        steps_to_run = [f'step{n}' for n in args.steps if f'step{n}' in all_scripts]

    if not steps_to_run:
        print('No steps to run')
        return

    step_nums = [s.replace('step', '') for s in steps_to_run]

    print(f'\n=== Smart Rerun ===')
    print(f'Project: {os.path.basename(project_dir)}')
    print(f'Steps:   {", ".join(steps_to_run)}')

    # 1. Backup
    if not args.no_backup:
        backup_outputs(project_dir, step_nums)

    # 2. Run steps
    success_count = 0
    fail_count = 0
    for step_id in steps_to_run:
        script = all_scripts.get(step_id)
        if script:
            ok = run_step(script)
            if ok:
                success_count += 1
            else:
                fail_count += 1

    # 3. Save metadata
    save_run_meta(project_dir, step_nums)

    # 4. Merge
    if not args.no_merge:
        run_merge(project_dir)

    # 5. Update changelog
    append_changelog(project_dir, step_nums, args.desc)

    # Summary
    print(f'\n=== Done ===')
    print(f'  Success: {success_count}  Failed: {fail_count}')
    if fail_count > 0:
        print(f'  WARNING: {fail_count} steps failed!')


if __name__ == '__main__':
    main()