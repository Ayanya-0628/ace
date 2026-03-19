# -*- coding: utf-8 -*-
"""
ace 代码库: survey.py
用途：问卷分析函数（信度/KMO/EFA/CFA/AVE/CR）
日期：2026-03-19 (v2.1 重构，去重 cronbachs_alpha)

使用方式:
    from survey import cronbachs_alpha, kmo_bartlett, efa, calc_ave, calc_cr
"""
import pandas as pd
import numpy as np
from scipy import stats


# ══════ 信度检验 ══════

def cronbachs_alpha(df_items):
    """Cronbach's alpha 信度系数
    >=0.9 优秀, >=0.8 良好, >=0.7 可接受, <0.7 需修改
    """
    k = df_items.shape[1]
    if k < 2:
        return 0.0
    item_vars = df_items.var(axis=0, ddof=1)
    total_var = df_items.sum(axis=1).var(ddof=1)
    if total_var == 0:
        return 0.0
    return round((k / (k - 1)) * (1 - item_vars.sum() / total_var), 4)


# ══════ KMO & Bartlett ══════

def kmo_bartlett(df):
    """KMO 和 Bartlett 球形检验
    
    Returns:
        dict: {'kmo': float, 'bartlett_chi2': float, 'bartlett_p': float,
               'suitable': bool}
        KMO>0.6 且 Bartlett p<0.05 适合因子分析
    """
    try:
        from factor_analyzer.factor_analyzer import (
            calculate_kmo, calculate_bartlett_sphericity)
        kmo_all, kmo_model = calculate_kmo(df)
        chi2, p = calculate_bartlett_sphericity(df)
    except ImportError:
        # factor_analyzer 不可用时手动计算 Bartlett
        n = len(df)
        corr = df.corr()
        p_val = len(corr)
        det = np.linalg.det(corr)
        chi2 = -(n - 1 - (2 * p_val + 5) / 6) * np.log(det) if det > 0 else 999
        dof = p_val * (p_val - 1) / 2
        p = 1 - stats.chi2.cdf(chi2, dof)
        kmo_model = 0  # 无法计算 KMO
    
    return {
        'kmo': round(float(kmo_model), 4),
        'bartlett_chi2': round(float(chi2), 2),
        'bartlett_p': round(float(p), 4),
        'suitable': float(kmo_model) > 0.6 and float(p) < 0.05,
    }


# ══════ 探索性因子分析 EFA ══════

def efa(df, n_factors, rotation='varimax'):
    """探索性因子分析
    
    Returns:
        dict: {'loadings': DataFrame, 'variance': tuple, 'communalities': array}
    """
    try:
        from factor_analyzer import FactorAnalyzer
        fa = FactorAnalyzer(n_factors=n_factors, rotation=rotation)
        fa.fit(df)
        loadings = pd.DataFrame(
            fa.loadings_, index=df.columns,
            columns=[f'F{i+1}' for i in range(n_factors)])
        return {
            'loadings': loadings,
            'variance': fa.get_factor_variance(),
            'communalities': fa.get_communalities(),
        }
    except Exception as e:
        # factor_analyzer 不兼容时的降级方案
        print(f'factor_analyzer 出错: {e}')
        print('降级方案: 使用 numpy 手动实现 PCA 旋转')
        corr = df.corr()
        eigenvalues, eigenvectors = np.linalg.eigh(corr)
        # 取前 n_factors 个
        idx = np.argsort(eigenvalues)[::-1][:n_factors]
        loadings_raw = eigenvectors[:, idx] * np.sqrt(eigenvalues[idx])
        loadings = pd.DataFrame(
            loadings_raw, index=df.columns,
            columns=[f'F{i+1}' for i in range(n_factors)])
        return {'loadings': loadings, 'variance': None, 'communalities': None}


# ══════ AVE 和 CR ══════

def calc_ave(loadings):
    """平均方差提取量 AVE (>0.5 合格)"""
    return round(float(np.mean(np.array(loadings) ** 2)), 4)


def calc_cr(loadings):
    """组合信度 CR (>0.7 合格)"""
    loadings = np.array(loadings)
    sum_l = np.sum(loadings)
    sum_e = np.sum(1 - loadings ** 2)
    cr = sum_l ** 2 / (sum_l ** 2 + sum_e)
    return round(float(cr), 4)


# ══════ ROC 曲线 ══════

def roc_analysis(y_true, y_score):
    """ROC 曲线分析
    
    Returns:
        dict: {'auc': float, 'optimal_threshold': float,
               'sensitivity': float, 'specificity': float,
               'fpr': array, 'tpr': array}
    """
    from sklearn.metrics import roc_curve, auc
    fpr, tpr, thresholds = roc_curve(y_true, y_score)
    roc_auc = auc(fpr, tpr)
    
    # 最佳截断点 Youden Index
    youden = tpr - fpr
    optimal_idx = np.argmax(youden)
    
    return {
        'auc': round(roc_auc, 4),
        'optimal_threshold': round(thresholds[optimal_idx], 4),
        'sensitivity': round(tpr[optimal_idx], 4),
        'specificity': round(1 - fpr[optimal_idx], 4),
        'fpr': fpr, 'tpr': tpr,
    }
