# -*- coding: utf-8 -*-
# ace 代码库: meta_analysis.py
# 从 SKILL.md 提取的可复用代码模板
# 使用时复制对应函数/代码段，替换变量名即可

# ══════ 效应量提取与计算 ══════
import numpy as np

# ── 连续型结局：标准化均数差 SMD (Hedges' g) ──
def hedges_g(m1, sd1, n1, m2, sd2, n2):
    pooled_sd = np.sqrt(((n1-1)*sd1**2 + (n2-1)*sd2**2) / (n1+n2-2))
    d = (m1 - m2) / pooled_sd
    j = 1 - 3 / (4*(n1+n2-2) - 1)  # 小样本校正
    g = d * j
    se = np.sqrt((n1+n2)/(n1*n2) + g**2/(2*(n1+n2)))
    return g, se

# ── 二分类结局：OR / RR ──
# 直接从文献提取 OR + 95%CI，转换为 lnOR ± SE
def or_to_lnor(or_val, ci_lower, ci_upper):
    lnor = np.log(or_val)
    se = (np.log(ci_upper) - np.log(ci_lower)) / (2 * 1.96)
    return lnor, se

# ── HR（生存分析）──
# 同理：lnHR ± SE

# ══════ 固定/随机效应模型合成 ══════
def meta_analysis(effects, se_list, model='random'):
    """
    effects: list of effect sizes (lnOR, SMD, etc.)
    se_list: list of standard errors
    model: 'fixed' or 'random'
    """
    effects = np.array(effects)
    variances = np.array(se_list) ** 2
    weights_fixed = 1 / variances

    # 固定效应
    pooled_fixed = np.sum(weights_fixed * effects) / np.sum(weights_fixed)

    # Q 统计量（异质性）
    Q = np.sum(weights_fixed * (effects - pooled_fixed) ** 2)
    df = len(effects) - 1
    I2 = max(0, (Q - df) / Q * 100)  # I² 百分比

    if model == 'random':
        # DerSimonian-Laird 方法估计 τ²
        C = np.sum(weights_fixed) - np.sum(weights_fixed**2) / np.sum(weights_fixed)
        tau2 = max(0, (Q - df) / C)
        weights_random = 1 / (variances + tau2)
        pooled = np.sum(weights_random * effects) / np.sum(weights_random)
        se_pooled = np.sqrt(1 / np.sum(weights_random))
    else:
        pooled = pooled_fixed
        se_pooled = np.sqrt(1 / np.sum(weights_fixed))

    ci_lower = pooled - 1.96 * se_pooled
    ci_upper = pooled + 1.96 * se_pooled

    return {
        'pooled_effect': pooled,
        'se': se_pooled,
        'ci_lower': ci_lower,
        'ci_upper': ci_upper,
        'Q': Q,
        'I2': I2,
        'p_heterogeneity': 1 - stats.chi2.cdf(Q, df),
    }

# ══════ 森林图模板 ══════
def forest_plot(studies, effects, ci_lower, ci_upper, pooled_result, ylabel='OR'):
    """简易森林图"""
    fig, ax = plt.subplots(figsize=(5.5, 0.35 * len(studies) + 1.5))
    y_pos = np.arange(len(studies))

    # 各研究
    ax.errorbar(effects, y_pos, xerr=[np.array(effects)-np.array(ci_lower),
                np.array(ci_upper)-np.array(effects)],
                fmt='s', color='#4C72B0', markersize=6, capsize=3, linewidth=1.2)

    # 合并效应（菱形）
    ax.errorbar(pooled_result['pooled_effect'], -1,
                xerr=[[pooled_result['pooled_effect']-pooled_result['ci_lower']],
                      [pooled_result['ci_upper']-pooled_result['pooled_effect']]],
                fmt='D', color='#C44E52', markersize=8, capsize=4, linewidth=1.5)

    # 无效线
    ax.axvline(x=0 if 'SMD' in ylabel else 1, color='gray', linestyle='--', linewidth=0.8)

    ax.set_yticks(list(y_pos) + [-1])
    ax.set_yticklabels(list(studies) + ['合并效应'])
    ax.set_xlabel(ylabel)
    ax.invert_yaxis()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    return fig, ax

# ══════ 亚组分析框架 ══════
# 按亚组标签分别做 meta_analysis
for subgroup in df['subgroup'].unique():
    sub = df[df['subgroup'] == subgroup]
    result = meta_analysis(sub['effect'].tolist(), sub['se'].tolist())
    print(f'{subgroup}: pooled={result["pooled_effect"]:.3f}, '
          f'I²={result["I2"]:.1f}%, p={result["p_heterogeneity"]:.4f}')

# ══════ 频率分析（单选题） ══════
def freq_analysis(data, var, labels_dict, n=None):
    """频率分析，返回 [(标签, 计数, 百分比), ...]"""
    if n is None:
        n = len(data)
    counts = data[var].value_counts()
    result = []
    for val, label in labels_dict.items():
        cnt = int(counts.get(val, 0))
        pct = cnt / n * 100
        result.append((label, cnt, pct))
    return result

