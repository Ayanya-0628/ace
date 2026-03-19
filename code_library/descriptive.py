# -*- coding: utf-8 -*-
"""
ace 代码库: descriptive.py
用途：描述性统计 + 频数分析 + 交叉表 + 人口学特征表生成
日期：2026-03-19 (v2.1 重构为可 import 函数)

使用方式:
    from descriptive import demographic_table, descriptive_stats, chi_square_test
"""
import pandas as pd
import numpy as np
from scipy import stats


# ══════ 描述性统计 ══════

def descriptive_stats(df, cols, format='parametric'):
    """批量描述性统计
    
    Args:
        df: DataFrame
        cols: 变量列名列表
        format: 'parametric'(均值+SD) / 'nonparametric'(中位数+IQR)
    
    Returns:
        DataFrame: 各变量的描述统计
    """
    results = []
    for col in cols:
        vals = df[col].dropna()
        if format == 'nonparametric':
            q25, q75 = vals.quantile(0.25), vals.quantile(0.75)
            results.append({
                '变量': col,
                '中位数': round(vals.median(), 3),
                'P25': round(q25, 3),
                'P75': round(q75, 3),
                'IQR': f'{q25:.2f}-{q75:.2f}',
                'N': len(vals),
            })
        else:
            results.append({
                '变量': col,
                '均值': round(vals.mean(), 3),
                '标准差': round(vals.std(), 3),
                '最小值': round(vals.min(), 3),
                '最大值': round(vals.max(), 3),
                'N': len(vals),
            })
    return pd.DataFrame(results)


# ══════ 人口学频数表 ══════

def demographic_table(df, vars_config):
    """自动生成人口学特征频数表
    
    Args:
        vars_config: 变量配置列表，每个元素为:
            {'col': '性别', 'label': '性别', 'type': 'categorical',
             'mapping': {1: '男', 2: '女'}}
            或
            {'col': '年龄', 'label': '年龄(岁)', 'type': 'continuous'}
    
    Returns:
        list: [{'特征': str, '类别': str, 'n': int, '%': float}, ...]
    """
    rows = []
    for var in vars_config:
        col = var['col']
        label = var.get('label', col)
        
        if var['type'] == 'categorical':
            mapping = var.get('mapping', {})
            total = df[col].notna().sum()
            for val, name in mapping.items():
                n = (df[col] == val).sum()
                pct = round(n / total * 100, 1) if total > 0 else 0
                rows.append({
                    '特征': label, '类别': name,
                    'n': n, '%': pct,
                    '格式': f'{n}({pct}%)',
                })
        elif var['type'] == 'continuous':
            vals = df[col].dropna()
            rows.append({
                '特征': label, '类别': '',
                'n': len(vals), '%': 0,
                '格式': f'{vals.mean():.2f}±{vals.std():.2f}',
            })
    
    return rows


# ══════ 卡方检验 ══════

def chi_square_test(data, group_var, outcome_var, group_labels=None):
    """卡方检验，返回统计量和各组率
    
    Returns:
        dict: {'chi2': float, 'p': float, 'dof': int,
               'rates': {group: {'n': int, 'positive': int, 'rate': float}}}
    """
    ct = pd.crosstab(data[group_var], data[outcome_var])
    chi2, p, dof, expected = stats.chi2_contingency(ct)
    
    # 检查是否需要Fisher精确检验
    use_fisher = (expected < 5).any()
    
    rates = {}
    for grp in sorted(data[group_var].unique()):
        mask = data[group_var] == grp
        total = int(mask.sum())
        positive = int(data.loc[mask, outcome_var].sum())
        label = group_labels.get(grp, str(grp)) if group_labels else str(grp)
        rates[label] = {
            'n': total, 'positive': positive,
            'rate': round(positive / total * 100, 1) if total > 0 else 0,
        }
    
    result = {'chi2': round(chi2, 3), 'p': round(p, 4),
              'dof': dof, 'rates': rates}
    
    if use_fisher and ct.shape == (2, 2):
        odds, p_fisher = stats.fisher_exact(ct)
        result['fisher_p'] = round(p_fisher, 4)
        result['note'] = '期望频数<5，建议使用Fisher精确检验'
    
    return result


# ══════ Cramér's V 效应量 ══════

def cramers_v(contingency_table):
    """Cramér's V 效应量  |V|: 0.1小, 0.3中, 0.5大"""
    chi2 = stats.chi2_contingency(contingency_table)[0]
    n = contingency_table.sum().sum()
    k = min(contingency_table.shape) - 1
    return round(np.sqrt(chi2 / (n * k)), 3) if n * k > 0 else 0
