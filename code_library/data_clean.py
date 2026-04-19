# -*- coding: utf-8 -*-
"""
ace 代码库: data_clean.py
用途：数据清洗标准化函数，每个问卷/分析项目都要用到的基础操作
日期：2026-03-19 (v2.0 新增)
"""
import pandas as pd
import numpy as np


# ══════ 反向计分 ══════

def reverse_score(df, columns, max_score=5):
    """对指定列进行反向计分
    
    Args:
        df: DataFrame
        columns: 需要反向计分的列名列表
        max_score: Likert 量表最大值（默认5分制）
    
    Returns:
        df: 反向计分后的 DataFrame（原地修改）
    
    示例:
        reverse_score(df, ['Q4', 'Q8'], max_score=5)
    """
    for col in columns:
        if col in df.columns:
            df[col] = max_score + 1 - df[col]
    return df


# ══════ 缺失值处理 ══════

def handle_missing(df, strategy='drop', fill_cols=None, fill_value=None):
    """处理缺失值
    
    Args:
        df: DataFrame
        strategy: 'drop'(删除) / 'mean'(均值填充) / 'median'(中位数填充) / 'value'(指定值)
        fill_cols: 需要填充的列（None=全部）
        fill_value: strategy='value' 时的填充值
    
    Returns:
        df: 处理后的 DataFrame
    """
    if strategy == 'drop':
        return df.dropna().reset_index(drop=True)
    
    cols = fill_cols or df.columns
    if strategy == 'mean':
        df[cols] = df[cols].fillna(df[cols].mean())
    elif strategy == 'median':
        df[cols] = df[cols].fillna(df[cols].median())
    elif strategy == 'value':
        df[cols] = df[cols].fillna(fill_value)
    
    return df


# ══════ 编码校验 ══════

def check_encoding(df, col, expected_map):
    """检查分类变量编码是否与预期一致
    
    Args:
        df: DataFrame
        col: 列名
        expected_map: 期望的编码映射，如 {1: '男', 2: '女'}
    
    Returns:
        bool: 编码是否一致
    
    示例:
        check_encoding(df, '性别', {1: '男', 2: '女'})
    """
    actual_values = set(df[col].dropna().unique())
    expected_values = set(expected_map.keys())
    
    if actual_values != expected_values:
        print(f'⚠️ 列 [{col}] 编码不匹配！')
        print(f'   期望值: {expected_values}')
        print(f'   实际值: {actual_values}')
        print(f'   实际分布:\n{df[col].value_counts().sort_index()}')
        return False
    
    print(f'✅ 列 [{col}] 编码匹配: {expected_map}')
    return True


# ══════ 维度均值得分计算 ══════

def calc_dimension_scores(df, dimension_map):
    """按维度计算均值得分
    
    Args:
        df: DataFrame（已完成反向计分）
        dimension_map: 维度-题项映射，如 {'教学效果': ['Q1','Q2','Q3'], '学习动机': ['Q4','Q5']}
    
    Returns:
        df: 新增维度均值列的 DataFrame
    
    示例:
        dim_map = {
            '教学效果': ['Q1', 'Q2', 'Q3', 'Q4'],
            '学习动机': ['Q5', 'Q6', 'Q7'],
            '自主学习': ['Q8', 'Q9', 'Q10'],
        }
        df = calc_dimension_scores(df, dim_map)
    """
    for dim_name, items in dimension_map.items():
        valid_items = [c for c in items if c in df.columns]
        if not valid_items:
            print(f'⚠️ 维度 [{dim_name}] 无有效题项！')
            continue
        df[dim_name] = df[valid_items].mean(axis=1)
    
    return df


# ══════ 数据概览 ══════

def data_overview(df, id_cols=None):
    """打印数据概览信息
    
    Args:
        df: DataFrame
        id_cols: ID列名列表（不参与统计的列）
    """
    print(f'样本量: N = {len(df)}')
    print(f'变量数: {df.shape[1]}')
    print(f'缺失值统计:')
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if len(missing) == 0:
        print('  无缺失值')
    else:
        for col, cnt in missing.items():
            print(f'  {col}: {cnt} ({cnt/len(df)*100:.1f}%)')
    
    # 数值型变量范围检查
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if id_cols:
        numeric_cols = [c for c in numeric_cols if c not in id_cols]
    
    print(f'\n数值变量范围:')
    for col in numeric_cols:
        print(f'  {col}: [{df[col].min()}, {df[col].max()}], '
              f'mean={df[col].mean():.2f}, std={df[col].std():.2f}')
