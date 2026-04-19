# -*- coding: utf-8 -*-
"""
ace 代码库: pretest.py
用途：前置检验函数（正态性、方差齐性、多重共线性、正态性批量检验）
日期：2026-03-19 (v2.0 重构为可 import 函数)

使用方式:
    from pretest import check_normality, check_homogeneity, check_vif
    from pretest import normality_decision
"""
import pandas as pd
import numpy as np
from scipy import stats


# ══════ 正态性检验 ══════

def check_normality(data, method='shapiro', alpha=0.05):
    """正态性检验
    
    Args:
        data: 一维数组或 Series
        method: 'shapiro'(n<5000) / 'ks'(大样本)
        alpha: 显著性水平
    
    Returns:
        dict: {'statistic': float, 'p_value': float, 'is_normal': bool}
    """
    data = pd.Series(data).dropna()
    
    if method == 'shapiro':
        stat, p = stats.shapiro(data)
    elif method == 'ks':
        stat, p = stats.kstest(data, 'norm', args=(data.mean(), data.std()))
    else:
        raise ValueError(f'未知方法: {method}')
    
    return {
        'statistic': round(stat, 4),
        'p_value': round(p, 4),
        'is_normal': p > alpha,
        'method': method,
    }


def normality_decision(df, columns, alpha=0.05):
    """批量正态性检验，决定使用参数/非参数路线
    
    Args:
        df: DataFrame
        columns: 需要检验的列名列表
        alpha: 显著性水平
    
    Returns:
        dict: {
            'results': {col: check_result},
            'all_normal': bool,  # 全部正态则True
            'recommendation': str,  # 'parametric' 或 'nonparametric'
        }
    
    示例:
        decision = normality_decision(df, ['教学效果', '学习动机', '自主学习'])
        if decision['recommendation'] == 'nonparametric':
            # 切换到非参数检验路线
    """
    results = {}
    for col in columns:
        if col in df.columns:
            data = df[col].dropna()
            n = len(data)
            method = 'shapiro' if n < 5000 else 'ks'
            results[col] = check_normality(data, method=method, alpha=alpha)
    
    all_normal = all(r['is_normal'] for r in results.values())
    recommendation = 'parametric' if all_normal else 'nonparametric'
    
    # 打印结果
    print(f'正态性检验结果 (alpha={alpha}):')
    for col, r in results.items():
        status = '正态' if r['is_normal'] else '非正态'
        print(f'  {col}: {r["method"]} stat={r["statistic"]}, '
              f'p={r["p_value"]} -> {status}')
    print(f'建议路线: {recommendation}')
    
    return {
        'results': results,
        'all_normal': all_normal,
        'recommendation': recommendation,
    }


# ══════ 方差齐性检验 ══════

def check_homogeneity(*groups, method='levene'):
    """方差齐性检验
    
    Args:
        *groups: 各组数据（多个数组）
        method: 'levene'(稳健) / 'bartlett'(严格正态)
    
    Returns:
        dict: {'statistic': float, 'p_value': float, 'is_homogeneous': bool}
    """
    if method == 'levene':
        stat, p = stats.levene(*groups)
    elif method == 'bartlett':
        stat, p = stats.bartlett(*groups)
    else:
        raise ValueError(f'未知方法: {method}')
    
    return {
        'statistic': round(stat, 4),
        'p_value': round(p, 4),
        'is_homogeneous': p > 0.05,
        'method': method,
    }


# ══════ 多重共线性诊断 ══════

def check_vif(X):
    """VIF 多重共线性检验
    
    Args:
        X: DataFrame，自变量矩阵（不含常数项，函数内部会添加）
    
    Returns:
        DataFrame: 各变量的 VIF 值
        VIF>10 严重共线性，VIF>5 需要关注
    """
    from statsmodels.stats.outliers_influence import variance_inflation_factor
    import statsmodels.api as sm
    
    X_const = sm.add_constant(X)
    vif_data = pd.DataFrame({
        'Variable': X.columns,
        'VIF': [variance_inflation_factor(X_const.values, i + 1)
                for i in range(X.shape[1])]
    })
    vif_data = vif_data.sort_values('VIF', ascending=False)
    
    # 标记警告
    for _, row in vif_data.iterrows():
        if row['VIF'] > 10:
            print(f'  ⚠️ {row["Variable"]}: VIF={row["VIF"]:.2f} > 10 严重共线性！')
        elif row['VIF'] > 5:
            print(f'  ⚠ {row["Variable"]}: VIF={row["VIF"]:.2f} > 5 需关注')
    
    return vif_data
