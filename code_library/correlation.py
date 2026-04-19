# -*- coding: utf-8 -*-
"""
ace 代码库: correlation.py
用途：相关分析函数（Pearson/Spearman + 带星号矩阵 + 热力图）
日期：2026-03-19 (v2.1 重构，移除重复Word工具)

使用方式:
    from correlation import correlation_test, correlation_matrix_stars
"""
import pandas as pd
import numpy as np
from scipy import stats


# ══════ 相关分析 ══════

def correlation_test(x, y, method='pearson'):
    """单对变量相关分析
    
    Args:
        x, y: 数据序列
        method: 'pearson' / 'spearman'
    
    Returns:
        dict: {'r': float, 'p': float, 'method': str}
        |r|<0.3 弱, 0.3-0.7 中等, >0.7 强
    """
    x, y = pd.Series(x).dropna(), pd.Series(y).dropna()
    # 对齐索引
    common = x.index.intersection(y.index)
    x, y = x[common], y[common]
    
    if method == 'spearman':
        r, p = stats.spearmanr(x, y)
    else:
        r, p = stats.pearsonr(x, y)
    
    return {'r': round(r, 3), 'p': round(p, 4), 'method': method}


def significance_stars(p):
    """P值转显著性星号"""
    if p < 0.001:
        return '***'
    elif p < 0.01:
        return '**'
    elif p < 0.05:
        return '*'
    return ''


def format_pvalue(p):
    """格式化P值用于报告"""
    if p < 0.001:
        return '<0.001'
    elif p < 0.01:
        return f'{p:.3f}'
    else:
        return f'{p:.3f}'


def correlation_matrix_stars(df, cols, method='pearson'):
    """生成带显著性星号的相关矩阵（下三角）
    
    Args:
        df: DataFrame
        cols: 变量列名列表
        method: 'pearson' / 'spearman'
    
    Returns:
        DataFrame: 下三角带星号的字符串矩阵
    
    示例:
        matrix = correlation_matrix_stars(df, ['X1','X2','X3','Y'])
    """
    n = len(cols)
    result = pd.DataFrame('', index=cols, columns=cols)
    
    for i in range(n):
        result.iloc[i, i] = '1'  # 对角线
        for j in range(i):
            x = df[cols[i]].dropna()
            y = df[cols[j]].dropna()
            common = x.index.intersection(y.index)
            
            if method == 'spearman':
                r, p = stats.spearmanr(x[common], y[common])
            else:
                r, p = stats.pearsonr(x[common], y[common])
            
            stars = significance_stars(p)
            result.iloc[i, j] = f'{r:.3f}{stars}'
    
    return result


def mean_sd(series, decimal=2):
    """格式化为 '均值±标准差' 字符串"""
    m = series.mean()
    s = series.std()
    return f'{m:.{decimal}f}±{s:.{decimal}f}'
