# -*- coding: utf-8 -*-
"""
ace 代码库: anova.py
用途：方差分析函数（单因素/双因素ANOVA + 事后比较 + 非参数替代）
日期：2026-03-19 (v2.1 重构为可 import 函数)

使用方式:
    from anova import oneway_anova, kruskal_test
"""
import pandas as pd
import numpy as np
from scipy import stats


# ══════ 单因素方差分析 ══════

def oneway_anova(df, group_col, value_col, posthoc='tukey'):
    """单因素方差分析 + 事后比较
    
    Args:
        df: DataFrame
        group_col: 分组变量列名
        value_col: 因变量列名
        posthoc: 'tukey' / 'lsd' / None
    
    Returns:
        dict: {
            'F': float, 'p': float,
            'groups': {name: {'mean': m, 'std': s, 'n': n}},
            'posthoc': DataFrame or None,
            'eta_squared': float,  # 效应量
        }
    """
    groups = df.groupby(group_col)[value_col]
    group_data = [g.dropna().values for _, g in groups]
    group_names = [name for name, _ in groups]
    
    F, p = stats.f_oneway(*group_data)
    
    # 效应量 eta^2
    grand_mean = df[value_col].mean()
    ss_between = sum(len(g) * (g.mean() - grand_mean)**2 for g in group_data)
    ss_total = sum((df[value_col] - grand_mean)**2)
    eta_sq = ss_between / ss_total if ss_total > 0 else 0
    
    # 各组描述统计
    group_stats = {}
    for name, g in groups:
        vals = g.dropna()
        group_stats[name] = {
            'mean': round(vals.mean(), 3),
            'std': round(vals.std(), 3),
            'n': len(vals),
        }
    
    # 事后比较
    posthoc_result = None
    if posthoc == 'tukey' and p < 0.05:
        from statsmodels.stats.multicomp import pairwise_tukeyhsd
        result = pairwise_tukeyhsd(df[value_col].dropna(),
                                    df[group_col].dropna())
        posthoc_result = pd.DataFrame(data=result._results_table.data[1:],
                                       columns=result._results_table.data[0])
    
    return {
        'F': round(F, 3), 'p': round(p, 4),
        'groups': group_stats,
        'posthoc': posthoc_result,
        'eta_squared': round(eta_sq, 4),
    }


# ══════ Kruskal-Wallis 非参数替代 ══════

def kruskal_test(df, group_col, value_col):
    """Kruskal-Wallis H 检验（非参数，3+组）
    
    Returns:
        dict: {'H': float, 'p': float, 'groups': {name: {'median': m, 'iqr': str, 'n': n}}}
    """
    groups = df.groupby(group_col)[value_col]
    group_data = [g.dropna().values for _, g in groups]
    
    H, p = stats.kruskal(*group_data)
    
    group_stats = {}
    for name, g in groups:
        vals = g.dropna()
        q25, q75 = vals.quantile(0.25), vals.quantile(0.75)
        group_stats[name] = {
            'median': round(vals.median(), 3),
            'iqr': f'{q25:.2f}-{q75:.2f}',
            'n': len(vals),
        }
    
    return {'H': round(H, 3), 'p': round(p, 4), 'groups': group_stats}
