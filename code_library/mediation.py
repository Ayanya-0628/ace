# -*- coding: utf-8 -*-
"""
ace 代码库: mediation.py
用途：中介效应 + 调节效应 + Bootstrap 方法
日期：2026-03-19 (v2.1 重构，修正文件名与内容不匹配的问题)

使用方式:
    from mediation import sobel_test, bootstrap_mediation, moderation_test
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm


# ══════ Sobel 检验 ══════

def sobel_test(a, b, se_a, se_b):
    """Sobel 检验
    
    Args:
        a: X→M 路径系数
        b: M→Y 路径系数（控制X）
        se_a: a 的标准误
        se_b: b 的标准误
    
    Returns:
        dict: {'z': float, 'p': float, 'ab': float}
    """
    ab = a * b
    se_ab = np.sqrt(a**2 * se_b**2 + b**2 * se_a**2)
    z = ab / se_ab if se_ab > 0 else 0
    p = 2 * (1 - __import__('scipy').stats.norm.cdf(abs(z)))
    return {'z': round(z, 3), 'p': round(p, 4), 'ab': round(ab, 4)}


# ══════ Baron & Kenny 中介检验 ══════

def baron_kenny_mediation(df, x, m, y, covariates=None):
    """Baron & Kenny 因果步骤法
    
    Args:
        df: DataFrame
        x: 自变量列名
        m: 中介变量列名
        y: 因变量列名
        covariates: 控制变量列名列表
    
    Returns:
        dict: {
            'c': float,   # 总效应 X→Y
            'a': float,   # X→M
            'b': float,   # M→Y|X
            'c_prime': float,  # 直接效应 X→Y|M
            'ab': float,  # 间接效应
            'sobel': dict,
            'type': str,  # 'full'/'partial'/'none'
        }
    """
    controls = covariates or []
    
    # Step 1: c 路径 (X→Y)
    X1 = sm.add_constant(df[[x] + controls])
    model_c = sm.OLS(df[y], X1).fit()
    c = model_c.params[x]
    
    # Step 2: a 路径 (X→M)
    model_a = sm.OLS(df[m], X1).fit()
    a = model_a.params[x]
    se_a = model_a.bse[x]
    
    # Step 3: b 路径 + c' (X+M→Y)
    X3 = sm.add_constant(df[[x, m] + controls])
    model_b = sm.OLS(df[y], X3).fit()
    b = model_b.params[m]
    se_b = model_b.bse[m]
    c_prime = model_b.params[x]
    
    # 间接效应 + Sobel
    ab = a * b
    sobel = sobel_test(a, b, se_a, se_b)
    
    # 判断类型
    if sobel['p'] < 0.05:
        if model_b.pvalues[x] > 0.05:
            med_type = 'full'  # 完全中介
        else:
            med_type = 'partial'  # 部分中介
    else:
        med_type = 'none'
    
    return {
        'c': round(c, 4), 'c_p': round(model_c.pvalues[x], 4),
        'a': round(a, 4), 'a_p': round(model_a.pvalues[x], 4),
        'b': round(b, 4), 'b_p': round(model_b.pvalues[m], 4),
        'c_prime': round(c_prime, 4), 'c_prime_p': round(model_b.pvalues[x], 4),
        'ab': round(ab, 4),
        'sobel': sobel,
        'type': med_type,
        'mediation_ratio': round(ab / c * 100, 1) if c != 0 else 0,
    }


# ══════ Bootstrap 中介检验 ══════

def bootstrap_mediation(df, x, m, y, covariates=None, n_boot=5000, ci=95):
    """Bootstrap 中介效应检验
    
    Returns:
        dict: {'ab_mean': float, 'ci_lower': float, 'ci_upper': float,
               'significant': bool, 'ab_samples': array}
    """
    controls = covariates or []
    n = len(df)
    ab_samples = np.zeros(n_boot)
    
    for i in range(n_boot):
        sample = df.sample(n=n, replace=True)
        X1 = sm.add_constant(sample[[x] + controls])
        
        try:
            model_a = sm.OLS(sample[m], X1).fit()
            X3 = sm.add_constant(sample[[x, m] + controls])
            model_b = sm.OLS(sample[y], X3).fit()
            ab_samples[i] = model_a.params[x] * model_b.params[m]
        except Exception:
            ab_samples[i] = np.nan
    
    ab_samples = ab_samples[~np.isnan(ab_samples)]
    alpha = (100 - ci) / 2
    ci_lower = np.percentile(ab_samples, alpha)
    ci_upper = np.percentile(ab_samples, 100 - alpha)
    
    return {
        'ab_mean': round(np.mean(ab_samples), 4),
        'ci_lower': round(ci_lower, 4),
        'ci_upper': round(ci_upper, 4),
        'significant': ci_lower * ci_upper > 0,  # CI 不含 0
        'n_boot': len(ab_samples),
    }


# ══════ 调节效应 ══════

def moderation_test(df, x, w, y, center=True, covariates=None):
    """调节效应检验（交互项法）
    
    Args:
        df: DataFrame
        x: 自变量
        w: 调节变量
        y: 因变量
        center: 是否中心化（推荐True，减少共线性）
    
    Returns:
        dict: {'interaction_coef': float, 'interaction_p': float,
               'model_summary': str, 'significant': bool}
    """
    controls = covariates or []
    data = df.copy()
    
    if center:
        data[f'{x}_c'] = data[x] - data[x].mean()
        data[f'{w}_c'] = data[w] - data[w].mean()
        x_var, w_var = f'{x}_c', f'{w}_c'
    else:
        x_var, w_var = x, w
    
    data['X_W'] = data[x_var] * data[w_var]
    
    X = sm.add_constant(data[[x_var, w_var, 'X_W'] + controls])
    model = sm.OLS(data[y], X).fit()
    
    return {
        'interaction_coef': round(model.params['X_W'], 4),
        'interaction_p': round(model.pvalues['X_W'], 4),
        'significant': model.pvalues['X_W'] < 0.05,
        'r_squared': round(model.rsquared, 4),
        'r_squared_change': round(
            model.rsquared - sm.OLS(
                data[y],
                sm.add_constant(data[[x_var, w_var] + controls])
            ).fit().rsquared, 4),
    }
