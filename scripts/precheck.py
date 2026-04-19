# -*- coding: utf-8 -*-
"""
一键前置检验脚本
用法：python scripts/precheck.py "数据文件.xlsx" "col1,col2,col3"
输出：正态性/方差齐性/VIF 检验结果
"""
import sys
import os
import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code_library'))

from pretest import normality_decision, check_homogeneity, check_vif

def precheck(filepath, columns, group_col=None):
    """一键前置检验"""
    print(f'═══ 数据前置检验 ═══\n')
    
    # 读取数据
    df = pd.read_excel(filepath)
    df.columns = df.columns.str.strip()
    print(f'文件: {filepath}')
    print(f'Shape: {df.shape}')
    print(f'检验变量: {columns}\n')
    
    # 1. 正态性检验
    print('─── 1. 正态性检验 ───')
    norm_results = normality_decision(df, columns)
    for col, res in norm_results.items():
        status = '✅ 正态' if res.get('normal') else '❌ 非正态'
        recommend = res.get('recommend', 'unknown')
        print(f'  {col}: {status} → 推荐 {recommend}')
    
    # 2. 方差齐性检验（如果有分组变量）
    if group_col and group_col in df.columns:
        print(f'\n─── 2. 方差齐性检验 (分组: {group_col}) ───')
        for col in columns:
            if col == group_col:
                continue
            try:
                result = check_homogeneity(df, group_col, col)
                status = '✅ 方差齐' if result.get('homogeneous') else '❌ 方差不齐'
                p = result.get('p_value', 'N/A')
                print(f'  {col}: {status} (Levene P={p:.4f})')
            except Exception as e:
                print(f'  {col}: ⚠️ 检验失败 ({e})')
    
    # 3. VIF（如果变量数>=2）
    if len(columns) >= 2:
        print(f'\n─── 3. 多重共线性 (VIF) ───')
        try:
            numeric_cols = [c for c in columns if df[c].dtype in ['float64', 'int64', 'float32', 'int32']]
            if len(numeric_cols) >= 2:
                vif_df = check_vif(df, numeric_cols)
                for _, row in vif_df.iterrows():
                    status = '❌ 共线性!' if row['VIF'] > 10 else ('⚠️ 关注' if row['VIF'] > 5 else '✅ OK')
                    print(f'  {row["Variable"]}: VIF={row["VIF"]:.2f} {status}')
            else:
                print('  跳过（数值型变量不足2个）')
        except Exception as e:
            print(f'  ⚠️ VIF计算失败: {e}')
    
    print(f'\n═══ 前置检验完成 ═══')

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('用法: python scripts/precheck.py "数据.xlsx" "col1,col2,col3" [group_col]')
        sys.exit(1)
    
    filepath = sys.argv[1]
    columns = [c.strip() for c in sys.argv[2].split(',')]
    group_col = sys.argv[3] if len(sys.argv) > 3 else None
    
    precheck(filepath, columns, group_col)
