# -*- coding: utf-8 -*-
"""
ace 代码库: ttest.py
用途：t检验全家桶 + 效应量 + 非参数替代
日期：2026-03-19 (v2.1 重构为可 import 函数)

使用方式:
    from ttest import independent_ttest, paired_ttest, mann_whitney_u, cohens_d
"""
import numpy as np
from scipy import stats


# ══════ 独立样本 t 检验 ══════

def independent_ttest(g1, g2, equal_var=None):
    """独立样本 t 检验（自动判断方差齐性）
    
    Args:
        g1, g2: 两组数据
        equal_var: True/False/None(自动用Levene判断)
    
    Returns:
        dict: {'t': float, 'p': float, 'method': str, 'd': float,
               'g1_mean': float, 'g1_std': float, 'g1_n': int,
               'g2_mean': float, 'g2_std': float, 'g2_n': int}
    """
    g1, g2 = np.array(g1, dtype=float), np.array(g2, dtype=float)
    g1, g2 = g1[~np.isnan(g1)], g2[~np.isnan(g2)]
    
    if equal_var is None:
        _, lev_p = stats.levene(g1, g2)
        equal_var = lev_p > 0.05
    
    t, p = stats.ttest_ind(g1, g2, equal_var=equal_var)
    d = cohens_d(g1, g2)
    method = 'Student t' if equal_var else "Welch's t"
    
    return {
        't': round(t, 3), 'p': round(p, 4), 'method': method,
        'd': round(d, 3),
        'g1_mean': round(np.mean(g1), 3), 'g1_std': round(np.std(g1, ddof=1), 3),
        'g1_n': len(g1),
        'g2_mean': round(np.mean(g2), 3), 'g2_std': round(np.std(g2, ddof=1), 3),
        'g2_n': len(g2),
    }


# ══════ 配对样本 t 检验 ══════

def paired_ttest(pre, post):
    """配对样本 t 检验
    
    Returns:
        dict: {'t': float, 'p': float, 'd': float,
               'pre_mean': float, 'post_mean': float, 'diff_mean': float}
    """
    pre, post = np.array(pre, dtype=float), np.array(post, dtype=float)
    mask = ~(np.isnan(pre) | np.isnan(post))
    pre, post = pre[mask], post[mask]
    
    t, p = stats.ttest_rel(pre, post)
    diff = post - pre
    d = np.mean(diff) / np.std(diff, ddof=1) if np.std(diff, ddof=1) > 0 else 0
    
    return {
        't': round(t, 3), 'p': round(p, 4), 'd': round(d, 3),
        'pre_mean': round(np.mean(pre), 3),
        'post_mean': round(np.mean(post), 3),
        'diff_mean': round(np.mean(diff), 3),
        'n': len(pre),
    }


# ══════ Mann-Whitney U 非参数 ══════

def mann_whitney_u(g1, g2):
    """Mann-Whitney U 检验（非参数，2组独立）
    
    Returns:
        dict: {'U': float, 'p': float, 'z': float, 'r': float(效应量),
               'g1_median': float, 'g2_median': float}
    """
    g1, g2 = np.array(g1, dtype=float), np.array(g2, dtype=float)
    g1, g2 = g1[~np.isnan(g1)], g2[~np.isnan(g2)]
    
    U, p = stats.mannwhitneyu(g1, g2, alternative='two-sided')
    n = len(g1) + len(g2)
    z = stats.norm.ppf(1 - p / 2) if p > 0 else 0
    r = z / np.sqrt(n) if n > 0 else 0  # 效应量
    
    return {
        'U': round(U, 1), 'p': round(p, 4),
        'z': round(z, 3), 'r': round(r, 3),
        'g1_median': round(np.median(g1), 3),
        'g2_median': round(np.median(g2), 3),
    }


# ══════ Wilcoxon 符号秩检验 ══════

def wilcoxon_test(pre, post):
    """Wilcoxon 符号秩检验（非参数，配对）"""
    pre, post = np.array(pre, dtype=float), np.array(post, dtype=float)
    mask = ~(np.isnan(pre) | np.isnan(post))
    pre, post = pre[mask], post[mask]
    
    W, p = stats.wilcoxon(pre, post)
    n = len(pre)
    z = stats.norm.ppf(1 - p / 2) if p > 0 else 0
    r = z / np.sqrt(n) if n > 0 else 0
    
    return {
        'W': round(W, 1), 'p': round(p, 4),
        'z': round(z, 3), 'r': round(r, 3),
        'pre_median': round(np.median(pre), 3),
        'post_median': round(np.median(post), 3),
        'n': n,
    }


# ══════ 效应量 ══════

def cohens_d(g1, g2):
    """Cohen's d 效应量  |d|: 0.2小, 0.5中, 0.8大"""
    g1, g2 = np.array(g1, dtype=float), np.array(g2, dtype=float)
    n1, n2 = len(g1), len(g2)
    s1, s2 = np.std(g1, ddof=1), np.std(g2, ddof=1)
    pooled = np.sqrt(((n1 - 1) * s1**2 + (n2 - 1) * s2**2) / (n1 + n2 - 2))
    return (np.mean(g1) - np.mean(g2)) / pooled if pooled > 0 else 0
