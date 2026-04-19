# -*- coding: utf-8 -*-
"""
一键创建新项目目录框架（分步执行架构版）
用法：python scripts/new_project.py "项目名称" [步骤数]
输出：标准项目目录 + step00-stepN 脚本 + merge_all.py
"""
import os
import sys
import json
import datetime

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODE_LIB = os.path.join(SKILL_DIR, 'code_library')

# 默认分步列表（问卷分析全套，最常见）
DEFAULT_STEPS = [
    ('01', '人口学基本特征', 'demographic_table'),
    ('02', '信度效度分析', 'cronbachs_alpha, kmo_bartlett'),
    ('03', '描述性统计', 'descriptive_stats'),
    ('04', '差异分析', 'independent_ttest, oneway_anova'),
    ('05', '相关分析', 'correlation_matrix_stars'),
    ('06', '回归分析', 'ols_regression'),
]


def create_step_script(base, num, name, funcs, date_str):
    """生成一个分步脚本"""
    content = f'''# -*- coding: utf-8 -*-
"""
用途：Step {num} - {name}
输入文件：交付成果/cleaned_data.xlsx
输出文件：交付成果/{num}_{name}.docx
日期：{date_str}
"""
import sys
import os
import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')
np.random.seed(42)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, r'{CODE_LIB}')

CLEANED_DATA = os.path.join(BASE_DIR, '交付成果', 'cleaned_data.xlsx')
OUTPUT_DIR = os.path.join(BASE_DIR, '交付成果')

# ══════ 数据加载 ══════
def load_data():
    df = pd.read_excel(CLEANED_DATA)
    print(f'Shape: {{df.shape}}')
    return df

# ══════ 统计分析 ══════
def analyze(df):
    results = {{}}
    # TODO: from {funcs.split(",")[0].strip()} import ...
    return results

# ══════ 报告生成 ══════
def generate_report(results, df):
    from word_utils import create_report_doc, add_heading, add_body_text, add_three_line_table, add_note
    doc = create_report_doc()
    add_heading(doc, '{name}', level=1)
    # TODO: 表格 + 文字分析
    output_path = os.path.join(OUTPUT_DIR, '{num}_{name}.docx')
    doc.save(output_path)
    print(f'✅ Step {num} 完成: {{output_path}}')

# ══════ 主入口 ══════
if __name__ == '__main__':
    print(f'═══ Step {num}: {name} ═══')
    df = load_data()
    results = analyze(df)
    generate_report(results, df)
'''
    path = os.path.join(base, f'step{num}_{name.replace("/", "_")}.py')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return path


def create_project(name):
    """创建分步执行架构的项目目录"""
    base = os.path.join(os.getcwd(), name)
    date_str = datetime.date.today().isoformat()

    # 1. 创建目录
    for d in ['原始数据', '需求整理', '交付成果']:
        os.makedirs(os.path.join(base, d), exist_ok=True)

    # 2. 生成 step00_clean.py
    clean_script = f'''# -*- coding: utf-8 -*-
"""
用途：Step 00 - 数据清洗（所有后续步骤依赖此脚本输出的 cleaned_data.xlsx）
输入文件：原始数据/xxx.xlsx
输出文件：交付成果/cleaned_data.xlsx
日期：{date_str}
"""
import sys
import os
import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')
np.random.seed(42)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, r'{CODE_LIB}')

INPUT_FILE = os.path.join(BASE_DIR, '原始数据', '数据.xlsx')   # TODO: 修改文件名
OUTPUT_DIR = os.path.join(BASE_DIR, '交付成果')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ══════ 数据清洗 ══════
def clean_data():
    df = pd.read_excel(INPUT_FILE)
    df.columns = df.columns.str.strip().str.replace('\\n', '', regex=False)
    df = df.replace('', np.nan)
    print(f'原始数据: {{df.shape}}')

    # TODO: 反向计分
    # from data_clean import reverse_score
    # df = reverse_score(df, ['Q4', 'Q8'], max_val=5)

    # TODO: 计算维度得分
    # from data_clean import calc_dimension_scores
    # df = calc_dimension_scores(df, dims_config)

    # TODO: 编码校验
    # from data_clean import check_encoding
    # check_encoding(df, '性别', {{1: '男', 2: '女'}})

    # 正态性检验决策
    from pretest import normality_decision
    # norm = normality_decision(df, ['维度1', '维度2'])
    # print(norm)

    # 保存清洗后数据
    output_path = os.path.join(OUTPUT_DIR, 'cleaned_data.xlsx')
    df.to_excel(output_path, index=False)
    print(f'✅ 清洗完成: {{output_path}}')
    return df

if __name__ == '__main__':
    print('═══ Step 00: 数据清洗 ═══')
    clean_data()
'''
    with open(os.path.join(base, 'step00_clean.py'), 'w', encoding='utf-8') as f:
        f.write(clean_script)
    print(f'  ✅ step00_clean.py')

    # 3. 生成分步脚本
    for num, step_name, funcs in DEFAULT_STEPS:
        path = create_step_script(base, num, step_name, funcs, date_str)
        print(f'  ✅ {os.path.basename(path)}')

    # 4. 生成 merge_all.py
    merge_script = f'''# -*- coding: utf-8 -*-
"""
用途：合并所有分步文档为一份完整报告
日期：{date_str}
"""
import sys
import os
sys.path.insert(0, r'{os.path.join(SKILL_DIR, "scripts")}')
from merge_report import merge_docx_files

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '交付成果')
OUTPUT_PATH = os.path.join(OUTPUT_DIR, '分析报告（合并版）.docx')

if __name__ == '__main__':
    merge_docx_files(OUTPUT_DIR, OUTPUT_PATH, title='{name} - 数据分析报告')
'''
    with open(os.path.join(base, 'merge_all.py'), 'w', encoding='utf-8') as f:
        f.write(merge_script)
    print(f'  ✅ merge_all.py')

    # 5. v4.0: CHANGELOG.md
    cl = ['# \u4fee\u6539\u65e5\u5fd7\n\n']
    cl.append(f'## [v1.0] {date_str} - \u521d\u7248\u4ea4\u4ed8\n\n')
    cl.append('| \u6b65\u9aa4 | \u811a\u672c | \u8f93\u51fa | \u72b6\u6001 |\n|------|------|------|------|\n')
    cl.append('| step00 | step00_clean.py | cleaned_data.xlsx | pending |\n')
    for num2, sn2, _ in DEFAULT_STEPS:
        cl.append(f'| step{num2} | step{num2}_{sn2}.py | {num2}_{sn2}.docx | pending |\n')
    with open(os.path.join(base, 'CHANGELOG.md'), 'w', encoding='utf-8') as f:
        f.writelines(cl)
    print('  ok CHANGELOG.md')
    # 6. v4.0: impact_map.json
    imp = {'version':'1.0','data_source':'\u4ea4\u4ed8\u6210\u679c/cleaned_data.xlsx','steps':{}}
    imp['steps']['step00'] = {'script':'step00_clean.py','type':'clean','outputs':['\u4ea4\u4ed8\u6210\u679c/cleaned_data.xlsx'],'variables_defined':[],'downstream':[f'step{n}' for n,_,_ in DEFAULT_STEPS]}
    for num2, sn2, _ in DEFAULT_STEPS:
        imp['steps'][f'step{num2}'] = {'script':f'step{num2}_{sn2}.py','type':'analysis','outputs':[f'\u4ea4\u4ed8\u6210\u679c/{num2}_{sn2}.docx'],'depends_on':['step00'],'variables_used':[],'downstream':[]}
    with open(os.path.join(base, 'impact_map.json'), 'w', encoding='utf-8') as f:
        json.dump(imp, f, ensure_ascii=False, indent=2)
    print('  ok impact_map.json')

    print(f'\n✅ 项目 "{name}" 创建完成（分步执行架构）')
    print(f'   目录: {base}')
    print(f'   文件: step00~06 + merge_all + CHANGELOG + impact_map')
    print(f'\n📋 下一步:')
    print(f'   1. 将客户数据放入 原始数据/')
    print(f'   2. 修改 step00_clean.py 中的文件名和清洗逻辑')
    print(f'   3. 按需修改/增删 step01~06')
    print(f'   4. 依次运行 step00 → step01 → ... → merge_all.py')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('用法: python scripts/new_project.py "项目名称"')
        print('      生成分步执行架构的完整项目框架')
        sys.exit(1)
    create_project(sys.argv[1])
