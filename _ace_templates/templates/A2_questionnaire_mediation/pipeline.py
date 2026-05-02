# -*- coding: utf-8 -*-
"""
A2_questionnaire_mediation/pipeline.py — 问卷 + 中介/调节效应分析流水线
在 A1 基础上增加：中介效应（Bootstrap）、调节效应（交互项）

用法：python pipeline.py --config ./config.yaml
"""
import sys, os, warnings, argparse
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import pearsonr, shapiro
import statsmodels.api as sm

warnings.filterwarnings('ignore')

TEMPLATE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, TEMPLATE_ROOT)
from text_library.blocks import *
from text_library.word_engine import ReportBuilder
from shared.utils import load_config, cronbach_alpha, load_and_clean, compute_dimension_scores


def bootstrap_mediation(df, iv, mv, dv, controls=None, n_boot=5000, seed=42):
    """Bootstrap 中介效应检验"""
    np.random.seed(seed)
    N = len(df)
    ctrl = controls or []

    # a 路径: IV -> MV
    Xa = sm.add_constant(df[ctrl + [iv]].astype(float))
    ma = sm.OLS(df[mv], Xa).fit()
    a_coef = ma.params[iv]
    a_p = ma.pvalues[iv]

    # b + c' 路径: IV + MV -> DV
    Xbc = sm.add_constant(df[ctrl + [iv, mv]].astype(float))
    mbc = sm.OLS(df[dv], Xbc).fit()
    b_coef = mbc.params[mv]
    b_p = mbc.pvalues[mv]
    cp_coef = mbc.params[iv]
    cp_p = mbc.pvalues[iv]

    # 总效应 c: IV -> DV
    Xc = sm.add_constant(df[ctrl + [iv]].astype(float))
    mc = sm.OLS(df[dv], Xc).fit()
    c_coef = mc.params[iv]
    c_p = mc.pvalues[iv]
    c_ci = mc.conf_int(alpha=0.05).loc[iv]
    cp_ci = mbc.conf_int(alpha=0.05).loc[iv]

    # Bootstrap
    boot_indirect = []
    for _ in range(n_boot):
        idx = np.random.choice(N, N, replace=True)
        db = df.iloc[idx]
        try:
            _Xa = sm.add_constant(db[ctrl + [iv]].astype(float))
            _ma = sm.OLS(db[mv], _Xa).fit()
            _Xbc = sm.add_constant(db[ctrl + [iv, mv]].astype(float))
            _mbc = sm.OLS(db[dv], _Xbc).fit()
            boot_indirect.append(_ma.params[iv] * _mbc.params[mv])
        except Exception:
            pass

    indirect = a_coef * b_coef
    indirect_se = np.std(boot_indirect, ddof=1)
    ci_lo = np.percentile(boot_indirect, 2.5)
    ci_hi = np.percentile(boot_indirect, 97.5)
    # BCA 修正
    try:
        z0 = stats.norm.ppf(np.mean(np.array(boot_indirect) < indirect))
        bca_lo = np.percentile(boot_indirect, stats.norm.cdf(2 * z0 + stats.norm.ppf(0.025)) * 100)
        bca_hi = np.percentile(boot_indirect, stats.norm.cdf(2 * z0 + stats.norm.ppf(0.975)) * 100)
    except:
        bca_lo, bca_hi = ci_lo, ci_hi

    return {
        'a': a_coef, 'a_p': a_p, 'a_t': ma.tvalues[iv],
        'b': b_coef, 'b_p': b_p, 'b_t': mbc.tvalues[mv],
        'cp': cp_coef, 'cp_p': cp_p, 'cp_t': mbc.tvalues[iv],
        'cp_se': mbc.bse[iv], 'cp_ci_lo': cp_ci[0], 'cp_ci_hi': cp_ci[1],
        'c': c_coef, 'c_p': c_p, 'c_se': mc.bse[iv],
        'c_ci_lo': c_ci[0], 'c_ci_hi': c_ci[1],
        'indirect': indirect, 'indirect_se': indirect_se,
        'ci_lo': ci_lo, 'ci_hi': ci_hi,
        'bca_lo': bca_lo, 'bca_hi': bca_hi,
        'sig': not (ci_lo <= 0 <= ci_hi),
        'partial': cp_p < 0.05,
    }


def moderation_test(df, iv, moderator, dv, controls=None):
    """调节效应检验（交互项）"""
    ctrl = controls or []
    df = df.copy()
    df['_X_c'] = df[iv] - df[iv].mean()
    df['_W_c'] = df[moderator] - df[moderator].mean()
    df['_XW'] = df['_X_c'] * df['_W_c']

    X = sm.add_constant(df[ctrl + ['_X_c', '_W_c', '_XW']].astype(float))
    model = sm.OLS(df[dv], X).fit()

    return {
        'interaction_beta': model.params['_XW'],
        'interaction_p': model.pvalues['_XW'],
        'interaction_t': model.tvalues['_XW'],
        'R2': model.rsquared,
        'model': model,
    }


def run_pipeline(config_path):
    cfg = load_config(config_path)
    project_dir = os.path.dirname(os.path.abspath(config_path))
    out_dir = os.path.join(project_dir, cfg.get('output', {}).get('output_dir', '交付成果'))
    os.makedirs(out_dir, exist_ok=True)

    print(f'[A2] 项目: {cfg["project_name"]}')

    # ── 数据读取 + 变量计算（使用 shared.utils）──
    df, N_raw, N, all_item_cols, demo_cols = load_and_clean(cfg, project_dir)
    dim_cols_map, scale_dims, all_dim_names, scale_names = compute_dimension_scores(df, cfg)

    ctrl_vars = cfg.get('regression', {}).get('controls', demo_cols)

    # ── 生成报告（A1基础部分省略，直接上中介/调节） ──
    preset = cfg.get('output', {}).get('format_preset', 'thesis_songti')
    rb = ReportBuilder(preset_name=preset)
    rb.add_title(f'{cfg["project_name"]}\n——数据分析报告')
    rb.add_body_text(f'本报告基于{N}份有效样本，系统检验各变量间的关系，重点分析中介效应和调节效应。')

    # ═══ 基础分析（信度、效度、描述统计、相关、差异、回归 —— 复用文字模板） ═══
    # 信度
    t = rb.next_table_no()
    rb.add_heading('一、信度检验')
    dim_alphas = []
    rel_rows = []
    for scale in cfg['scales']:
        a = cronbach_alpha(df[scale['items']])
        rel_rows.append([scale['name'], str(len(scale['items'])), f'{a:.3f}'])
        dim_alphas.append((scale['name'], a))
    overall_a = cronbach_alpha(df[all_item_cols])
    rb.add_three_line_table(['变量', '题项数', "Cronbach's α"], rel_rows,
                            title=f"表{t}  信度检验结果")
    rb.add_body_text(reliability_analysis(t, dim_alphas, overall_a))

    # 描述统计
    t = rb.next_table_no()
    rb.add_heading('二、描述性统计')
    desc_rows = [[v, f'{df[v].mean():.3f}', f'{df[v].std():.3f}'] for v in scale_names]
    rb.add_three_line_table(['变量', 'M', 'SD'], desc_rows, title=f'表{t}  描述性统计')

    # 相关分析
    t = rb.next_table_no()
    rb.add_heading('三、相关分析')
    corr_pairs = []
    for i in range(len(scale_names)):
        for j in range(i + 1, len(scale_names)):
            r, p = pearsonr(df[scale_names[i]], df[scale_names[j]])
            corr_pairs.append((scale_names[i], scale_names[j], r, p))
    rb.add_body_text(correlation_analysis(t, corr_pairs, N))

    # ═══ 回归分析 ═══
    reg_cfg = cfg.get('regression', {})
    if reg_cfg:
        t = rb.next_table_no()
        rb.add_heading('四、回归分析')
        dv = reg_cfg['dependent']
        ivs = reg_cfg['independent']
        X = sm.add_constant(df[ctrl_vars + ivs].astype(float))
        model = sm.OLS(df[dv], X).fit()
        reg_rows = []
        for var in ivs:
            b, se, tv, pv = model.params[var], model.bse[var], model.tvalues[var], model.pvalues[var]
            beta = b * (df[var].std() / df[dv].std())
            reg_rows.append([var, f'{b:.4f}', f'{se:.4f}', f'{beta:.4f}',
                             f'{tv:.3f}', f'{pv:.4f}{_sig_star(pv)}'])
        rb.add_three_line_table(['变量', 'B', 'SE', 'β', 't', 'P'], reg_rows,
                                title=f'表{t}  回归分析结果')
        rb.add_note(f'注：R²={model.rsquared:.4f}，F={model.fvalue:.3f}，N={N}')
        rb.add_body_text(regression_model_fit(t, dv, model.rsquared, model.rsquared_adj,
                                             model.fvalue, model.f_pvalue, ivs))

    # ═══ 中介效应 ═══
    med_cfgs = [h for h in cfg.get('hypotheses', []) if h.get('type') == 'mediation']
    if med_cfgs:
        rb.add_heading('五、中介效应检验')
        rb.add_body_text('采用逐步回归法与Bootstrap重复抽样法检验中介效应，其中总效应和直接效应采用回归估计，间接效应采用Bootstrap重复抽样5000次估计置信区间。')
        for h in med_cfgs:
            t = rb.next_table_no()
            iv, mv, dv = h['iv'], h['mv'], h['dv']
            print(f'[中介] {iv} → {mv} → {dv}')

            med = bootstrap_mediation(df, iv, mv, dv, controls=ctrl_vars)

            med_rows = mediation_effect_decomposition_rows(
                med['c'], med['c_se'], (med['c_ci_lo'], med['c_ci_hi']),
                med['cp'], med['cp_se'], (med['cp_ci_lo'], med['cp_ci_hi']),
                med['indirect'], med['indirect_se'], (med['ci_lo'], med['ci_hi']))
            rb.add_three_line_table(['效应', 'Effect', 'SE', '95%CI'], med_rows,
                                    title=f'表{t}  效应分解与Bootstrap检验（{iv}→{mv}→{dv}）')
            rb.add_note(mediation_effect_decomposition_note(5000))

            rb.add_body_text(mediation_paths(
                t, iv, mv, dv,
                med['a'], med['a_p'], med['b'], med['b_p'],
                med['cp'], med['cp_p'],
                med['indirect'], med['ci_lo'], med['ci_hi']))

    # ═══ 调节效应 ═══
    mod_cfgs = [h for h in cfg.get('hypotheses', []) if h.get('type') == 'moderation']
    if mod_cfgs:
        rb.add_heading('六、调节效应检验')
        rb.add_body_text('将自变量和调节变量均进行均值中心化处理，构建交互项纳入回归模型。')
        for h in mod_cfgs:
            t = rb.next_table_no()
            iv, mod_var, dv = h['iv'], h['moderator'], h['dv']
            print(f'[调节] {iv} × {mod_var} → {dv}')

            mod = moderation_test(df, iv, mod_var, dv, controls=ctrl_vars)
            mod_rows = [
                [iv, f'{mod["model"].params["_X_c"]:.3f}',
                 f'{mod["model"].tvalues["_X_c"]:.2f}',
                 f'{mod["model"].pvalues["_X_c"]:.4f}'],
                [mod_var, f'{mod["model"].params["_W_c"]:.3f}',
                 f'{mod["model"].tvalues["_W_c"]:.2f}',
                 f'{mod["model"].pvalues["_W_c"]:.4f}'],
                [f'{iv}×{mod_var}', f'{mod["interaction_beta"]:.3f}',
                 f'{mod["interaction_t"]:.2f}',
                 f'{mod["interaction_p"]:.4f}'],
            ]
            rb.add_three_line_table(['变量', 'β', 't', 'P'], mod_rows,
                                    title=f'表{t}  {mod_var}对{iv}与{dv}关系的调节效应')
            rb.add_note(f'注：已均值中心化，R²={mod["R2"]:.4f}')
            rb.add_body_text(moderation_result(t, iv, mod_var, dv,
                                              mod['interaction_beta'],
                                              mod['interaction_p']))

    # ═══ 假设汇总 ═══
    if cfg.get('hypotheses'):
        t = rb.next_table_no()
        rb.add_heading('七、假设检验结果汇总')
        hyp_rows = []
        for h in cfg['hypotheses']:
            label = h.get('H1', h.get('H2', h.get('H3', h.get('H4', '假设'))))
            hyp_rows.append([label, h.get(label, ''), '待确认'])
        rb.add_three_line_table(['假设编号', '内容', '结论'], hyp_rows,
                                title=f'表{t}  假设检验结果汇总')

    # ── 保存 ──
    report_name = cfg['project_name'].replace(' ', '_') + '_分析报告.docx'
    rb.save(os.path.join(out_dir, report_name))
    print(f'\n[A2] ✅ 完成！共生成 {rb.table_count} 张表。')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A2 问卷+中介/调节效应分析流水线')
    parser.add_argument('--config', required=True, help='config.yaml 路径')
    args = parser.parse_args()
    run_pipeline(args.config)
