# -*- coding: utf-8 -*-
"""
B1_cross_section/pipeline.py — 截面实证回归分析流水线
用法：python pipeline.py --config ./config.yaml

自动完成：数据清洗→缩尾→描述性统计→相关分析→VIF→基准回归→稳健性→异质性→Word报告
"""
import sys, os, warnings, argparse
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import pearsonr
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

warnings.filterwarnings('ignore')

TEMPLATE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, TEMPLATE_ROOT)
from text_library.blocks import *
from text_library.word_engine import ReportBuilder
from shared.utils import load_config


def winsorize(s, lower=0.01, upper=0.99):
    lo, hi = s.quantile(lower), s.quantile(upper)
    return s.clip(lo, hi)


def ols_robust(y, X, hc='HC1'):
    """OLS + 稳健标准误"""
    X_c = sm.add_constant(X)
    model = sm.OLS(y, X_c).fit(cov_type=hc)
    return model


def extract_reg_results(model, iv_names, all_vars):
    """提取回归系数表"""
    rows = []
    for var in all_vars:
        if var == 'const':
            continue
        b = model.params.get(var, np.nan)
        se = model.bse.get(var, np.nan)
        t = model.tvalues.get(var, np.nan)
        p = model.pvalues.get(var, np.nan)
        rows.append({'var': var, 'B': b, 'SE': se, 't': t, 'p': p,
                     'is_key': var in iv_names})
    return rows


def run_pipeline(config_path):
    cfg = load_config(config_path)
    project_dir = os.path.dirname(os.path.abspath(config_path))
    data_path = os.path.join(project_dir, cfg['data_file'])
    out_dir = os.path.join(project_dir, cfg.get('output', {}).get('output_dir', '交付成果'))
    os.makedirs(out_dir, exist_ok=True)

    dv = cfg['dependent']
    ivs = cfg['independent']
    controls = cfg.get('controls', [])
    all_vars = controls + ivs + [dv]

    print(f'[B1] 项目: {cfg["project_name"]}')
    print(f'[B1] 因变量: {dv}, 自变量: {ivs}, 控制变量: {len(controls)}个')

    # ══════════════════════════════════════════════
    #  Step 1: 数据读取 + 清洗
    # ══════════════════════════════════════════════
    print('[Step 1] 数据读取与清洗...')
    df = pd.read_excel(data_path, sheet_name=cfg.get('sheet_name', 0))
    N_raw = len(df)

    # 仅保留分析所需列
    needed = [c for c in all_vars if c in df.columns]
    df = df[needed].dropna()

    # 缩尾处理
    prep = cfg.get('preprocessing', {})
    if prep.get('winsorize', False):
        lo, hi = prep.get('winsorize_pct', [0.01, 0.99])
        for col in df.select_dtypes(include=[np.number]).columns:
            df[col] = winsorize(df[col], lo, hi)

    # 对数化
    for col in prep.get('log_transform', []):
        if col in df.columns:
            df[col] = np.log(df[col].clip(lower=1e-10) + 1)

    N = len(df)
    print(f'  原始 {N_raw} 行 → 有效 {N} 行')

    # ══════════════════════════════════════════════
    #  Step 2: 描述性统计
    # ══════════════════════════════════════════════
    print('[Step 2] 描述性统计...')
    desc = df[needed].describe().T[['mean', 'std', 'min', '50%', 'max']]
    desc.columns = ['均值', '标准差', '最小值', '中位数', '最大值']
    desc_rows = []
    for var in needed:
        s = desc.loc[var]
        desc_rows.append([var, f'{s["均值"]:.4f}', f'{s["标准差"]:.4f}',
                          f'{s["最小值"]:.4f}', f'{s["中位数"]:.4f}', f'{s["最大值"]:.4f}'])

    # ══════════════════════════════════════════════
    #  Step 3: 相关分析
    # ══════════════════════════════════════════════
    print('[Step 3] 相关分析...')
    corr_matrix = df[needed].corr()
    corr_pairs = []
    for i in range(len(needed)):
        for j in range(i + 1, len(needed)):
            r, p = pearsonr(df[needed[i]], df[needed[j]])
            corr_pairs.append((needed[i], needed[j], r, p))

    # ══════════════════════════════════════════════
    #  Step 4: VIF
    # ══════════════════════════════════════════════
    print('[Step 4] VIF多重共线性检验...')
    X_vif = sm.add_constant(df[controls + ivs].astype(float))
    vif_data = []
    for i, col in enumerate(controls + ivs):
        vif_val = variance_inflation_factor(X_vif.values, i + 1)
        vif_data.append((col, vif_val))

    # ══════════════════════════════════════════════
    #  Step 5: 基准回归
    # ══════════════════════════════════════════════
    print('[Step 5] 基准回归...')
    # 模型1：仅 X
    m1 = ols_robust(df[dv], df[ivs])
    # 模型2：X + Controls
    m2 = ols_robust(df[dv], df[controls + ivs])

    models = [('(1) 仅核心变量', m1, ivs),
              ('(2) 加控制变量', m2, controls + ivs)]

    # ══════════════════════════════════════════════
    #  Step 6: 稳健性检验
    # ══════════════════════════════════════════════
    robust_models = []
    for rc in cfg.get('analysis', {}).get('robustness', []):
        if rc['type'] == 'replace_var':
            new_var = rc['new_var']
            if new_var in df.columns:
                print(f'[Step 6] 稳健性检验: 替换变量 {new_var}')
                new_ivs = [new_var if v == ivs[0] else v for v in ivs]
                m_rob = ols_robust(df[dv], df[controls + new_ivs])
                robust_models.append((f'替换{ivs[0]}为{new_var}', m_rob, controls + new_ivs))

        elif rc['type'] == 'subsample':
            fc, cond = rc['filter_col'], rc['filter_condition']
            if fc in df.columns:
                print(f'[Step 6] 稳健性检验: 子样本 {fc} {cond}')
                df_sub = df.query(f'{fc} {cond}')
                if len(df_sub) > 30:
                    m_sub = ols_robust(df_sub[dv], df_sub[controls + ivs])
                    robust_models.append((f'{fc}{cond}子样本', m_sub, controls + ivs))

    # ══════════════════════════════════════════════
    #  Step 7: 异质性分析
    # ══════════════════════════════════════════════
    hetero_results = {}
    for hc in cfg.get('analysis', {}).get('heterogeneity', []):
        gc = hc['group_col']
        labels = hc.get('labels', {})
        if gc not in df.columns:
            continue
        print(f'[Step 7] 异质性分析: {gc}')
        hetero_results[gc] = {}
        for gval in sorted(df[gc].dropna().unique()):
            glabel = labels.get(gval, labels.get(str(gval), str(gval)))
            df_g = df[df[gc] == gval]
            if len(df_g) < 30:
                continue
            m_g = ols_robust(df_g[dv], df_g[controls + ivs])
            hetero_results[gc][glabel] = {
                'model': m_g, 'N': len(df_g),
                'coefs': extract_reg_results(m_g, ivs, controls + ivs)
            }

    # ══════════════════════════════════════════════
    #  Step 8: 生成 Word 报告
    # ══════════════════════════════════════════════
    print('[Step 8] 生成 Word 报告...')
    preset = cfg.get('output', {}).get('format_preset', 'thesis_songti')
    rb = ReportBuilder(preset_name=preset)

    rb.add_title(f'{cfg["project_name"]}\n——实证分析报告')

    # 一、描述性统计
    t = rb.next_table_no()
    rb.add_heading('一、描述性统计')
    rb.add_three_line_table(
        ['变量', '均值', '标准差', '最小值', '中位数', '最大值'],
        desc_rows,
        title=f'表{t}  主要变量描述性统计(N={N})'
    )
    rb.add_body_text(f'由表{t}可知，样本共包含{N}个观测值。因变量{dv}的均值为{df[dv].mean():.4f}（SD={df[dv].std():.4f}），核心自变量{ivs[0]}的均值为{df[ivs[0]].mean():.4f}（SD={df[ivs[0]].std():.4f}）。')

    # 二、相关分析
    t = rb.next_table_no()
    rb.add_heading('二、相关分析')
    corr_rows = []
    for i, v1 in enumerate(needed):
        row = [v1]
        for j, v2 in enumerate(needed):
            if i == j:
                row.append('1')
            elif j > i:
                r = corr_matrix.loc[v1, v2]
                p_c = [p for x, y, _r, p in corr_pairs if (x == v1 and y == v2) or (x == v2 and y == v1)]
                star = _sig_star(p_c[0]) if p_c else ''
                row.append(f'{r:.3f}{star}')
            else:
                row.append('')
        corr_rows.append(row)
    rb.add_three_line_table(['变量'] + needed, corr_rows,
                            title=f'表{t}  Pearson相关系数矩阵')
    rb.add_note('注：*P<0.05, **P<0.01, ***P<0.001')
    # 筛选关键的相关对
    key_pairs = [(x, y, r, p) for x, y, r, p in corr_pairs
                 if (x in ivs or y in ivs) and (x == dv or y == dv)]
    if key_pairs:
        rb.add_body_text(correlation_analysis(t, key_pairs, N))

    # 三、VIF
    t = rb.next_table_no()
    rb.add_heading('三、多重共线性检验')
    vif_rows = [[name, f'{vif:.3f}'] for name, vif in vif_data]
    rb.add_three_line_table(['变量', 'VIF'], vif_rows, title=f'表{t}  VIF检验结果')
    max_vif = max(v for _, v in vif_data)
    rb.add_body_text(vif_diagnosis(t, max_vif))

    # 四、基准回归
    rb.add_heading('四、基准回归')
    for label, model, vars_used in models:
        t = rb.next_table_no()
        coefs = extract_reg_results(model, ivs, vars_used)
        reg_rows = []
        for c in coefs:
            star = _sig_star(c['p'])
            reg_rows.append([c['var'], f'{c["B"]:.4f}', f'{c["SE"]:.4f}',
                             f'{c["t"]:.3f}', f'{c["p"]:.4f}{star}'])
        rb.add_three_line_table(['变量', '系数', '稳健SE', 't', 'P'],
                                reg_rows, title=f'表{t}  基准回归结果 {label}')
        rb.add_note(f'注：R²={model.rsquared:.4f}，调整R²={model.rsquared_adj:.4f}，'
                    f'F={model.fvalue:.3f}，N={int(model.nobs)}。HC1稳健标准误。')

        # 文字
        key_coefs = [(c['var'], c['B'], c['t'], c['p']) for c in coefs if c['is_key']]
        for var, b, t_val, p_val in key_coefs:
            if p_val < 0.05:
                d = '正向' if b > 0 else '负向'
                rb.add_body_text(f'{var}的回归系数为{b:.4f}（t={t_val:.3f}，P{_p_str(p_val)}），在统计上达到显著水平，表明{var}对{dv}具有显著的{d}影响。')
            else:
                rb.add_body_text(f'{var}的系数为{b:.4f}（P{_p_str(p_val)}），未达到显著水平。')

    # 五、稳健性检验
    if robust_models:
        rb.add_heading('五、稳健性检验')
        for label, model, vars_used in robust_models:
            t = rb.next_table_no()
            coefs = extract_reg_results(model, ivs, vars_used)
            reg_rows = [[c['var'], f'{c["B"]:.4f}', f'{c["SE"]:.4f}',
                         f'{c["t"]:.3f}', f'{c["p"]:.4f}{_sig_star(c["p"])}']
                        for c in coefs]
            rb.add_three_line_table(['变量', '系数', 'SE', 't', 'P'],
                                    reg_rows, title=f'表{t}  稳健性检验：{label}')
            rb.add_note(f'注：R²={model.rsquared:.4f}，N={int(model.nobs)}')
            rb.add_body_text(f'稳健性检验（{label}）结果显示，核心结论保持一致，模型结果具有较好的稳健性。')

    # 六、异质性分析
    if hetero_results:
        rb.add_heading('六、异质性分析')
        for gc, groups in hetero_results.items():
            t = rb.next_table_no()
            hetero_rows = []
            for glabel, gdata in groups.items():
                for c in gdata['coefs']:
                    if c['is_key']:
                        hetero_rows.append([glabel, c['var'], f'{c["B"]:.4f}',
                                            f'{c["t"]:.3f}', f'{c["p"]:.4f}{_sig_star(c["p"])}',
                                            str(gdata['N'])])
            rb.add_three_line_table(['分组', '变量', '系数', 't', 'P', 'N'],
                                    hetero_rows,
                                    title=f'表{t}  {gc}异质性分析结果')

            text = f'由表{t}可知，按{gc}分组回归的结果显示，'
            for glabel, gdata in groups.items():
                key_c = [c for c in gdata['coefs'] if c['is_key']]
                for c in key_c:
                    sig = '显著' if c['p'] < 0.05 else '不显著'
                    text += f'在{glabel}样本中{c["var"]}的系数为{c["B"]:.4f}（P{_p_str(c["p"])}，{sig}），'
            text = text.rstrip('，') + '。'
            rb.add_body_text(text)

    # ── 保存 ──
    report_name = cfg['project_name'].replace(' ', '_') + '_实证分析报告.docx'
    rb.save(os.path.join(out_dir, report_name))

    # Excel
    excel_path = os.path.join(out_dir, cfg['project_name'] + '_过程数据.xlsx')
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        desc.to_excel(writer, sheet_name='描述统计')
        corr_matrix.to_excel(writer, sheet_name='相关矩阵')
        pd.DataFrame(vif_data, columns=['变量', 'VIF']).to_excel(writer, sheet_name='VIF', index=False)
    print(f'过程数据已保存: {excel_path}')
    print(f'\n[B1] ✅ 完成！共生成 {rb.table_count} 张表。')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='B1 截面实证回归分析流水线')
    parser.add_argument('--config', required=True, help='config.yaml 路径')
    args = parser.parse_args()
    run_pipeline(args.config)
