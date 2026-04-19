# -*- coding: utf-8 -*-
"""
D1_medical/pipeline.py — 医学/临床统计分析流水线
适用场景：中医证型分布、卡方检验、交叉分析、组间比较（参数/非参数自动判断）

自动完成：频数分布→描述统计→正态性→组间比较→卡方/交叉表→Word报告
"""
import sys, os, warnings, argparse
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import shapiro, chi2_contingency, mannwhitneyu, kruskal, f_oneway

warnings.filterwarnings('ignore')

TEMPLATE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, TEMPLATE_ROOT)
from text_library.blocks import *
from text_library.word_engine import ReportBuilder
from shared.utils import load_config


def auto_test(groups_data, group_names):
    """自动选择参数/非参数检验"""
    valid = [(n, d) for n, d in zip(group_names, groups_data) if len(d) >= 3]
    if len(valid) < 2:
        return {'method': '样本不足', 'stat': np.nan, 'p': 1.0}

    names = [v[0] for v in valid]
    data = [v[1] for v in valid]

    # 正态性判断
    all_normal = all(shapiro(d[:5000])[1] > 0.05 for d in data if len(d) >= 3)

    if len(valid) == 2:
        if all_normal:
            stat, p = stats.ttest_ind(data[0], data[1])
            return {'method': '独立样本t检验', 'stat': stat, 'p': p}
        else:
            stat, p = mannwhitneyu(data[0], data[1], alternative='two-sided')
            return {'method': 'Mann-Whitney U检验', 'stat': stat, 'p': p}
    else:
        if all_normal:
            stat, p = f_oneway(*data)
            return {'method': '单因素ANOVA', 'stat': stat, 'p': p}
        else:
            stat, p = kruskal(*data)
            return {'method': 'Kruskal-Wallis H检验', 'stat': stat, 'p': p}


def run_pipeline(config_path):
    cfg = load_config(config_path)
    project_dir = os.path.dirname(os.path.abspath(config_path))
    data_path = os.path.join(project_dir, cfg['data_file'])
    out_dir = os.path.join(project_dir, cfg.get('output', {}).get('output_dir', '交付成果'))
    os.makedirs(out_dir, exist_ok=True)

    print(f'[D1] 项目: {cfg["project_name"]}')

    df = pd.read_excel(data_path, sheet_name=cfg.get('sheet_name', 0))
    N = len(df)
    print(f'  数据量: {N} 行')

    cat_vars = cfg.get('categorical_vars', [])
    cont_vars = cfg.get('continuous_vars', [])

    preset = cfg.get('output', {}).get('format_preset', 'thesis_songti')
    rb = ReportBuilder(preset_name=preset)
    rb.add_title(f'{cfg["project_name"]}\n——统计分析报告')
    rb.add_body_text(f'本报告基于{N}例临床资料进行统计分析。')

    # ═══ 一、频数分布 ═══
    if cfg.get('analysis', {}).get('frequency', True):
        rb.add_heading('一、一般资料分布')
        for cv in cat_vars:
            t = rb.next_table_no()
            col = cv['col']
            labels = cv.get('labels', {})
            if col not in df.columns:
                continue

            vc = df[col].value_counts().sort_index()
            total = vc.sum()
            freq_rows = []
            items = []
            for code, count in vc.items():
                label = labels.get(code, labels.get(str(code), str(code)))
                pct = count / total * 100
                freq_rows.append([label, str(count), f'{pct:.1f}'])
                items.append((label, count, pct))
            freq_rows.append(['合计', str(total), '100.0'])

            rb.add_three_line_table(
                [cv['name'], '例数', '构成比(%)'],
                freq_rows,
                title=f'表{t}  {cv["name"]}分布(N={N})'
            )
            # 文字
            sorted_items = sorted(items, key=lambda x: x[1], reverse=True)
            text = f'由表{t}可知，{sorted_items[0][0]}占比最高（{sorted_items[0][1]}例，{sorted_items[0][2]:.1f}%），'
            if len(sorted_items) > 1:
                text += f'其次为{sorted_items[1][0]}（{sorted_items[1][1]}例，{sorted_items[1][2]:.1f}%）'
                if len(sorted_items) > 2:
                    text += f'，{sorted_items[-1][0]}占比最低（{sorted_items[-1][1]}例，{sorted_items[-1][2]:.1f}%）'
            text += '。'
            rb.add_body_text(text)

    # ═══ 二、描述性统计（连续变量） ═══
    if cfg.get('analysis', {}).get('descriptive', True) and cont_vars:
        t = rb.next_table_no()
        rb.add_heading('二、连续变量描述性统计')
        desc_rows = []
        for cv in cont_vars:
            col = cv['col']
            if col not in df.columns:
                continue
            vals = df[col].dropna()
            # 正态性
            w, p_norm = shapiro(vals[:5000]) if len(vals) >= 3 else (np.nan, 1.0)
            if p_norm > 0.05:
                # 正态：报告 M±SD
                desc_rows.append([f'{cv["name"]}({cv.get("unit", "")})',
                                  f'{vals.mean():.2f}±{vals.std():.2f}',
                                  f'{vals.min():.1f}', f'{vals.max():.1f}',
                                  '正态'])
            else:
                # 非正态：报告 M(Q1, Q3)
                q1, q3 = vals.quantile(0.25), vals.quantile(0.75)
                desc_rows.append([f'{cv["name"]}({cv.get("unit", "")})',
                                  f'{vals.median():.2f}({q1:.2f}, {q3:.2f})',
                                  f'{vals.min():.1f}', f'{vals.max():.1f}',
                                  '偏态'])

        rb.add_three_line_table(
            ['变量', '集中趋势', '最小值', '最大值', '分布'],
            desc_rows,
            title=f'表{t}  连续变量描述性统计(N={N})'
        )
        rb.add_note('注：正态分布变量以均值±标准差表示，偏态分布以中位数(P25, P75)表示。')

    # ═══ 三、组间比较 ═══
    gc_cfg = cfg.get('analysis', {}).get('group_comparison', None)
    if gc_cfg:
        rb.add_heading('三、组间比较')
        gvar = gc_cfg['group_var']
        compare_vars = gc_cfg['compare_vars']

        # 找到分组变量的配置
        gvar_cfg = next((cv for cv in cat_vars if cv['name'] == gvar), None)
        if gvar_cfg and gvar_cfg['col'] in df.columns:
            gcol = gvar_cfg['col']
            glabels = gvar_cfg.get('labels', {})
            g_vals = sorted(df[gcol].dropna().unique())
            g_names = [glabels.get(g, glabels.get(str(g), str(g))) for g in g_vals]

            t = rb.next_table_no()
            comp_rows = []
            for cvar_name in compare_vars:
                cvar_cfg = next((cv for cv in cont_vars if cv['name'] == cvar_name), None)
                if not cvar_cfg or cvar_cfg['col'] not in df.columns:
                    continue
                ccol = cvar_cfg['col']

                groups_data = [df[df[gcol] == g][ccol].dropna().values for g in g_vals]
                result = auto_test(groups_data, g_names)

                first = True
                for gn, gd in zip(g_names, groups_data):
                    if len(gd) > 0:
                        comp_rows.append([
                            cvar_name if first else '', gn, str(len(gd)),
                            f'{gd.mean():.2f}±{gd.std():.2f}',
                            f'{result["stat"]:.3f}' if first else '',
                            f'{result["p"]:.4f}' if first else ''
                        ])
                        first = False

            rb.add_three_line_table(
                ['变量', '组别', '例数', cvar_name if len(compare_vars) == 1 else '均值±标准差', 't/F', 'P'],
                comp_rows,
                title=f'表{t}  不同{gvar}的连续变量比较'
            )
            rb.add_note('注：结果列以均值±标准差表示；参数检验时统计量列对应 t 或 F，非参数检验时对应 U 或 H。')

    # ═══ 四、交叉分析（卡方检验） ═══
    cross_cfgs = cfg.get('analysis', {}).get('cross_tab', [])
    if cross_cfgs:
        rb.add_heading('四、交叉分析')
        for cc in cross_cfgs:
            row_name = cc['row']
            col_name = cc['col']

            row_cfg = next((cv for cv in cat_vars if cv['name'] == row_name), None)
            col_cfg = next((cv for cv in cat_vars if cv['name'] == col_name), None)
            if not row_cfg or not col_cfg:
                continue

            rcol, ccol = row_cfg['col'], col_cfg['col']
            if rcol not in df.columns or ccol not in df.columns:
                continue

            rlabels = row_cfg.get('labels', {})
            clabels = col_cfg.get('labels', {})

            t = rb.next_table_no()
            ct = pd.crosstab(df[rcol], df[ccol])
            chi2, p_chi, dof_chi, _ = chi2_contingency(ct)

            cross_rows = []
            r_vals = sorted(ct.index)
            c_vals = sorted(ct.columns)
            for rv in r_vals:
                rl = rlabels.get(rv, rlabels.get(str(rv), str(rv)))
                row = [rl]
                row_total = ct.loc[rv].sum()
                for cv_val in c_vals:
                    n = ct.loc[rv, cv_val] if cv_val in ct.columns else 0
                    pct = n / row_total * 100 if row_total > 0 else 0
                    row.append(f'{n}({pct:.1f}%)')
                row.append(str(row_total))
                cross_rows.append(row)

            # 合计行
            total_row = ['合计']
            for cv_val in c_vals:
                col_sum = ct[cv_val].sum()
                total_row.append(str(col_sum))
            total_row.append(str(ct.values.sum()))
            cross_rows.append(total_row)

            c_headers = [clabels.get(cv_val, clabels.get(str(cv_val), str(cv_val))) for cv_val in c_vals]
            rb.add_three_line_table(
                [row_name] + c_headers + ['合计'],
                cross_rows,
                title=f'表{t}  {row_name}与{col_name}的交叉分析'
            )
            rb.add_note(f'注：χ²={chi2:.3f}，df={dof_chi}，P{_p_str(p_chi)}')

            # 文字
            rb.add_body_text(chi_square_test(t, row_name, col_name, chi2, p_chi))

    # ── 保存 ──
    report_name = cfg['project_name'].replace(' ', '_') + '_分析报告.docx'
    rb.save(os.path.join(out_dir, report_name))
    print(f'\n[D1] ✅ 完成！共生成 {rb.table_count} 张表。')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='D1 医学/临床统计分析流水线')
    parser.add_argument('--config', required=True, help='config.yaml 路径')
    args = parser.parse_args()
    run_pipeline(args.config)
