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


# ══════ 批量卡方交叉检验（多自变量 × 多因变量） ══════

def batch_chi_square(df, row_vars, col_vars, row_labels=None, col_labels=None):
    """批量卡方检验：多个分类自变量 × 多个分类因变量
    
    适用场景：人口学特征(Q1-Q8) × 满意度/态度变量(Q17-Q21)
    
    Args:
        df: DataFrame
        row_vars: 自变量列名列表（如人口学变量）
        col_vars: 因变量列名列表（如满意度变量）
        row_labels: {列名: 显示名} 映射（可选）
        col_labels: {列名: 显示名} 映射（可选）
    
    Returns:
        dict: {
            'summary': DataFrame (汇总表),
            'crosstabs': {(row, col): DataFrame},
            'tests': {(row, col): dict}
        }
    """
    if row_labels is None:
        row_labels = {v: v for v in row_vars}
    if col_labels is None:
        col_labels = {v: v for v in col_vars}
    
    summary_rows = []
    crosstabs = {}
    tests = {}
    
    for rv in row_vars:
        for cv in col_vars:
            sub = df[[rv, cv]].dropna()
            if len(sub) < 10:
                continue
            
            ct = pd.crosstab(sub[rv], sub[cv])
            # 去掉频数为0的行/列
            ct = ct.loc[(ct.sum(axis=1) > 0), (ct.sum(axis=0) > 0)]
            
            if ct.shape[0] < 2 or ct.shape[1] < 2:
                continue
            
            chi2, p, dof, expected = stats.chi2_contingency(ct)
            low_expected = (expected < 5).sum()
            total_cells = expected.size
            low_pct = low_expected / total_cells * 100
            
            sig = '**' if p < 0.01 else ('*' if p < 0.05 else 'ns')
            
            # Fisher精确检验（仅2×2表）
            fisher_p = None
            if ct.shape == (2, 2):
                try:
                    _, fisher_p = stats.fisher_exact(ct)
                except:
                    pass
            
            # 交叉表（带合计）
            ct_full = pd.crosstab(sub[rv], sub[cv], margins=True, margins_name='合计')
            crosstabs[(rv, cv)] = ct_full
            
            test_result = {
                'chi2': round(chi2, 4), 'p': round(p, 4),
                'dof': int(dof), 'sig': sig,
                'low_expected_pct': round(low_pct, 1),
                'fisher_p': round(fisher_p, 4) if fisher_p else None,
                'v': cramers_v(ct),
            }
            tests[(rv, cv)] = test_result
            
            summary_rows.append({
                '自变量': row_labels.get(rv, rv),
                '因变量': col_labels.get(cv, cv),
                'χ²': round(chi2, 4),
                'df': int(dof),
                'P值': round(p, 4),
                '显著性': sig,
                "Cramér's V": cramers_v(ct),
                '期望频数<5占比(%)': round(low_pct, 1),
            })
    
    return {
        'summary': pd.DataFrame(summary_rows),
        'crosstabs': crosstabs,
        'tests': tests,
    }


# ══════ 频数分布表（单变量） ══════

def frequency_table(series, sort='count', ascending=False):
    """单变量频数分布表
    
    Args:
        series: pd.Series
        sort: 'count'(按频数) / 'value'(按值) / None(不排序)
    
    Returns:
        DataFrame: 值, 频数, 百分比, 累计百分比
    """
    vc = series.value_counts(dropna=True)
    if sort == 'value':
        vc = vc.sort_index(ascending=ascending)
    elif sort == 'count':
        vc = vc.sort_values(ascending=ascending)
    
    total = vc.sum()
    df_out = pd.DataFrame({
        '值': vc.index,
        '频数': vc.values,
        '百分比(%)': (vc.values / total * 100).round(1),
    })
    df_out['累计百分比(%)'] = df_out['百分比(%)'].cumsum().round(1)
    return df_out.reset_index(drop=True)

