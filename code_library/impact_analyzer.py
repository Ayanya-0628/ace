# -*- coding: utf-8 -*-
"""
ace code_library: impact_analyzer.py
用途：根据 impact_map.json 分析修改的影响范围，生成重跑步骤列表
日期：2026-03-28 (v4.0 新增)

使用方式：
    from impact_analyzer import ImpactAnalyzer
    analyzer = ImpactAnalyzer('项目目录/')
    affected = analyzer.get_affected_steps('step00')
    analyzer.print_rerun_plan(affected)
"""
import json
import os
import hashlib
import datetime


class ImpactAnalyzer:
    """分析修改影响范围，推导需要重跑的步骤"""

    def __init__(self, project_dir):
        self.project_dir = project_dir
        self.map_path = os.path.join(project_dir, 'impact_map.json')
        self.meta_dir = os.path.join(project_dir, '交付成果', '.step_meta')
        self.impact_map = self._load_map()

    def _load_map(self):
        if not os.path.exists(self.map_path):
            print(f'warning: no impact_map.json: {self.map_path}')
            return None
        with open(self.map_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_affected_steps(self, changed_step):
        """给定修改了哪个步骤，返回所有受影响的步骤列表（含自身）"""
        if not self.impact_map:
            return []
        steps = self.impact_map.get('steps', {})
        if changed_step not in steps:
            return [changed_step]
        affected = set()
        self._collect_downstream(changed_step, steps, affected)
        affected.add(changed_step)
        return sorted(affected, key=lambda s: s.replace('step', ''))

    def _collect_downstream(self, step_id, steps, affected):
        info = steps.get(step_id, {})
        for ds in info.get('downstream', []):
            if ds not in affected:
                affected.add(ds)
                self._collect_downstream(ds, steps, affected)

    def get_affected_by_variable(self, variable_name):
        """给定修改了哪个变量，返回使用该变量的所有步骤"""
        if not self.impact_map:
            return []
        affected = []
        for step_id, info in self.impact_map.get('steps', {}).items():
            vars_used = info.get('variables_used', [])
            vars_defined = info.get('variables_defined', [])
            if variable_name in vars_used or variable_name in vars_defined:
                affected.append(step_id)
        return sorted(affected, key=lambda s: s.replace('step', ''))

    def classify_change(self, description):
        """根据修改描述判断修改类型"""
        data_kw = ['清洗','筛选','过滤','删除样本','缺失值','反向计分','编码','重新编码','变量定义','维度','计算方式']
        param_kw = ['控制变量','自变量','因变量','中介变量','调节变量','显著性','bootstrap','回归模型','去掉','增加','替换','换成']
        fmt_kw = ['字体','格式','表格','列宽','标题','措辞','文字','颜色','粗体','行距','缩进','对齐','表注','图题']
        add_kw = ['新增','增加分析','补充','追加','多做一个']

        for kw in data_kw:
            if kw in description:
                return {'type': 'data_logic', 'level': 'high', 'label': '数据/逻辑修改',
                        'suggestion': '若step00变了，所有下游必须重跑'}
        for kw in param_kw:
            if kw in description:
                return {'type': 'param', 'level': 'medium', 'label': '分析参数修改',
                        'suggestion': '只重跑涉及修改的stepN + 重新合并'}
        for kw in fmt_kw:
            if kw in description:
                return {'type': 'format', 'level': 'low', 'label': '格式/文字修改',
                        'suggestion': '只重跑对应stepN + 重新合并'}
        for kw in add_kw:
            if kw in description:
                return {'type': 'add_new', 'level': 'low', 'label': '新增分析',
                        'suggestion': '新建stepN+1 + 重新合并'}
        return {'type': 'unknown', 'level': 'unknown', 'label': '未识别',
                'suggestion': '请人工分析影响范围'}

    def get_data_hash(self, filepath):
        if not os.path.exists(filepath):
            return None
        h = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)
        return h.hexdigest()

    def save_step_meta(self, step_num, output_file, variables_used=None):
        """保存步骤运行元数据"""
        os.makedirs(self.meta_dir, exist_ok=True)
        ds = self.impact_map.get('data_source', '交付成果/cleaned_data.xlsx') if self.impact_map else '交付成果/cleaned_data.xlsx'
        data_hash = self.get_data_hash(os.path.join(self.project_dir, ds))
        meta = {
            'step': step_num,
            'last_run': datetime.datetime.now().isoformat(),
            'data_hash': data_hash,
            'output_file': output_file,
            'variables_used': variables_used or [],
        }
        mf = os.path.join(self.meta_dir, f'step{step_num}_last_run.json')
        with open(mf, 'w', encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

    def check_stale_steps(self):
        """检查哪些步骤的输出已过期"""
        if not os.path.exists(self.meta_dir):
            return []
        ds = self.impact_map.get('data_source', '交付成果/cleaned_data.xlsx') if self.impact_map else '交付成果/cleaned_data.xlsx'
        current_hash = self.get_data_hash(os.path.join(self.project_dir, ds))
        if not current_hash:
            return []
        stale = []
        for mf in sorted(os.listdir(self.meta_dir)):
            if not mf.endswith('_last_run.json'):
                continue
            with open(os.path.join(self.meta_dir, mf), 'r', encoding='utf-8') as f:
                meta = json.load(f)
            if meta.get('data_hash') != current_hash:
                stale.append(meta['step'])
        return stale

    def print_rerun_plan(self, affected_steps):
        if not self.impact_map:
            print('no impact_map.json')
            return
        steps = self.impact_map.get('steps', {})
        print('\n=== Rerun Plan ===\n')
        for sid in affected_steps:
            info = steps.get(sid, {})
            print(f'  > {sid}: python {info.get("script", sid + ".py")}')
        print(f'  > merge: python merge_all.py')
        print(f'\n{len(affected_steps)} steps to rerun\n')

    def generate_changelog_entry(self, version, summary, changes, change_type, affected_steps, date_str=None):
        if not date_str:
            date_str = datetime.date.today().isoformat()
        steps = self.impact_map.get('steps', {}) if self.impact_map else {}
        lines = [f'\n## [{version}] {date_str} - {summary}\n', '### 客户要求']
        for c in changes:
            lines.append(f'- {c}')
        lines.append(f'\n### 修改类型：{change_type}\n')
        lines.append('### 影响范围')
        lines.append('| 步骤 | 是否受影响 | 脚本 | 操作 |')
        lines.append('|------|-----------|------|------|')
        for sid in sorted(steps.keys(), key=lambda s: s.replace('step', '')):
            info = steps.get(sid, {})
            script = info.get('script', sid + '.py')
            if sid in affected_steps:
                lines.append(f'| {sid} | YES | {script} | rerun |')
            else:
                lines.append(f'| {sid} | NO | {script} | skip |')
        lines.append('\n### 重跑命令')
        lines.append('```bash')
        for sid in affected_steps:
            lines.append(f'python {steps.get(sid, {}).get("script", sid + ".py")}')
        lines.append('python merge_all.py')
        lines.append('```\n')
        return '\n'.join(lines)


def analyze_impact(project_dir, changed_step):
    a = ImpactAnalyzer(project_dir)
    affected = a.get_affected_steps(changed_step)
    a.print_rerun_plan(affected)
    return affected

def check_stale(project_dir):
    a = ImpactAnalyzer(project_dir)
    stale = a.check_stale_steps()
    if stale:
        print(f'Stale steps: {stale}')
    else:
        print('All steps up to date')
    return stale

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('Usage:')
        print('  python impact_analyzer.py <dir> --changed step00')
        print('  python impact_analyzer.py <dir> --stale')
        print('  python impact_analyzer.py <dir> --var varname')
        sys.exit(1)
    pd = sys.argv[1]
    a = ImpactAnalyzer(pd)
    if '--changed' in sys.argv:
        i = sys.argv.index('--changed')
        affected = a.get_affected_steps(sys.argv[i+1])
        a.print_rerun_plan(affected)
    elif '--stale' in sys.argv:
        check_stale(pd)
    elif '--var' in sys.argv:
        i = sys.argv.index('--var')
        print(f'Steps using "{sys.argv[i+1]}": {a.get_affected_by_variable(sys.argv[i+1])}')
    elif '--classify' in sys.argv:
        i = sys.argv.index('--classify')
        r = a.classify_change(' '.join(sys.argv[i+1:]))
        print(f'Type: {r["label"]}, Level: {r["level"]}, Suggestion: {r["suggestion"]}')