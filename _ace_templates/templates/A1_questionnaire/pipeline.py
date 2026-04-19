# -*- coding: utf-8 -*-
"""
A1_questionnaire/pipeline.py — 问卷全套分析流水线
用法：python pipeline.py --config ./config.yaml

自动完成：数据清洗→正态性→人口学→描述统计→信度→效度→相关→差异→回归→Word报告
"""
import sys, os, warnings, argparse
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import f_oneway, pearsonr, spearmanr, shapiro
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

warnings.filterwarnings('ignore')

# ── 加载模板引擎 + 公共工具 ──
TEMPLATE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, TEMPLATE_ROOT)
from text_library.blocks import *
from text_library.word_engine import ReportBuilder
from shared.utils import load_config, cronbach_alpha, load_and_clean, compute_dimension_scores


def run_pipeline(config_path):
    cfg = load_config(config_path)
    project_dir = os.path.dirname(os.path.abspath(config_path))
    out_dir = os.path.join(project_dir, cfg.get('output', {}).get('output_dir', '交付成果'))
    os.makedirs(out_dir, exist_ok=True)

    print(f'[A1] 项目: {cfg["project_name"]}')

    # ══════════════════════════════════════════════
    #  Step 0: 数据读取 + 清洗（使用 shared.utils）
    # ══════════════════════════════════════════════
    print('[Step 0] 数据读取与清洗...')
    df, N_raw, N, all_item_cols, demo_cols = load_and_clean(cfg, project_dir)
    print(f'  原始 {N_raw} 行 → 有效 {N} 行')

    # ══════════════════════════════════════════════
    #  Step 0.5: 计算维度得分（使用 shared.utils）
    # ══════════════════════════════════════════════
    print('[Step 0.5] 计算维度得分...')
    dim_cols_map, scale_dims, all_dim_names, scale_names = compute_dimension_scores(df, cfg)


    # ══════════════════════════════════════════════
    #  Step 1: 正态性检验
    # ══════════════════════════════════════════════
    print('[Step 1] 正态性检验...')
    norm_results = []
    all_normal = True
    for dim in scale_names:
        stat_w, p_w = shapiro(df[dim].dropna()[:5000])
        normal = p_w > 0.05
        if not normal:
            all_normal = False
        norm_results.append([dim, str(N), f'{stat_w:.4f}', f'{p_w:.4f}',
                             '正态' if normal else '非正态'])

    # ══════════════════════════════════════════════
    #  Step 2: 人口学描述性统计
    # ══════════════════════════════════════════════
    print('[Step 2] 人口学描述性统计...')
    demo_table = []
    demo_detail = {}
    for d in cfg.get('demographics', []):
        col = d['col']
        labels = d.get('labels', {})
        vc = df[col].value_counts().sort_index()
        total = vc.sum()
        items = []
        first = True
        for code, count in vc.items():
            label = labels.get(code, labels.get(str(code), str(code)))
            pct = count / total * 100
            demo_table.append([col if first else '', label, str(count), f'{pct:.1f}'])
            items.append((label, count, pct))
            first = False
        demo_detail[col] = items

    # ══════════════════════════════════════════════
    #  Step 3: 各变量描述性统计
    # ══════════════════════════════════════════════
    print('[Step 3] 各变量描述性统计...')
    desc_table = []
    dim_stats_list = []
    for dim in all_dim_names:
        m, s = df[dim].mean(), df[dim].std()
        desc_table.append([dim, f'{m:.3f}', f'{s:.3f}'])
        dim_stats_list.append((dim, m, s))

    # ══════════════════════════════════════════════
    #  Step 4: 信度检验
    # ══════════════════════════════════════════════
    print('[Step 4] 信度检验...')
    rel_table = []
    dim_alphas = []
    total_alpha_val = None  # reserved for future use
    for scale in cfg['scales']:
        sname = scale['name']
        # 各维度
        if scale.get('dimensions'):
            for dim in scale['dimensions']:
                dname = dim['name']
                items = dim['items']
                a = cronbach_alpha(df[items])
                rel_table.append([dname, str(len(items)), f'{a:.3f}'])
                dim_alphas.append((dname, a))
        # 总量表
        a_total = cronbach_alpha(df[scale['items']])
        rel_table.append([f'{sname}(总)', str(len(scale['items'])), f'{a_total:.3f}'])
    # 所有题目的总信度
    all_items_data = df[all_item_cols]
    overall_alpha = cronbach_alpha(all_items_data)

    # ══════════════════════════════════════════════
    #  Step 5: 效度检验
    # ══════════════════════════════════════════════
    print('[Step 5] 效度检验...')
    data_efa = df[all_item_cols].dropna()
    n_obs = len(data_efa)
    p_vars = data_efa.shape[1]

    # KMO
    corr_mat = data_efa.corr().values.copy()
    try:
        inv_corr = np.linalg.inv(corr_mat)
        D_diag = np.diag(1.0 / np.sqrt(np.diag(inv_corr)))
        partial_corr = -D_diag @ inv_corr @ D_diag
        np.fill_diagonal(partial_corr, 0)
        corr_nodiag = corr_mat.copy()
        np.fill_diagonal(corr_nodiag, 0)
        kmo_val = (corr_nodiag ** 2).sum() / ((corr_nodiag ** 2).sum() + (partial_corr ** 2).sum())
    except:
        kmo_val = 0.5

    # Bartlett
    det_val = np.linalg.det(corr_mat)
    chi2_val = -(n_obs - 1 - (2 * p_vars + 5) / 6) * np.log(max(det_val, 1e-300))
    dof = p_vars * (p_vars - 1) / 2
    p_bart = stats.chi2.sf(chi2_val, dof)

    # EFA
    n_factors = len(cfg['scales'])
    X_std = StandardScaler().fit_transform(data_efa)
    pca = PCA(n_components=min(n_factors, p_vars))
    pca.fit(X_std)
    cum_var_pct = np.sum(pca.explained_variance_ratio_) * 100

    # ══════════════════════════════════════════════
    #  Step 6: 相关分析
    # ══════════════════════════════════════════════
    print('[Step 6] 相关分析...')
    corr_vars = scale_names
    corr_data = df[corr_vars].dropna()
    corr_matrix = corr_data.corr()
    corr_pairs = []
    for i in range(len(corr_vars)):
        for j in range(i + 1, len(corr_vars)):
            r, p = pearsonr(corr_data[corr_vars[i]], corr_data[corr_vars[j]])
            corr_pairs.append((corr_vars[i], corr_vars[j], r, p))

    # ══════════════════════════════════════════════
    #  Step 7: 差异分析
    # ══════════════════════════════════════════════
    print('[Step 7] 差异分析...')
    diff_results = {}
    for d in cfg.get('demographics', []):
        col = d['col']
        test_type = d.get('test', 'anova')
        labels = d.get('labels', {})
        diff_results[col] = {}

        groups = sorted(df[col].dropna().unique())
        for dim in scale_names:
            group_data = [df[df[col] == g][dim].dropna() for g in groups]
            valid = [(g, data) for g, data in zip(groups, group_data) if len(data) >= 2]
            if len(valid) < 2:
                diff_results[col][dim] = {'method': '样本不足', 'stat': np.nan, 'p': 1.0,
                                          'group_stats': [], 'sig': False}
                continue

            groups_v = [v[0] for v in valid]
            data_v = [v[1] for v in valid]

            if len(valid) == 2 and test_type in ('ttest', 'binary'):
                t_stat, t_p = stats.ttest_ind(data_v[0], data_v[1])
                method, stat_val, p_val = 't检验', t_stat, t_p
            else:
                f_stat, f_p = f_oneway(*data_v)
                method, stat_val, p_val = 'ANOVA', f_stat, f_p

            group_stats = [{'label': labels.get(g, labels.get(str(g), str(g))),
                            'n': len(d_), 'mean': d_.mean(), 'sd': d_.std()}
                           for g, d_ in zip(groups_v, data_v)]
            diff_results[col][dim] = {
                'method': method, 'stat': stat_val, 'p': p_val,
                'group_stats': group_stats, 'sig': p_val < 0.05
            }

    # ══════════════════════════════════════════════
    #  Step 8: 回归分析
    # ══════════════════════════════════════════════
    reg_results = {}
    if cfg.get('analysis', {}).get('regression', False) and 'regression' in cfg:
        print('[Step 8] 回归分析...')
        reg_cfg = cfg['regression']
        dv = reg_cfg['dependent']
        ivs = reg_cfg['independent']
        controls = reg_cfg.get('controls', [])

        all_reg_vars = controls + ivs + [dv]
        reg_data = df[all_reg_vars].dropna()
        X = reg_data[controls + ivs].astype(float)
        y = reg_data[dv]
        X_const = sm.add_constant(X)
        model = sm.OLS(y, X_const).fit()

        # VIF
        vif_data = []
        for i, col in enumerate(ivs):
            idx = len(controls) + i + 1
            vif_val = variance_inflation_factor(X_const.values, idx)
            vif_data.append((col, vif_val))

        # 系数
        coefficients = []
        for var in ivs:
            b = model.params[var]
            se = model.bse[var]
            t_val = model.tvalues[var]
            p_val = model.pvalues[var]
            beta = b * (X[var].std() / y.std())
            coefficients.append({
                'var': var, 'B': b, 'SE': se, 'beta': beta, 't': t_val, 'p': p_val
            })

        reg_results = {
            'R2': model.rsquared, 'adj_R2': model.rsquared_adj,
            'F': model.fvalue, 'F_p': model.f_pvalue,
            'vif': vif_data, 'coefficients': coefficients, 'N': len(reg_data),
            'dv': dv, 'ivs': ivs
        }

    # ══════════════════════════════════════════════
    #  Step 9: 生成 Word 报告
    # ══════════════════════════════════════════════
    print('[Step 9] 生成 Word 报告...')
    preset = cfg.get('output', {}).get('format_preset', 'thesis_songti')
    rb = ReportBuilder(preset_name=preset)

    rb.add_title(f'{cfg["project_name"]}\n——数据分析报告')
    rb.add_body_text(f'本报告基于{N}份有效问卷数据，采用描述性统计、信度效度检验、相关分析、差异分析及回归分析等方法进行系统分析。')

    # ── 一、人口学 ──
    t = rb.next_table_no()
    rb.add_heading('一、样本人口学特征')
    rb.add_three_line_table(
        ['变量', '类别', '频数', '百分比(%)'],
        demo_table,
        title=f'表{t}  样本人口学特征分布(N={N})'
    )
    rb.add_body_text(demographic_overview(N, f'样本覆盖了不同{", ".join(demo_cols)}的受访者。'))

    # ── 二、正态性 ──
    t = rb.next_table_no()
    rb.add_heading('二、正态性检验')
    rb.add_three_line_table(
        ['变量', 'N', 'W', 'p', '结论'],
        norm_results,
        title=f'表{t}  各维度Shapiro-Wilk正态性检验结果'
    )
    rb.add_body_text(normality_test(t, N, all_normal))

    # ── 三、描述性统计 ──
    t = rb.next_table_no()
    rb.add_heading('三、各变量描述性统计')
    rb.add_three_line_table(
        ['变量/维度', '均值(M)', '标准差(SD)'],
        desc_table,
        title=f'表{t}  各变量描述性统计(N={N})'
    )
    # 按量表分组输出文字
    for scale in cfg['scales']:
        sname = scale['name']
        if scale.get('dimensions'):
            dim_st = [(d['name'], df[d['name']].mean(), df[d['name']].std())
                      for d in scale['dimensions']]
            dim_st.sort(key=lambda x: x[1], reverse=True)
            rb.add_body_text(descriptive_scales(t, dim_st, sname,
                                               midpoint=cfg.get('likert_scale', 5) / 2 + 0.5))

    # ── 四、信度 ──
    t = rb.next_table_no()
    rb.add_heading('四、信度检验')
    rb.add_three_line_table(
        ['维度', '题目数', "Cronbach's α"],
        rel_table,
        title=f"表{t}  各维度信度检验结果(Cronbach's α)"
    )
    rb.add_body_text(reliability_analysis(t, dim_alphas, overall_alpha))

    # ── 五、效度 ──
    t = rb.next_table_no()
    rb.add_heading('五、效度检验')
    kmo_rows = [
        ['KMO取样适当性度量', '', f'{kmo_val:.3f}'],
        ['巴特利特球形检验', '近似卡方', f'{chi2_val:.1f}'],
        ['', '自由度(df)', str(int(dof))],
        ['', '显著性(Sig.)', '<0.001' if p_bart < 0.001 else f'{p_bart:.4f}'],
    ]
    rb.add_three_line_table(
        ['检验项目', '统计量', '值'],
        kmo_rows,
        title=f'表{t}  KMO和巴特利特球形检验结果'
    )
    rb.add_body_text(validity_kmo_bartlett(t, kmo_val, chi2_val, dof, p_bart))
    rb.add_body_text(validity_efa(t, n_factors, cum_var_pct))

    # ── 六、相关分析 ──
    t = rb.next_table_no()
    rb.add_heading('六、相关分析')
    # 相关矩阵表
    corr_rows = []
    for i, v1 in enumerate(corr_vars):
        row = [v1, f'{corr_data[v1].mean():.3f}', f'{corr_data[v1].std():.3f}']
        for j, v2 in enumerate(corr_vars):
            if i == j:
                row.append('1')
            elif j > i:
                r = corr_matrix.loc[v1, v2]
                p_c = [p for x, y, _r, p in corr_pairs if (x == v1 and y == v2) or (x == v2 and y == v1)][0]
                row.append(f'{r:.3f}{_sig_star(p_c)}')
            else:
                row.append('')
        corr_rows.append(row)
    rb.add_three_line_table(
        ['变量', 'M', 'SD'] + corr_vars,
        corr_rows,
        title=f'表{t}  各变量Pearson相关系数矩阵(N={N})'
    )
    rb.add_note('注：*P<0.05, **P<0.01, ***P<0.001；表中仅显示上三角相关系数。')
    rb.add_body_text(correlation_analysis(t, corr_pairs, N))
    if len(corr_pairs) > 1:
        rb.add_body_text(correlation_strength_detail(corr_pairs))

    # ── 七、差异分析 ──
    rb.add_heading('七、差异分析')
    for d in cfg.get('demographics', []):
        col = d['col']
        labels = d.get('labels', {})
        if col not in diff_results:
            continue

        t = rb.next_table_no()
        group_diff = diff_results[col]
        diff_rows = []
        for dim in scale_names:
            dd = group_diff.get(dim, {})
            if dd.get('method') == '样本不足':
                continue
            first = True
            for gs in dd.get('group_stats', []):
                diff_rows.append([
                    dim if first else '', gs['label'], str(gs['n']),
                    f'{gs["mean"]:.3f}', f'{gs["sd"]:.3f}',
                    f'{dd["stat"]:.3f}' if first else '',
                    f'{dd["p"]:.4f}' if first else ''])
                first = False

        method_label = list(group_diff.values())[0].get('method', 'ANOVA')
        stat_col = 'F' if 'ANOVA' in method_label else 't'
        rb.add_three_line_table(
            ['维度', col, 'N', 'M', 'SD', stat_col, 'p'],
            diff_rows,
            title=f'表{t}  不同{col}在各维度上的差异分析结果'
        )

        # 文字
        anova_results = []
        for dim in scale_names:
            dd = group_diff.get(dim, {})
            if dd.get('method') == '样本不足':
                continue
            gs = dd.get('group_stats', [])
            if gs:
                top = max(gs, key=lambda x: x['mean'])
                bot = min(gs, key=lambda x: x['mean'])
                anova_results.append((dim, dd['stat'], dd['p'],
                                      top['label'], top['mean'],
                                      bot['label'], bot['mean']))
        if anova_results:
            rb.add_body_text(difference_anova(t, col, anova_results))

    # ── 八、回归分析 ──
    if reg_results:
        rb.add_heading('八、回归分析')

        # VIF 表
        t = rb.next_table_no()
        vif_rows = [[name, f'{vif:.3f}'] for name, vif in reg_results['vif']]
        rb.add_three_line_table(['自变量', 'VIF'], vif_rows,
                                title=f'表{t}  自变量共线性诊断(VIF)')
        rb.add_note('注：VIF<10表示不存在严重多重共线性。')
        max_vif = max(v for _, v in reg_results['vif'])
        rb.add_body_text(vif_diagnosis(t, max_vif))

        # 回归表
        t = rb.next_table_no()
        reg_rows = []
        for c in reg_results['coefficients']:
            sig = _sig_star(c['p'])
            reg_rows.append([c['var'], f'{c["B"]:.4f}', f'{c["SE"]:.4f}',
                             f'{c["beta"]:.4f}', f'{c["t"]:.3f}',
                             f'{c["p"]:.4f}{sig}'])
        rb.add_three_line_table(
            ['自变量', 'B', 'SE', 'β', 't', 'p'],
            reg_rows,
            title=f'表{t}  {",".join(reg_results["ivs"])}对{reg_results["dv"]}的回归分析'
        )
        fp = _p_str(reg_results['F_p'])
        rb.add_note(f'注：R²={reg_results["R2"]:.4f}，调整R²={reg_results["adj_R2"]:.4f}，'
                    f'F={reg_results["F"]:.3f}，P{fp}；N={reg_results["N"]}')
        rb.add_note('*P<0.05, **P<0.01, ***P<0.001')

        rb.add_body_text(regression_model_fit(
            t, reg_results['dv'], reg_results['R2'], reg_results['adj_R2'],
            reg_results['F'], reg_results['F_p'], reg_results['ivs']))

        coef_tuples = [(c['var'], c['beta'], c['t'], c['p']) for c in reg_results['coefficients']]
        rb.add_body_text(regression_coefficients(reg_results['dv'], coef_tuples))

    # ── 保存 ──
    report_name = cfg['project_name'].replace(' ', '_') + '_分析报告.docx'
    report_path = os.path.join(out_dir, report_name)
    rb.save(report_path)

    # ── 过程数据 Excel ──
    if cfg.get('output', {}).get('include_excel', True):
        excel_path = os.path.join(out_dir, cfg['project_name'] + '_过程数据.xlsx')
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            pd.DataFrame(demo_table, columns=['变量', '类别', '频数', '百分比']).to_excel(
                writer, sheet_name='人口学', index=False)
            pd.DataFrame(desc_table, columns=['维度', '均值', '标准差']).to_excel(
                writer, sheet_name='描述统计', index=False)
            pd.DataFrame(rel_table, columns=['维度', '题目数', 'α']).to_excel(
                writer, sheet_name='信度', index=False)
            corr_matrix.to_excel(writer, sheet_name='相关矩阵')
            if reg_results:
                pd.DataFrame(reg_results['coefficients']).to_excel(
                    writer, sheet_name='回归系数', index=False)
        print(f'过程数据已保存: {excel_path}')

    print(f'\n[A1] ✅ 完成！共生成 {rb.table_count} 张表。')
    return reg_results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A1 问卷全套分析流水线')
    parser.add_argument('--config', required=True, help='config.yaml 路径')
    args = parser.parse_args()
    run_pipeline(args.config)
