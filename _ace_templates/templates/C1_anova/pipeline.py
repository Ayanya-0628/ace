# -*- coding: utf-8 -*-
"""
C1_anova/pipeline.py — 方差分析流水线
适用场景：心率/血压/BIS/NRS 等临床指标的组间+时间交叉比较
         实验组/对照组前后测对比及LSD字母标记

自动完成：描述统计→正态性→方差齐性→ANOVA(+LSD事后比较)→三线表→Word
"""
import sys, os, warnings, argparse
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import shapiro, levene, f_oneway, kruskal, mannwhitneyu
from itertools import combinations
import string

warnings.filterwarnings('ignore')

TEMPLATE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, TEMPLATE_ROOT)
from text_library.blocks import *
from text_library.word_engine import ReportBuilder
from shared.utils import load_config


def lsd_letters(means, p_matrix, alpha=0.05):
    """
    根据LSD多重比较的P值矩阵为各组分配字母标记。
    means: {组名: 均值}
    p_matrix: {(组A, 组B): p值}
    返回: {组名: 字母标记}
    """
    sorted_groups = sorted(means.keys(), key=lambda g: means[g], reverse=True)
    n = len(sorted_groups)
    letters = {}
    current_letter_idx = 0

    if n <= 1:
        return {g: 'a' for g in sorted_groups}

    # Greedy letter assignment
    assigned = {g: set() for g in sorted_groups}
    for i in range(n):
        if not assigned[sorted_groups[i]]:
            assigned[sorted_groups[i]].add(current_letter_idx)
        for j in range(i + 1, n):
            g1, g2 = sorted_groups[i], sorted_groups[j]
            pair = (g1, g2) if (g1, g2) in p_matrix else (g2, g1)
            p = p_matrix.get(pair, 1.0)
            if p >= alpha:
                # 不显著差异，共享字母
                assigned[g2].update(assigned[g1])
            else:
                # 显著差异，需要新字母
                if not assigned[g2]:
                    current_letter_idx += 1
                    assigned[g2].add(current_letter_idx)
        if not assigned[sorted_groups[i]]:
            assigned[sorted_groups[i]].add(current_letter_idx)
            current_letter_idx += 1

    # 转换为字母
    for g in sorted_groups:
        idxs = sorted(assigned[g])
        letters[g] = ''.join(string.ascii_lowercase[i] for i in idxs if i < 26)
        if not letters[g]:
            letters[g] = string.ascii_lowercase[min(current_letter_idx, 25)]

    return letters


def one_way_anova_with_lsd(groups_data, group_names, alpha=0.05):
    """
    单因素方差分析 + LSD事后比较
    groups_data: [array1, array2, ...]
    group_names: [name1, name2, ...]
    """
    # ANOVA
    valid = [(n, d) for n, d in zip(group_names, groups_data) if len(d) >= 2]
    if len(valid) < 2:
        return {'F': np.nan, 'p': 1.0, 'sig': False, 'post_hoc': {}, 'letters': {}}

    names = [v[0] for v in valid]
    data = [v[1] for v in valid]

    if len(valid) == 2:
        t_stat, p_val = stats.ttest_ind(data[0], data[1])
        f_val = t_stat ** 2
    else:
        f_val, p_val = f_oneway(*data)

    means = {n: np.mean(d) for n, d in zip(names, data)}
    sds = {n: np.std(d, ddof=1) for n, d in zip(names, data)}
    ns = {n: len(d) for n, d in zip(names, data)}

    # LSD post-hoc
    N_total = sum(ns.values())
    k = len(names)
    MSE = sum(np.sum((d - np.mean(d)) ** 2) for d in data) / (N_total - k) if N_total > k else 1.0

    post_hoc = {}
    for g1, g2 in combinations(names, 2):
        d1 = dict(zip(names, data))[g1]
        d2 = dict(zip(names, data))[g2]
        se = np.sqrt(MSE * (1 / len(d1) + 1 / len(d2)))
        t_val = (np.mean(d1) - np.mean(d2)) / se if se > 0 else 0
        df = N_total - k
        p_pair = 2 * stats.t.sf(abs(t_val), df)
        post_hoc[(g1, g2)] = p_pair

    letters = lsd_letters(means, post_hoc, alpha)

    return {
        'F': f_val, 'p': p_val, 'sig': p_val < alpha,
        'means': means, 'sds': sds, 'ns': ns,
        'post_hoc': post_hoc, 'letters': letters
    }


def run_pipeline(config_path):
    cfg = load_config(config_path)
    project_dir = os.path.dirname(os.path.abspath(config_path))
    data_path = os.path.join(project_dir, cfg['data_file'])
    out_dir = os.path.join(project_dir, cfg.get('output', {}).get('output_dir', '交付成果'))
    os.makedirs(out_dir, exist_ok=True)

    print(f'[C1] 项目: {cfg["project_name"]}')

    # ── 数据读取 ──
    df = pd.read_excel(data_path, sheet_name=cfg.get('sheet_name', 0))
    N = len(df)
    print(f'  数据量: {N} 行')

    factors = cfg['factors']
    indicators = cfg['indicators']
    post_hoc_method = cfg.get('analysis', {}).get('post_hoc', 'LSD')
    show_letters = cfg.get('table_style', {}).get('show_letters', True)

    # 提取因素列和标签
    factor_A = factors[0]  # 主因素（如"组别"）
    fA_col = factor_A['col']
    fA_labels = factor_A.get('labels', {})
    fA_groups = sorted(df[fA_col].dropna().unique())

    has_factor_B = len(factors) > 1
    if has_factor_B:
        factor_B = factors[1]
        fB_col = factor_B['col']
        fB_labels = factor_B.get('labels', {})
        fB_groups = sorted(df[fB_col].dropna().unique())

    # ── 报告生成 ──
    preset = cfg.get('output', {}).get('format_preset', 'thesis_songti')
    rb = ReportBuilder(preset_name=preset)
    rb.add_title(f'{cfg["project_name"]}\n——统计分析报告')

    # ═══ 一、描述性统计 + ANOVA ═══
    rb.add_heading('一、各指标描述性统计与方差分析')

    for indicator in indicators:
        ind_name = indicator['name']
        ind_col = indicator['col']
        ind_unit = indicator.get('unit', '')

        if ind_col not in df.columns:
            print(f'  ⚠ 指标列 {ind_col} 不存在，跳过')
            continue

        t = rb.next_table_no()

        if has_factor_B:
            # ═ 双因素情况：因素A × 因素B 交叉 ═
            rb.add_heading(f'（{"一二三四五六七八"[indicators.index(indicator)]}）{ind_name}', level=2)

            # 构建交叉表
            data_rows = []
            # 分组数据行
            for ga in fA_groups:
                ga_label = fA_labels.get(ga, fA_labels.get(str(ga), str(ga)))
                first_row = True
                for gb in fB_groups:
                    gb_label = fB_labels.get(gb, fB_labels.get(str(gb), str(gb)))
                    mask = (df[fA_col] == ga) & (df[fB_col] == gb)
                    vals = df.loc[mask, ind_col].dropna()
                    if len(vals) > 0:
                        cell = f'{vals.mean():.2f}±{vals.std():.2f}'
                    else:
                        cell = '-'
                    data_rows.append([ga_label if first_row else '', gb_label, cell])
                    first_row = False

            # 因素A 边际均值（各组别的总均值）
            data_rows.append(['─' * 3, '─' * 3, '─' * 5])
            for ga in fA_groups:
                ga_label = fA_labels.get(ga, fA_labels.get(str(ga), str(ga)))
                vals = df[df[fA_col] == ga][ind_col].dropna()
                cell = f'{vals.mean():.2f}±{vals.std():.2f}'
                # 因素A组间LSD
                data_rows.append([f'{factor_A["name"]}均值', ga_label, cell])

            # 因素B 边际均值
            for gb in fB_groups:
                gb_label = fB_labels.get(gb, fB_labels.get(str(gb), str(gb)))
                vals = df[df[fB_col] == gb][ind_col].dropna()
                cell = f'{vals.mean():.2f}±{vals.std():.2f}'
                data_rows.append([f'{factor_B["name"]}均值', gb_label, cell])

            # ANOVA结果
            data_rows.append(['─' * 3, '─' * 3, '─' * 5])
            # 因素A单因素
            groups_A = [df[df[fA_col] == g][ind_col].dropna().values for g in fA_groups]
            names_A = [fA_labels.get(g, str(g)) for g in fA_groups]
            res_A = one_way_anova_with_lsd(groups_A, names_A)
            sig_A = '**' if res_A['p'] < 0.01 else ('*' if res_A['p'] < 0.05 else 'ns')
            data_rows.append([f'{factor_A["name"]}', 'F值', f'{res_A["F"]:.3f}{sig_A}'])

            # 因素B单因素
            groups_B = [df[df[fB_col] == g][ind_col].dropna().values for g in fB_groups]
            names_B = [fB_labels.get(g, str(g)) for g in fB_groups]
            res_B = one_way_anova_with_lsd(groups_B, names_B)
            sig_B = '**' if res_B['p'] < 0.01 else ('*' if res_B['p'] < 0.05 else 'ns')
            data_rows.append([f'{factor_B["name"]}', 'F值', f'{res_B["F"]:.3f}{sig_B}'])

            rb.add_three_line_table(
                [factor_A['name'], factor_B['name'], f'{ind_name}({ind_unit})'],
                data_rows,
                title=f'表{t}  {ind_name}的描述性统计与方差分析结果'
            )
            rb.add_note(f'注：数据以均值±标准差表示；**P<0.01，*P<0.05，ns=不显著。'
                        f'事后比较采用{post_hoc_method}法。')

            # 文字
            text = f'由表{t}可知，'
            if res_A['sig']:
                text += f'不同{factor_A["name"]}的{ind_name}差异具有统计学意义（F={res_A["F"]:.3f}，P{_p_str(res_A["p"])}）。'
            else:
                text += f'不同{factor_A["name"]}的{ind_name}差异无统计学意义（F={res_A["F"]:.3f}，P{_p_str(res_A["p"])}）。'
            if res_B['sig']:
                text += f'不同{factor_B["name"]}的{ind_name}差异具有统计学意义（F={res_B["F"]:.3f}，P{_p_str(res_B["p"])}）。'
            rb.add_body_text(text)

        else:
            # ═ 单因素情况 ═
            rb.add_heading(f'（{"一二三四五六七八"[indicators.index(indicator)]}）{ind_name}', level=2)

            groups = [df[df[fA_col] == g][ind_col].dropna().values for g in fA_groups]
            names = [fA_labels.get(g, fA_labels.get(str(g), str(g))) for g in fA_groups]
            res = one_way_anova_with_lsd(groups, names)

            data_rows = []
            for name in names:
                m = res['means'].get(name, 0)
                s = res['sds'].get(name, 0)
                n = res['ns'].get(name, 0)
                letter = res['letters'].get(name, '') if show_letters else ''
                cell = f'{m:.3f}±{s:.3f}'
                if letter:
                    cell += f' {letter}'
                data_rows.append([name, str(n), cell])

            sig = '**' if res['p'] < 0.01 else ('*' if res['p'] < 0.05 else 'ns')
            data_rows.append(['F值', '', f'{res["F"]:.3f}{sig}'])

            rb.add_three_line_table(
                [factor_A['name'], 'N', f'{ind_name}({ind_unit})'],
                data_rows,
                title=f'表{t}  不同{factor_A["name"]}的{ind_name}比较'
            )
            rb.add_note(f'注：数据以均值±标准差表示。相同字母表示差异不显著（P>0.05）。')

            anova_results = [(ind_name, res['F'], res['p'],
                              max(res['means'], key=res['means'].get),
                              max(res['means'].values()),
                              min(res['means'], key=res['means'].get),
                              min(res['means'].values()))]
            rb.add_body_text(difference_anova(t, factor_A['name'], anova_results))

    # ── 保存 ──
    report_name = cfg['project_name'].replace(' ', '_') + '_分析报告.docx'
    rb.save(os.path.join(out_dir, report_name))
    print(f'\n[C1] ✅ 完成！共生成 {rb.table_count} 张表。')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='C1 方差分析流水线')
    parser.add_argument('--config', required=True, help='config.yaml 路径')
    args = parser.parse_args()
    run_pipeline(args.config)
