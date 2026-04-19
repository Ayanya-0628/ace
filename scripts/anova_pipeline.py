# -*- coding: utf-8 -*-
"""
ACE 方差分析流水线
===================
用法:
    python anova_pipeline.py data.xlsx --indicators HR MAP BIS --group 组别 --time 时间
        --time-order 入室后 阻滞后 开始时 5min 15min 30min 手术结束时
        --output result.docx

功能:
    1. 双因素方差分析（组别×时间）
    2. LSD 多重比较 → 紧凑字母显示（CLD）
    3. 三线表 Word 输出
    4. 结果分析段落自动生成

也可作为模块导入:
    from anova_pipeline import do_two_way_anova, lsd_comparison, cld_from_pmatrix
"""

import argparse
import sys
import numpy as np
import pandas as pd
from scipy import stats
from itertools import combinations
import statsmodels.api as sm
from statsmodels.formula.api import ols
import warnings
warnings.filterwarnings('ignore')


# ============================================================
# 统计分析核心函数
# ============================================================

def cld_from_pmatrix(p_matrix, means, alpha=0.05):
    """
    从 p 值矩阵生成紧凑字母显示 (CLD)

    Args:
        p_matrix: k×k 对称矩阵，p_matrix[i][j] = LSD 比较 p 值
        means: 各水平均值 (用于排序)
        alpha: 显著性水平
    Returns:
        list of str: 每个水平的字母标记
    """
    k = len(means)
    sorted_idx = np.argsort(means)[::-1]
    letters_list = [[] for _ in range(k)]
    current_letter = 0
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    remaining = set(range(k))

    while remaining:
        start = None
        for idx in sorted_idx:
            if idx in remaining:
                start = idx
                break
        if start is None:
            break

        group = {start}
        for idx in sorted_idx:
            if idx == start:
                continue
            can_add = all(p_matrix[idx][m] >= alpha for m in group)
            if can_add:
                group.add(idx)

        letter = alphabet[current_letter % 26]
        for idx in group:
            letters_list[idx].append(letter)
        current_letter += 1

        new_remaining = set()
        for idx in remaining:
            if idx not in group:
                new_remaining.add(idx)
            else:
                for other in remaining:
                    if other != idx and other not in group and p_matrix[idx][other] >= alpha:
                        new_remaining.add(idx)
                        break
        if new_remaining == remaining:
            for idx in group:
                if idx in remaining:
                    new_remaining.discard(idx)
                    break
        remaining = new_remaining

    return [''.join(sorted(set(ll))) if ll else 'a' for ll in letters_list]


def lsd_comparison_independent(data_arrays, labels, alpha=0.05):
    """
    独立样本 LSD 多重比较

    Args:
        data_arrays: list of array-like
        labels: list of str
    Returns:
        dict: {label: letter}
    """
    k = len(data_arrays)
    n_total = sum(len(a) for a in data_arrays)
    ss_within = sum(np.sum((a - np.mean(a)) ** 2) for a in data_arrays)
    df_within = n_total - k
    mse = ss_within / df_within if df_within > 0 else 1
    means = [np.mean(a) for a in data_arrays]
    ns = [len(a) for a in data_arrays]

    p_matrix = np.ones((k, k))
    for i, j in combinations(range(k), 2):
        se = np.sqrt(mse * (1 / ns[i] + 1 / ns[j]))
        t_val = abs(means[i] - means[j]) / se if se > 0 else 0
        p_val = 2 * (1 - stats.t.cdf(t_val, df_within))
        p_matrix[i][j] = p_val
        p_matrix[j][i] = p_val

    letters = cld_from_pmatrix(p_matrix, means, alpha)
    return {labels[i]: letters[i] for i in range(k)}


def lsd_comparison_paired(df, value_col, time_col, time_labels, alpha=0.05):
    """
    组内配对 LSD 多重比较

    Args:
        df: 单组数据
        value_col: 数值列名
        time_col: 时间列名
        time_labels: 时间水平顺序
    Returns:
        dict: {time_label: letter}
    """
    k = len(time_labels)
    data_arrays = [df[df[time_col] == t][value_col].dropna().values for t in time_labels]
    means = [np.mean(a) for a in data_arrays]
    p_matrix = np.ones((k, k))

    for i, j in combinations(range(k), 2):
        n_min = min(len(data_arrays[i]), len(data_arrays[j]))
        if n_min > 1:
            _, p_val = stats.ttest_rel(data_arrays[i][:n_min], data_arrays[j][:n_min])
            p_matrix[i][j] = p_val
            p_matrix[j][i] = p_val

    letters = cld_from_pmatrix(p_matrix, means, alpha)
    return {time_labels[i]: letters[i] for i in range(k)}


def do_two_way_anova(df, value_col, group_col='组别', time_col='时间'):
    """
    双因素方差分析

    Args:
        df: DataFrame
        value_col: 因变量列名
        group_col: 组别列名
        time_col: 时间/重复测量列名
    Returns:
        dict: {'group': (F, p), 'time': (F, p), 'interaction': (F, p)}
    """
    df_temp = df.copy()
    df_temp['_group'] = df_temp[group_col].astype(str)
    df_temp['_time'] = df_temp[time_col].astype(str)
    model = ols(f'{value_col} ~ C(_group) * C(_time)', data=df_temp).fit()
    at = sm.stats.anova_lm(model, typ=2)

    return {
        'group': (at.loc['C(_group)', 'F'], at.loc['C(_group)', 'PR(>F)']),
        'time': (at.loc['C(_time)', 'F'], at.loc['C(_time)', 'PR(>F)']),
        'interaction': (at.loc['C(_group):C(_time)', 'F'],
                        at.loc['C(_group):C(_time)', 'PR(>F)']),
    }


def assign_subject_id(df, group_col, n_timepoints):
    """分配受试者 ID（按组别×时间点数推断）"""
    df = df.copy()
    df['subject'] = -1
    sid = 0
    for grp in df[group_col].unique():
        mask = df[group_col] == grp
        grp_indices = df[mask].index
        n_subjects = len(grp_indices) // n_timepoints
        for s in range(n_subjects):
            start = s * n_timepoints
            end = start + n_timepoints
            indices = grp_indices[start:end]
            df.loc[indices, 'subject'] = sid
            sid += 1
    return df


def format_f_sig(F_val, p_val):
    """格式化 F 值 + 显著性标记"""
    if p_val < 0.01:
        return f'{F_val:.1f}**'
    elif p_val < 0.05:
        return f'{F_val:.1f}*'
    else:
        return f'{F_val:.1f}ns'


# ============================================================
# 完整分析流程
# ============================================================

def analyze(df, indicators, time_order, groups, group_col='组别', time_col='时间'):
    """
    对数据集做完整双因素方差分析

    Args:
        df: DataFrame
        indicators: list of dict, [{'col': 'HR', 'name_cn': 'HR(次/min)', 'name_en': 'HR(beats/min)'}]
        time_order: 时间水平顺序
        groups: 组别列表
        group_col: 组别列名
        time_col: 时间列名
    Returns:
        dict: 完整结构化结果
    """
    result = {
        'indicators': indicators,
        'time_order': time_order,
        'groups': groups,
        'cell_data': {},
        'within_letters': {},
        'group_means': {},
        'group_letters': {},
        'time_means': {},
        'time_letters': {},
        'anova': {},
    }

    for ind in indicators:
        col = ind['col']
        print(f"  分析 {ind['name_cn']} ...")

        # 各 Cell 均值±标准差
        for g in groups:
            for t in time_order:
                vals = df[(df[group_col] == g) & (df[time_col] == t)][col].dropna()
                result['cell_data'][(g, t, col)] = {
                    'mean': vals.mean(), 'std': vals.std(), 'n': len(vals)
                }

        # 组内 LSD（小写字母）
        for g in groups:
            g_df = df[df[group_col] == g]
            letters = lsd_comparison_paired(g_df, col, time_col, time_order)
            for t in time_order:
                result['within_letters'][(g, t, col)] = letters[t]

        # 组间 LSD（大写字母）
        group_arrays = []
        for g in groups:
            vals = df[df[group_col] == g][col].dropna().values
            result['group_means'][(g, col)] = {'mean': vals.mean(), 'std': vals.std()}
            group_arrays.append(vals)
        gl = lsd_comparison_independent(group_arrays, groups)
        for g in groups:
            result['group_letters'][(g, col)] = gl[g].upper()

        # 时间间 LSD（大写字母）
        time_arrays = []
        for t in time_order:
            vals = df[df[time_col] == t][col].dropna().values
            result['time_means'][(t, col)] = {'mean': vals.mean(), 'std': vals.std()}
            time_arrays.append(vals)
        tl = lsd_comparison_independent(time_arrays, time_order)
        for t in time_order:
            result['time_letters'][(t, col)] = tl[t].upper()

        # ANOVA
        result['anova'][col] = do_two_way_anova(df, col, group_col, time_col)

    return result


def print_summary(result):
    """打印分析摘要到终端"""
    print("\n" + "=" * 60)
    print("  ANOVA 分析摘要")
    print("=" * 60)
    for ind in result['indicators']:
        col = ind['col']
        name = ind['name_cn']
        a = result['anova'][col]
        print(f"\n  {name}:")
        print(f"    组别效应:   F={a['group'][0]:.2f}, p={a['group'][1]:.4f}  "
              f"{'**' if a['group'][1]<0.01 else ('*' if a['group'][1]<0.05 else 'ns')}")
        print(f"    时间效应:   F={a['time'][0]:.2f}, p={a['time'][1]:.4f}  "
              f"{'**' if a['time'][1]<0.01 else ('*' if a['time'][1]<0.05 else 'ns')}")
        print(f"    交互效应:   F={a['interaction'][0]:.2f}, p={a['interaction'][1]:.4f}  "
              f"{'**' if a['interaction'][1]<0.01 else ('*' if a['interaction'][1]<0.05 else 'ns')}")


def main():
    parser = argparse.ArgumentParser(description="ACE 方差分析流水线")
    parser.add_argument("file", help="Excel 数据文件")
    parser.add_argument("--sheet", default=0, help="Sheet名或索引")
    parser.add_argument("--indicators", nargs="+", required=True,
                        help="指标列名 (如 HR MAP BIS)")
    parser.add_argument("--group", default="组别", help="组别列名")
    parser.add_argument("--time", default="时间", help="时间/重复测量列名")
    parser.add_argument("--time-order", nargs="+", default=None,
                        help="时间水平顺序 (默认按数据中出现顺序)")
    parser.add_argument("--output", default=None, help="输出 Word 文件路径")
    args = parser.parse_args()

    # 读取
    sheet = int(args.sheet) if str(args.sheet).isdigit() else args.sheet
    df = pd.read_excel(args.file, sheet_name=sheet)
    print(f"📂 数据: {args.file}, 样本量={len(df)}")

    groups = df[args.group].unique().tolist()
    time_order = args.time_order or df[args.time].unique().tolist()

    # 构建指标
    indicators = [{'col': c, 'name_cn': c, 'name_en': c} for c in args.indicators]

    # 分配 subject ID
    df = assign_subject_id(df, args.group, len(time_order))

    # 分析
    print("\n🔬 执行双因素方差分析...")
    result = analyze(df, indicators, time_order, groups, args.group, args.time)
    print_summary(result)

    # Word 输出
    if args.output:
        try:
            from three_line_table import ThreeLineTable, create_doc_landscape
        except ImportError:
            # 添加当前目录到路径
            import os
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from three_line_table import ThreeLineTable, create_doc_landscape

        doc = create_doc_landscape()
        ind_names = '/'.join(i['name_cn'] for i in indicators)
        ThreeLineTable.add_table_title(
            doc,
            f'两组不同时间点{ind_names}比较（x̄±s）'
        )

        # 构建表格数据行
        headers = [args.group, args.time] + [i['name_cn'] for i in indicators]
        rows = []
        for g in groups:
            for t in time_order:
                row = [g, t]
                for ind in indicators:
                    col = ind['col']
                    d = result['cell_data'][(g, t, col)]
                    letter = result['within_letters'][(g, t, col)]
                    row.append(f"{d['mean']:.1f}±{d['std']:.1f} {letter}")
                rows.append(row)

        table = ThreeLineTable.build_simple(doc, headers, rows)
        ThreeLineTable.add_note(
            doc,
            '注：小写字母表示差异在同一组别不同时间间达5%显著水平；'
            'ns表示差异不显著，*和**分别表示差异达到5%和1%显著水平。'
        )
        doc.save(args.output)
        print(f"\n📁 Word 三线表已保存: {args.output}")

    print("\n✅ 分析完成")


if __name__ == "__main__":
    main()
