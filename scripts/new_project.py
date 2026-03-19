# -*- coding: utf-8 -*-
"""
一键创建新项目目录框架
用法：python scripts/new_project.py "项目名称"
输出：在当前目录创建标准项目文件夹结构
"""
import os
import sys
import datetime

def create_project(name):
    """创建标准项目目录结构"""
    base = os.path.join(os.getcwd(), name)
    
    dirs = [
        os.path.join(base, '原始数据'),
        os.path.join(base, '交付成果'),
    ]
    
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f'  ✅ 创建目录: {d}')
    
    # 创建 analysis_template.py
    template = f'''# -*- coding: utf-8 -*-
"""
用途：{name} - 数据分析脚本
输入文件：原始数据/xxx.xlsx
输出文件：交付成果/分析报告.docx
日期：{datetime.date.today().isoformat()}
"""
import sys
import os
import numpy as np
import pandas as pd

# ══════ 防御性设置 ══════
sys.stdout.reconfigure(encoding='utf-8')
np.random.seed(42)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, '原始数据', '数据.xlsx')   # TODO: 修改
OUTPUT_DIR = os.path.join(BASE_DIR, '交付成果')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 添加 code_library 到 path
sys.path.insert(0, r'C:\\Users\\16342\\.antigravity\\skills\\ace\\code_library')

# ══════ 第0层：配置 ══════
ANALYSIS_CONFIG = {{
    'project_name': '{name}',
    'input_file': INPUT_FILE,
    'output_dir': OUTPUT_DIR,
}}

# ══════ 第1层：数据加载与清洗 ══════
def load_data():
    df = pd.read_excel(INPUT_FILE)
    df.columns = df.columns.str.strip().str.replace('\\n', '', regex=False)
    df = df.replace('', np.nan)
    print(f'Shape: {{df.shape}}')
    print(f'Columns: {{list(df.columns)}}')
    return df

# ══════ 第2层：统计分析 ══════
def analyze(df):
    results = {{}}
    # TODO: 添加分析代码
    return results

# ══════ 第3层：报告生成 ══════
def generate_report(results):
    from word_utils import create_report_doc, add_heading, add_body_text
    doc = create_report_doc()
    add_heading(doc, '{name} - 分析报告', level=0)
    # TODO: 添加表格和文字分析
    output_path = os.path.join(OUTPUT_DIR, '分析报告.docx')
    doc.save(output_path)
    print(f'报告已保存: {{output_path}}')

# ══════ 主入口 ══════
if __name__ == '__main__':
    df = load_data()
    results = analyze(df)
    generate_report(results)
    print('\\n✅ 全部完成')
'''
    
    template_path = os.path.join(base, 'analysis.py')
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(template)
    print(f'  ✅ 创建模板: {template_path}')
    
    print(f'\n✅ 项目 "{name}" 创建完成')
    print(f'   目录: {base}')
    print(f'   下一步: 将客户数据放入 原始数据/ 目录，修改 analysis.py')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('用法: python scripts/new_project.py "项目名称"')
        sys.exit(1)
    create_project(sys.argv[1])
