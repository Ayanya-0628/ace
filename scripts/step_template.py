# -*- coding: utf-8 -*-
"""
分步分析脚本模板
用法：复制此文件为 stepXX_xxx.py，修改 STEP_CONFIG 和 analyze() 函数
输出：一个独立的 .docx 文件（完整三线表 + 文字分析）
"""
import sys
import os
import numpy as np
import pandas as pd

# ══════ 防御性设置 ══════
sys.stdout.reconfigure(encoding='utf-8')
np.random.seed(42)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, r'C:\Users\16342\.antigravity\skills\ace\code_library')

# ══════ 步骤配置（每个脚本改这里） ══════
STEP_CONFIG = {
    'step_number': '01',                          # 步骤编号
    'step_name': '人口学基本特征',                   # 步骤名称
    'input_file': os.path.join(BASE_DIR, '原始数据', '数据.xlsx'),  # 输入文件
    'output_dir': os.path.join(BASE_DIR, '交付成果'),
    'cleaned_data': os.path.join(BASE_DIR, '交付成果', 'cleaned_data.xlsx'),  # 清洗后数据
}

# ══════ 第0层：数据加载 ══════
def load_data():
    """加载清洗后的数据（如果存在），否则加载原始数据"""
    cleaned = STEP_CONFIG['cleaned_data']
    if os.path.exists(cleaned):
        df = pd.read_excel(cleaned)
        print(f'加载已清洗数据: {cleaned}')
    else:
        df = pd.read_excel(STEP_CONFIG['input_file'])
        print(f'加载原始数据: {STEP_CONFIG["input_file"]}')
    
    df.columns = df.columns.str.strip().str.replace('\n', '', regex=False)
    df = df.replace('', np.nan)
    print(f'Shape: {df.shape}')
    return df

# ══════ 第1层：统计分析 ══════
def analyze(df):
    """
    执行本步骤的统计分析
    返回 results 字典，供报告生成使用
    
    TODO: 根据实际需求修改此函数
    """
    results = {}
    
    # 示例：人口学统计
    # from descriptive import demographic_table
    # results['demographic'] = demographic_table(df, [...])
    
    return results

# ══════ 第2层：报告生成 ══════
def generate_report(results, df):
    """
    生成独立的 Word 文档（完整三线表 + 文字分析）
    
    TODO: 根据实际需求修改此函数
    """
    from word_utils import create_report_doc, add_heading, add_body_text, add_three_line_table, add_note
    
    doc = create_report_doc()
    
    step_num = STEP_CONFIG['step_number']
    step_name = STEP_CONFIG['step_name']
    
    add_heading(doc, f'{step_name}', level=1)
    
    # TODO: 添加表格和文字分析
    # ✅ 正确：表+文字同步生成
    # add_three_line_table(doc, headers, data_rows, title=f'表X {step_name}')
    # add_note(doc, '注：...')
    # add_body_text(doc, f'由表X可知，...')
    
    # 保存
    output_dir = STEP_CONFIG['output_dir']
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f'{step_num}_{step_name}.docx')
    doc.save(output_path)
    print(f'\n✅ 步骤 {step_num} 完成: {output_path}')
    return output_path

# ══════ 主入口 ══════
if __name__ == '__main__':
    print(f'═══ Step {STEP_CONFIG["step_number"]}: {STEP_CONFIG["step_name"]} ═══\n')
    df = load_data()
    results = analyze(df)
    output_path = generate_report(results, df)

    # v4.0: Save step run metadata
    try:
        from impact_analyzer import ImpactAnalyzer
        analyzer = ImpactAnalyzer(BASE_DIR)
        analyzer.save_step_meta(STEP_CONFIG["step_number"], output_path)
    except Exception:
        pass
