# -*- coding: utf-8 -*-
"""
ace 代码库: regression.py
用途：回归分析函数（OLS / 分层回归 / Logistic / 分组回归）
日期：2026-03-19 (v2.1 重构，移除重复的中介和信度代码)

使用方式:
    from regression import ols_regression, hierarchical_regression, logistic_regression
    
注意：
    - 中介效应已移至 mediation.py
    - 信度 cronbachs_alpha 已移至 survey.py
"""
import pandas as pd
import numpy as np
import statsmodels.api as sm


# ══════ OLS 回归 ══════

def ols_regression(df, y_var, x_vars, control_vars=None, robust_se='HC1'):
    """OLS 回归分析
    
    Args:
        df: DataFrame
        y_var: 因变量列名
        x_vars: 自变量列名列表
        control_vars: 控制变量列名列表
        robust_se: 稳健标准误类型 ('HC0'~'HC3') 或 None
    
    Returns:
        dict: {'model': OLSResults, 'coefficients': DataFrame,
               'r_squared': float, 'adj_r_squared': float,
               'f_stat': float, 'f_p': float}
    """
    controls = control_vars or []
    all_vars = list(x_vars) + controls
    data = df[[y_var] + all_vars].dropna()
    
    X = sm.add_constant(data[all_vars])
    model = sm.OLS(data[y_var], X).fit(
        cov_type=robust_se if robust_se else 'nonrobust')
    
    coef_df = pd.DataFrame({
        '变量': model.params.index,
        '系数': model.params.round(4).values,
        '标准误': model.bse.round(4).values,
        't': model.tvalues.round(3).values,
        'P': model.pvalues.round(4).values,
    })
    coef_df = coef_df[coef_df['变量'] != 'const']
    
    return {
        'model': model,
        'coefficients': coef_df,
        'r_squared': round(model.rsquared, 4),
        'adj_r_squared': round(model.rsquared_adj, 4),
        'f_stat': round(model.fvalue, 3),
        'f_p': round(model.f_pvalue, 4),
        'n': int(model.nobs),
    }


# ══════ 分层回归 ══════

def hierarchical_regression(df, y_var, model_specs):
    """分层回归（逐步添加变量块）
    
    Args:
        model_specs: [
            {'name': '模型1', 'vars': ['age', 'gender']},
            {'name': '模型2', 'vars': ['age', 'gender', 'education']},
            {'name': '模型3', 'vars': ['age', 'gender', 'education', 'X*W']},
        ]
    
    Returns:
        list[dict]: 每个模型的 {name, r2, adj_r2, delta_r2, f, f_p, coef_df}
    """
    results = []
    prev_r2 = 0
    
    for spec in model_specs:
        data = df[[y_var] + spec['vars']].dropna()
        X = sm.add_constant(data[spec['vars']])
        model = sm.OLS(data[y_var], X).fit()
        
        r2 = round(model.rsquared, 4)
        delta_r2 = round(r2 - prev_r2, 4)
        
        coef_df = pd.DataFrame({
            '变量': model.params.index,
            '系数': model.params.round(4).values,
            '标准误': model.bse.round(4).values,
            't': model.tvalues.round(3).values,
            'P': model.pvalues.round(4).values,
        })
        
        results.append({
            'name': spec['name'],
            'r_squared': r2,
            'adj_r_squared': round(model.rsquared_adj, 4),
            'delta_r_squared': delta_r2,
            'f_stat': round(model.fvalue, 3),
            'f_p': round(model.f_pvalue, 4),
            'coefficients': coef_df,
            'n': int(model.nobs),
        })
        prev_r2 = r2
    
    return results


# ══════ Logistic 回归 ══════

def logistic_regression(df, y_var, x_vars, control_vars=None):
    """二元 Logistic 回归
    
    Returns:
        dict: {'model': LogitResults, 'or_table': DataFrame(OR/CI/P),
               'pseudo_r2': float}
    """
    controls = control_vars or []
    all_vars = list(x_vars) + controls
    data = df[[y_var] + all_vars].dropna()
    
    X = sm.add_constant(data[all_vars])
    model = sm.Logit(data[y_var], X).fit(disp=0)
    
    or_vals = np.exp(model.params)
    ci_vals = np.exp(model.conf_int())
    
    or_table = pd.DataFrame({
        '变量': model.params.index,
        'OR': or_vals.round(3).values,
        'CI下限': ci_vals[0].round(3).values,
        'CI上限': ci_vals[1].round(3).values,
        'P': model.pvalues.round(4).values,
    })
    or_table = or_table[or_table['变量'] != 'const']
    
    return {
        'model': model,
        'or_table': or_table,
        'pseudo_r2': round(model.prsquared, 4),
        'n': int(model.nobs),
    }


# ══════ 分组回归（异质性分析） ══════

def subgroup_regression(df, y_var, x_vars, group_col, control_vars=None):
    """分组回归（异质性分析）
    
    Returns:
        dict: {group_name: ols_result, ...}
    """
    controls = control_vars or []
    results = {}
    
    for group_name, sub_df in df.groupby(group_col):
        result = ols_regression(sub_df, y_var, x_vars, controls)
        results[group_name] = result
    
    return results
