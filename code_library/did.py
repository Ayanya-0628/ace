# -*- coding: utf-8 -*-
"""
ace 代码库: did.py
用途：DID双重差分 + 工具变量2SLS + 面板数据分析
日期：2026-04-04 (v2.0 重写为可import函数)

使用方式:
    from did import did_estimate, iv_2sls
"""
import pandas as pd
import numpy as np
from scipy import stats


# ══════ DID 双重差分估计 ══════

def did_estimate(df, y_col, treat_col, post_col, controls=None):
    """DID双重差分回归估计
    
    Y = β0 + β1*Treat + β2*Post + β3*Treat×Post + γ*Controls + ε
    β3 即 DID 估计量
    
    Args:
        df: DataFrame
        y_col: 因变量列名
        treat_col: 处理组虚拟变量列名 (0/1)
        post_col: 政策后虚拟变量列名 (0/1)
        controls: 控制变量列名列表 (可选)
    
    Returns:
        dict: {'did_coef': float, 'did_se': float, 'did_p': float,
               'model': OLS result object}
    """
    import statsmodels.api as sm
    
    data = df.copy()
    data['Treat_Post'] = data[treat_col] * data[post_col]
    
    x_cols = [treat_col, post_col, 'Treat_Post']
    if controls:
        x_cols += controls
    
    X = sm.add_constant(data[x_cols].astype(float))
    y = data[y_col].astype(float)
    
    # 去缺失
    mask = X.notna().all(axis=1) & y.notna()
    X, y = X[mask], y[mask]
    
    model = sm.OLS(y, X).fit(cov_type='HC1')  # 异方差稳健标准误
    
    return {
        'did_coef': round(model.params['Treat_Post'], 4),
        'did_se': round(model.bse['Treat_Post'], 4),
        'did_p': round(model.pvalues['Treat_Post'], 4),
        'did_t': round(model.tvalues['Treat_Post'], 4),
        'sig': '**' if model.pvalues['Treat_Post'] < 0.01 
               else ('*' if model.pvalues['Treat_Post'] < 0.05 else 'ns'),
        'r_squared': round(model.rsquared, 4),
        'n': int(model.nobs),
        'model': model,
    }


# ══════ 平行趋势检验 ══════

def parallel_trend_test(df, y_col, treat_col, time_col, ref_period,
                        controls=None):
    """平行趋势检验（事件研究法）
    
    对每个时间点生成交互项 Treat × D_t，ref_period 为参照期（系数为0）
    
    Returns:
        DataFrame: period, coef, se, p, ci_lower, ci_upper
    """
    import statsmodels.api as sm
    
    data = df.copy()
    periods = sorted(data[time_col].unique())
    periods_no_ref = [t for t in periods if t != ref_period]
    
    # 生成各期虚拟变量交互项
    for t in periods_no_ref:
        data[f'Treat_D{t}'] = (data[treat_col] * (data[time_col] == t)).astype(int)
    
    x_cols = [treat_col] + [f'Treat_D{t}' for t in periods_no_ref]
    # 加入时间固定效应
    for t in periods[1:]:
        data[f'D{t}'] = (data[time_col] == t).astype(int)
        x_cols.append(f'D{t}')
    if controls:
        x_cols += controls
    
    X = sm.add_constant(data[x_cols].astype(float))
    y = data[y_col].astype(float)
    mask = X.notna().all(axis=1) & y.notna()
    
    model = sm.OLS(y[mask], X[mask]).fit(cov_type='HC1')
    
    rows = []
    for t in periods:
        if t == ref_period:
            rows.append({'period': t, 'coef': 0, 'se': 0, 'p': 1,
                        'ci_lower': 0, 'ci_upper': 0})
        else:
            key = f'Treat_D{t}'
            coef = model.params[key]
            se = model.bse[key]
            ci = model.conf_int().loc[key]
            rows.append({
                'period': t, 'coef': round(coef, 4),
                'se': round(se, 4), 'p': round(model.pvalues[key], 4),
                'ci_lower': round(ci[0], 4), 'ci_upper': round(ci[1], 4),
            })
    
    return pd.DataFrame(rows)


# ══════ 工具变量 / 2SLS ══════

def iv_2sls(df, y_col, endog_col, instrument_col, exog_cols=None):
    """工具变量两阶段最小二乘法 (2SLS)
    
    第一阶段：X = π0 + π1*Z + γ*Controls + ε
    第二阶段：Y = β0 + β1*X_hat + γ*Controls + ε
    
    Args:
        df: DataFrame
        y_col: 因变量列名
        endog_col: 内生变量列名
        instrument_col: 工具变量列名
        exog_cols: 外生控制变量列名列表 (可选)
    
    Returns:
        dict: {'coef': float, 'se': float, 'p': float,
               'first_stage_F': float, 'model': IV2SLS result}
    """
    try:
        from linearmodels.iv import IV2SLS
    except ImportError:
        raise ImportError("需要安装 linearmodels: pip install linearmodels")
    
    import statsmodels.api as sm
    
    data = df.dropna(subset=[y_col, endog_col, instrument_col])
    if exog_cols:
        data = data.dropna(subset=exog_cols)
    
    dependent = data[y_col]
    endog = data[[endog_col]]
    instruments = data[[instrument_col]]
    
    if exog_cols:
        exog = sm.add_constant(data[exog_cols])
    else:
        exog = sm.add_constant(pd.DataFrame(index=data.index))
    
    model = IV2SLS(dependent, exog, endog, instruments).fit()
    
    # 第一阶段F统计量
    first_stage = sm.OLS(
        data[endog_col],
        sm.add_constant(data[[instrument_col] + (exog_cols or [])])
    ).fit()
    first_F = first_stage.fvalue
    
    return {
        'coef': round(model.params[endog_col], 4),
        'se': round(model.std_errors[endog_col], 4),
        'p': round(model.pvalues[endog_col], 4),
        'first_stage_F': round(first_F, 2),
        'weak_instrument': first_F < 10,
        'n': int(model.nobs),
        'model': model,
    }
