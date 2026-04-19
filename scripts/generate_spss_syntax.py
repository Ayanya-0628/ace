# -*- coding: utf-8 -*-
"""
ACE Skill - SPSS 语法自动生成器
用法：根据项目具体变量名修改 CONFIG 部分，运行后生成 .sav + .sps

输入：pandas DataFrame（已清洗的问卷数据）
输出：
  - {项目名}_分析数据.sav  （带变量标签+值标签）
  - {项目名}_analysis.sps  （GBK编码，SPSS可直接运行）
"""

import pandas as pd
import numpy as np
import pyreadstat
import os

# ============================================================
# CONFIG - 每个项目修改这里
# ============================================================

PROJECT_NAME = '项目名'  # 生成文件前缀

# 人口统计变量: {变量名: 变量标签}
DEMO_VARS = {
    'gender': '性别',
    'age': '年龄',
    'education': '教育程度',
}

# 值标签: {变量名: {值: 标签}}
VALUE_LABELS = {
    'gender': {1: '男', 2: '女'},
    'age': {1: '18岁以下', 2: '18-25岁', 3: '26-35岁', 4: '36-45岁', 5: '45岁以上'},
    'education': {1: '高中及以下', 2: '本科/大专', 3: '研究生及以上'},
}

# 量表维度: {维度名: [题项变量名列表]}
DIMENSIONS = {
    '功能价值': ['Q8', 'Q9', 'Q10', 'Q11', 'Q12'],
    '情感价值': ['Q13', 'Q14', 'Q15'],
    '社会价值': ['Q16', 'Q17', 'Q18', 'Q19', 'Q20'],
}

# 因变量/结果变量
DEPENDENT_VAR = 'satisfaction'
DEPENDENT_LABEL = '总体满意度'
DEPENDENT_ITEMS = ['Q28', 'Q29', 'Q30', 'Q31']

# 题项标签: {变量名: 中文标签}
ITEM_LABELS = {
    'Q8': '活动流程安排合理',
    'Q9': '工具与材料齐全易用',
    # ... 补充所有题项
}

# t检验分组变量（二分类）
T_TEST_VARS = ['gender']

# ANOVA 分组变量（多分类）
ANOVA_VARS = ['age', 'education']

# EFA 提取因子数
N_FACTORS = 5

# ============================================================
# 核心逻辑 - 一般不需要修改
# ============================================================

def generate_sav(df, output_path):
    """导出 .sav 文件（带变量标签+值标签）"""
    # 构建完整 column_labels
    column_labels = {}
    column_labels.update(DEMO_VARS)
    column_labels.update(ITEM_LABELS)
    column_labels[DEPENDENT_VAR] = DEPENDENT_LABEL
    for dim_name, dim_cols in DIMENSIONS.items():
        var_name = dim_name.replace('（', '').replace('）', '')
        column_labels[var_name] = f'{dim_name}（均值）'
    
    # 确保数值列为 float
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].fillna('').astype(str)
        else:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    pyreadstat.write_sav(df, output_path,
                         column_labels=column_labels,
                         variable_value_labels=VALUE_LABELS)
    print(f'SAV 已保存: {output_path} ({df.shape})')


def generate_sps(sav_path, output_path, spv_path):
    """生成完整 SPSS .sps 语法文件（GBK编码）"""
    
    # 所有感知价值题项
    perceived_items = []
    for cols in DIMENSIONS.values():
        perceived_items.extend(cols)
    perceived_str = ' '.join(perceived_items)
    
    # 维度均值变量名
    dim_vars = list(DIMENSIONS.keys())
    dim_vars_str = ' '.join(dim_vars)
    dep_vars_str = ' '.join(dim_vars + [DEPENDENT_VAR])
    
    lines = []
    lines.append(f"* {PROJECT_NAME} - SPSS 全部分析语法.")
    lines.append(f"* 自动生成，运行后保存 .spv 输出文件.")
    lines.append("")
    lines.append(f"GET FILE='{os.path.abspath(sav_path)}'.")
    lines.append("")
    
    # 计算维度均值
    lines.append("* === 计算维度均值 ===.")
    for dim_name, dim_cols in DIMENSIONS.items():
        cols_str = ','.join(dim_cols)
        lines.append(f"COMPUTE {dim_name} = MEAN({cols_str}).")
    dep_str = ','.join(DEPENDENT_ITEMS)
    lines.append(f"COMPUTE {DEPENDENT_VAR} = MEAN({dep_str}).")
    lines.append("EXECUTE.")
    lines.append("")
    
    # 变量标签
    for dim_name in DIMENSIONS:
        lines.append(f"VARIABLE LABELS {dim_name} '{dim_name}（均值）'.")
    lines.append(f"VARIABLE LABELS {DEPENDENT_VAR} '{DEPENDENT_LABEL}（均值）'.")
    lines.append("")
    
    # === 信度分析 ===
    lines.append("* ============================================================.")
    lines.append("* 1. 信度分析.")
    lines.append("* ============================================================.")
    lines.append("")
    
    for dim_name, dim_cols in DIMENSIONS.items():
        cols_str = ' '.join(dim_cols)
        lines.append(f"TITLE '信度分析 - {dim_name}'.")
        lines.append(f"RELIABILITY /VARIABLES={cols_str}")
        lines.append(f"  /SCALE('{dim_name}') ALL")
        lines.append("  /MODEL=ALPHA")
        lines.append("  /STATISTICS=DESCRIPTIVE SCALE")
        lines.append("  /SUMMARY=TOTAL.")
        lines.append("")
    
    # 总量表
    lines.append("TITLE '信度分析 - 感知价值总量表'.")
    lines.append(f"RELIABILITY /VARIABLES={perceived_str}")
    lines.append("  /SCALE('感知价值总量表') ALL")
    lines.append("  /MODEL=ALPHA")
    lines.append("  /STATISTICS=DESCRIPTIVE SCALE")
    lines.append("  /SUMMARY=TOTAL.")
    lines.append("")
    
    # === 因子分析 ===
    lines.append("* ============================================================.")
    lines.append("* 2. KMO + 探索性因子分析.")
    lines.append("* ============================================================.")
    lines.append("")
    lines.append("TITLE 'KMO和Bartlett检验 + EFA'.")
    lines.append(f"FACTOR /VARIABLES={perceived_str}")
    lines.append("  /MISSING LISTWISE")
    lines.append("  /PRINT INITIAL KMO EXTRACTION ROTATION")
    lines.append(f"  /CRITERIA FACTORS({N_FACTORS}) ITERATE(25)")
    lines.append("  /EXTRACTION PC")
    lines.append("  /ROTATION VARIMAX.")
    lines.append("")
    
    # === 描述统计 ===
    lines.append("* ============================================================.")
    lines.append("* 3. 描述统计.")
    lines.append("* ============================================================.")
    lines.append("")
    
    demo_vars_str = ' '.join(DEMO_VARS.keys())
    lines.append("TITLE '人口统计学频次'.")
    lines.append(f"FREQUENCIES VARIABLES={demo_vars_str}")
    lines.append("  /ORDER=ANALYSIS.")
    lines.append("")
    
    all_items_str = ' '.join(list(ITEM_LABELS.keys()) + dim_vars + [DEPENDENT_VAR])
    lines.append("TITLE '量表描述统计'.")
    lines.append(f"DESCRIPTIVES VARIABLES={all_items_str}")
    lines.append("  /STATISTICS=MEAN STDDEV MIN MAX VARIANCE SKEWNESS KURTOSIS.")
    lines.append("")
    
    # === 相关分析 ===
    lines.append("* ============================================================.")
    lines.append("* 4. Pearson 相关分析.")
    lines.append("* ============================================================.")
    lines.append("")
    lines.append("TITLE 'Pearson相关分析'.")
    lines.append("CORRELATIONS")
    lines.append(f"  /VARIABLES={dep_vars_str}")
    lines.append("  /PRINT=TWOTAIL NOSIG")
    lines.append("  /MISSING=PAIRWISE.")
    lines.append("")
    
    # === t 检验 ===
    lines.append("* ============================================================.")
    lines.append("* 5. 独立样本 t 检验.")
    lines.append("* ============================================================.")
    lines.append("")
    
    for t_var in T_TEST_VARS:
        vals = sorted(VALUE_LABELS.get(t_var, {}).keys())
        if len(vals) >= 2:
            lines.append(f"TITLE '独立样本t检验 - {DEMO_VARS.get(t_var, t_var)}'.")
            lines.append(f"T-TEST GROUPS={t_var}({vals[0]} {vals[1]})")
            lines.append("  /MISSING=ANALYSIS")
            lines.append(f"  /VARIABLES={dep_vars_str}")
            lines.append("  /CRITERIA=CI(.95).")
            lines.append("")
    
    # === ANOVA ===
    lines.append("* ============================================================.")
    lines.append("* 6. 单因素 ANOVA + LSD 事后比较.")
    lines.append("* ============================================================.")
    lines.append("")
    
    for a_var in ANOVA_VARS:
        lines.append(f"TITLE '单因素ANOVA - {DEMO_VARS.get(a_var, a_var)}'.")
        lines.append(f"ONEWAY {dep_vars_str} BY {a_var}")
        lines.append("  /STATISTICS DESCRIPTIVES HOMOGENEITY")
        lines.append("  /MISSING ANALYSIS")
        lines.append("  /POSTHOC=LSD ALPHA(0.05).")
        lines.append("")
    
    # === 回归 ===
    lines.append("* ============================================================.")
    lines.append("* 7. 多元线性回归.")
    lines.append("* ============================================================.")
    lines.append("")
    lines.append("TITLE '多元线性回归分析'.")
    lines.append("REGRESSION")
    lines.append("  /MISSING LISTWISE")
    lines.append("  /STATISTICS COEFF OUTS R ANOVA COLLIN TOL")
    lines.append("  /CRITERIA=PIN(.05) POUT(.10)")
    lines.append("  /NOORIGIN")
    lines.append(f"  /DEPENDENT {DEPENDENT_VAR}")
    lines.append(f"  /METHOD=ENTER {dim_vars_str}")
    lines.append("  /RESIDUALS DURBIN.")
    lines.append("")
    
    # === 保存输出 ===
    lines.append("* ============================================================.")
    lines.append("* 保存 .spv 输出.")
    lines.append("* ============================================================.")
    lines.append("")
    lines.append(f"OUTPUT SAVE OUTFILE='{os.path.abspath(spv_path)}'.")
    
    # 写入 GBK 编码
    content = '\n'.join(lines)
    with open(output_path, 'w', encoding='gbk') as f:
        f.write(content)
    
    print(f'SPS 已保存: {output_path} (GBK编码, {len(lines)}行)')
    print(f'在 SPSS 中打开运行全部即可生成: {spv_path}')


# ============================================================
# 入口 - 直接运行示例
# ============================================================
if __name__ == '__main__':
    print("这是模板脚本，请根据具体项目修改 CONFIG 部分后使用。")
    print("用法：")
    print("  1. 修改 CONFIG 中的变量名、维度划分等")
    print("  2. 准备好 pandas DataFrame")
    print("  3. 调用 generate_sav(df, 'output.sav')")
    print("  4. 调用 generate_sps('output.sav', 'analysis.sps', 'output.spv')")
    print("  5. 在 SPSS 中打开 .sps 文件，运行全部")
