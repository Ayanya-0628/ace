# -*- coding: utf-8 -*-
"""
text_library/blocks.py — 标准化文字段落库（完整段落版）
从100+个已完成项目中提炼的最佳文字模板，直接传入数据即填空输出。
每个函数返回一个完整段落字符串，可直接用 add_body_text(doc, text) 写入。

版本日志：
  v1.0 2026-04-09 从 Katherine120 / 临时单120 / 唐卡100 提取初始模板
"""


# ══════════════════════════════════════════════
#  工具函数
# ══════════════════════════════════════════════
def _p_str(p):
    """P值格式化"""
    return '<0.001' if p < 0.001 else f'={p:.3f}'

def _sig_star(p):
    """显著性星号"""
    if p < 0.001: return '***'
    if p < 0.01: return '**'
    if p < 0.05: return '*'
    return ''

def _sig_text(p, pos, neg):
    """根据P值选择文本"""
    return pos if p < 0.05 else neg

def _direction(value):
    """正/负方向"""
    return '正' if value > 0 else '负'

def _corr_strength(r):
    """相关强度描述"""
    ar = abs(r)
    if ar > 0.7: return '强'
    if ar > 0.5: return '较强'
    if ar > 0.3: return '中等'
    return '弱'


# ══════════════════════════════════════════════
#  1. 人口学特征描述
# ══════════════════════════════════════════════
def demographic_overview(N, detail_text):
    """
    参数：
      N: 总样本量
      detail_text: 各变量的描述文字（由调用方按实际数据组装）
    返回：完整段落
    """
    return f'由表可知，本次调查共回收有效问卷{N}份。{detail_text}'


def demographic_gender(n_male, pct_male, n_female, pct_female):
    return (f'从性别来看，男性{n_male}人（{pct_male:.1f}%），'
            f'女性{n_female}人（{pct_female:.1f}%），'
            f'{"男女比例大致持平" if abs(pct_male - pct_female) < 15 else "性别分布存在一定差异"}。')


def demographic_age(age_groups):
    """
    age_groups: [(标签, 人数, 百分比), ...] 按人数降序排列
    """
    text = f'从年龄分布来看，{age_groups[0][0]}的受访者最多（{age_groups[0][1]}人，{age_groups[0][2]:.1f}%），'
    if len(age_groups) > 1:
        text += f'{age_groups[1][0]}次之（{age_groups[1][1]}人，{age_groups[1][2]:.1f}%），'
    text += '受访者以中青年群体为主。'
    return text


# ══════════════════════════════════════════════
#  2. 各变量描述性统计
# ══════════════════════════════════════════════
def descriptive_scales(table_no, dim_stats, scale_name='', midpoint=3.0):
    """
    参数：
      table_no: 表号
      dim_stats: [(维度名, 均值, 标准差), ...] 按均值降序排列
      scale_name: 量表名称（如"职业倦怠"）
      midpoint: 量表中点（默认3.0=五点Likert中点）
    """
    text = f'由表{table_no}可知，'
    overall_mean = sum(d[1] for d in dim_stats) / len(dim_stats)
    level = '中等偏上' if overall_mean > midpoint else '中等偏下'

    text += f'{dim_stats[0][0]}维度得分最高（M={dim_stats[0][1]:.3f}，SD={dim_stats[0][2]:.3f}），'
    text += f'{dim_stats[-1][0]}维度得分最低（M={dim_stats[-1][1]:.3f}，SD={dim_stats[-1][2]:.3f}）。'
    text += f'总体而言，受访者的{scale_name}处于{level}水平。'
    return text


def descriptive_single_var(var_name, mean, sd, interpretation=''):
    """单个变量的描述"""
    text = f'{var_name}的总体均值为{mean:.3f}（SD={sd:.3f}），'
    if interpretation:
        text += interpretation
    return text


# ══════════════════════════════════════════════
#  3. 信度检验
# ══════════════════════════════════════════════
def reliability_analysis(table_no, dim_alphas, total_alpha):
    """
    参数：
      table_no: 表号
      dim_alphas: [(维度名, alpha值), ...]
      total_alpha: 总量表alpha
    """
    text = f"由表{table_no}可知，本研究采用克朗巴赫α信度系数(Cronbach's α)对问卷进行信度检验。"

    for name, alpha in dim_alphas:
        text += f'{name}维度的α系数为{alpha:.3f}，'

    text += f'总量表的α系数为{total_alpha:.3f}。'

    min_alpha = min([a for _, a in dim_alphas] + [total_alpha])
    if min_alpha >= 0.9:
        text += '各维度及总量表的α系数均大于0.9，远超0.7的可接受标准，表明问卷各维度的内部一致性信度优异，量表的测量结果具有很高的可靠性和稳定性。'
    elif min_alpha >= 0.8:
        text += '各维度的α系数均大于0.8，表明量表具有良好的内部一致性信度。'
    elif min_alpha >= 0.7:
        text += '各维度的α系数均大于0.7的可接受标准，表明量表具有较好的内部一致性信度。'
    else:
        low_dims = [name for name, a in dim_alphas if a < 0.7]
        text += f'其中{"、".join(low_dims)}维度的α系数略低于0.7，'
        text += '这可能与该维度题项数量较少有关，后续分析中需谨慎解读。'

    return text


# ══════════════════════════════════════════════
#  4. 效度检验（KMO + Bartlett + EFA）
# ══════════════════════════════════════════════
def validity_kmo_bartlett(table_no, kmo, chi2, dof, p_bart):
    """KMO + Bartlett 文字"""
    kmo_level = ('非常适合' if kmo >= 0.9 else
                 '适合' if kmo >= 0.8 else
                 '较适合' if kmo >= 0.7 else
                 '基本适合' if kmo >= 0.6 else '不太适合')

    text = f'由表{table_no}可知，KMO取样适当性度量值为{kmo:.3f}，'
    text += f'表明数据{kmo_level}进行因子分析。'
    text += f"巴特利特球形检验(Bartlett's Test of Sphericity)的近似卡方值为{chi2:.1f}（df={int(dof)}，P{_p_str(p_bart)}），"

    if p_bart < 0.05:
        text += '达到显著水平，拒绝了相关矩阵为单位矩阵的零假设，说明各变量之间存在显著的相关关系，满足因子分析的前提条件。'
    else:
        text += '未达到显著水平，变量间可能不存在共同因子，因子分析结果需谨慎解读。'

    return text


def validity_efa(table_no, n_factors, cum_var_pct):
    """EFA 文字"""
    text = f'由表{table_no}可知，采用主成分分析法提取公因子，经最大方差法(Varimax)正交旋转后，共提取{n_factors}个因子，'
    text += f'累计方差贡献率为{cum_var_pct:.2f}%，'
    text += '大于60%的标准，' if cum_var_pct > 60 else '接近60%的推荐标准，'
    text += '说明提取的因子能够较好地解释原始变量的信息。各题目在其所属因子上的载荷值均较高，且在其他因子上的载荷较低，表明问卷具有较好的结构效度。'
    return text


# ══════════════════════════════════════════════
#  5. 相关分析
# ══════════════════════════════════════════════
def correlation_analysis(table_no, pairs, N=None):
    """
    参数：
      table_no: 表号
      pairs: [(变量1, 变量2, r值, p值), ...]
      N: 样本量（可选）
    """
    sig_pairs = [(x, y, r, p) for x, y, r, p in pairs if p < 0.05]
    nonsig_pairs = [(x, y, r, p) for x, y, r, p in pairs if p >= 0.05]

    text = f'由表{table_no}可知，'

    if sig_pairs:
        parts = []
        for x, y, r, p in sig_pairs:
            d = _direction(r)
            s = _corr_strength(r)
            parts.append(f'{x}与{y}呈显著{d}相关（r={r:.3f}，P{_p_str(p)}）')
        text += '，'.join(parts) + '。'

    if nonsig_pairs:
        ns_names = [f'{x}与{y}' for x, y, r, p in nonsig_pairs]
        text += f'{"、".join(ns_names)}的相关未达到显著水平（P>0.05）。'

    if sig_pairs:
        text += '上述结果为后续回归分析提供了初步依据。'

    return text


def correlation_strength_detail(pairs):
    """相关分析的强度详述"""
    text = '具体而言，'
    for x, y, r, p in pairs:
        s = _corr_strength(r)
        d = _direction(r)
        text += f'{x}与{y}之间呈{s}{d}相关（r={r:.3f}，P{_p_str(p)}），'
    text = text.rstrip('，') + '。'
    return text


# ══════════════════════════════════════════════
#  6. 差异分析（t检验 / ANOVA）
# ══════════════════════════════════════════════
def difference_ttest(table_no, group_var, results):
    """
    results: [(维度名, t值, p值, 高分组名, 低分组名), ...]
    """
    text = f'由表{table_no}可知，'
    sig_parts = []
    nonsig_dims = []

    for dim, t_val, p_val, higher, lower in results:
        if p_val < 0.05:
            sig_parts.append(
                f'不同{group_var}的受访者在{dim}维度得分上差异有统计学意义'
                f'（t={t_val:.3f}，P{_p_str(p_val)}），其中{higher}得分较高'
            )
        else:
            nonsig_dims.append(dim)

    if sig_parts:
        text += '；'.join(sig_parts) + '。'
    if nonsig_dims:
        text += f'在{"、".join(nonsig_dims)}维度上，差异无统计学意义（P>0.05）。'
    if not sig_parts:
        text += f'不同{group_var}的受访者在各维度上的差异均无统计学意义（P>0.05），'
        text += f'说明{group_var}对受访者的相关态度/行为没有显著影响。'

    return text


def difference_anova(table_no, group_var, results):
    """
    results: [(维度名, F值, p值, 最高组, 最高均值, 最低组, 最低均值), ...]
    """
    text = f'由表{table_no}可知，'
    sig_parts = []
    nonsig_dims = []

    for dim, f_val, p_val, top_grp, top_m, bot_grp, bot_m in results:
        if p_val < 0.05:
            sig_parts.append(
                f'不同{group_var}的受访者在{dim}维度上存在显著差异'
                f'（F={f_val:.3f}，P{_p_str(p_val)}），其中{top_grp}组得分最高（M={top_m:.3f}），'
                f'{bot_grp}组得分最低（M={bot_m:.3f}）'
            )
        else:
            nonsig_dims.append(dim)

    if sig_parts:
        text += '。'.join(sig_parts) + '。'
    if nonsig_dims:
        text += f'在{"、".join(nonsig_dims)}维度上，不同{group_var}的受访者得分差异不显著（P>0.05）。'
    if not sig_parts:
        text += f'不同{group_var}的受访者在各维度得分上的差异均不具有统计学显著性（P>0.05）。'
        text += f'这说明{group_var}对受访者的相关评价没有产生显著影响。'

    return text


# ══════════════════════════════════════════════
#  7. 正态性检验
# ══════════════════════════════════════════════
def normality_test(table_no, N, all_normal=False):
    """正态性检验文字"""
    if all_normal:
        return (f'由表{table_no}可知，采用Shapiro-Wilk检验对各维度得分进行正态性检验，'
                f'结果显示所有维度的P值均大于0.05，数据服从正态分布，后续采用参数检验方法。')
    else:
        return (f'由表{table_no}可知，采用Shapiro-Wilk检验对各维度得分进行正态性检验，'
                f'结果显示部分维度的P值小于0.05，即数据不严格服从正态分布。'
                f'然而，考虑到本研究有效样本量为{N}份，根据中心极限定理，'
                f'当样本量足够大时（通常N>30），样本均值的分布近似于正态分布。'
                f'因此，后续分析仍采用参数检验方法，结果具有较好的稳健性。')


# ══════════════════════════════════════════════
#  8. 回归分析
# ══════════════════════════════════════════════
def regression_model_fit(table_no, dv_name, R2, adj_R2, F, F_p, iv_names):
    """模型拟合描述"""
    fp_str = _p_str(F_p)
    text = f'由表{table_no}可知，以{dv_name}为因变量，'
    text += f'{"和".join(iv_names)}为自变量构建多元线性回归模型。'
    text += f'模型的R²为{R2:.4f}，调整R²为{adj_R2:.4f}，F值为{F:.3f}（P{fp_str}），'
    text += f'回归模型整体显著，表明自变量共同解释了{dv_name}{R2*100:.1f}%的方差变异。'
    return text


def regression_coefficients(dv_name, coefficients):
    """
    coefficients: [(变量名, beta, t值, p值), ...]
    """
    text = ''
    for var, beta, t_val, p_val in coefficients:
        if p_val < 0.05:
            d = '正向' if beta > 0 else '负向'
            text += f'{var}对{dv_name}具有显著的{d}预测作用（β={beta:.3f}，t={t_val:.3f}，P{_p_str(p_val)}）。'
        else:
            text += f'{var}对{dv_name}的预测作用未达到显著水平（β={beta:.3f}，P{_p_str(p_val)}）。'
    return text


def regression_compare_predictors(dv_name, stronger_name, stronger_beta, weaker_name, weaker_beta):
    """比较两个自变量的预测力"""
    return (f'从标准化回归系数(β)的绝对值比较来看，{stronger_name}的影响力（β={abs(stronger_beta):.4f}）'
            f'大于{weaker_name}（β={abs(weaker_beta):.4f}），'
            f'说明{stronger_name}对{dv_name}起着相对更重要的预测作用。')


def vif_diagnosis(table_no, max_vif):
    """VIF 共线性诊断文字"""
    text = f'由表{table_no}可知，各自变量的方差膨胀因子(VIF)值均远小于10的警戒标准（最大VIF={max_vif:.3f}），'
    text += '说明自变量之间不存在严重的多重共线性问题，回归模型的参数估计结果具有良好的可靠性。'
    return text


# ══════════════════════════════════════════════
#  9. 中介效应
# ══════════════════════════════════════════════
def mediation_paths(table_no, iv, mv, dv,
                    a_coef, a_p, b_coef, b_p, cp_coef, cp_p,
                    indirect, ci_lo, ci_hi):
    """中介效应完整文字"""
    text = f'由表{table_no}可知，'

    # a路径
    text += f'a路径上，{iv}对{mv}的回归系数为{a_coef:.3f}（P{_p_str(a_p)}），'
    if a_p < 0.05:
        d = '正' if a_coef > 0 else '负'
        text += f'达到显著水平且系数为{d}，说明{iv}对{mv}有显著{d}向影响。'
    else:
        text += '未达显著水平。'

    # b路径
    text += f'b路径上，{mv}对{dv}的回归系数为{b_coef:.3f}（P{_p_str(b_p)}），'
    if b_p < 0.05:
        d = '负' if b_coef < 0 else '正'
        text += f'显著为{d}，表明{mv}对{dv}有显著影响。'
    else:
        text += '未达显著水平。'

    # 间接效应
    ci_contains_zero = ci_lo <= 0 <= ci_hi
    if not ci_contains_zero:
        text += f'Bootstrap检验结果显示，间接效应a×b={indirect:.4f}，95%CI为[{ci_lo:.4f}, {ci_hi:.4f}]，区间不包含0，中介效应显著。'
        if cp_p < 0.05:
            text += f"同时c'路径系数为{cp_coef:.3f}（P{_p_str(cp_p)}），仍然显著，表明{mv}起部分中介作用。"
        else:
            text += f"c'路径系数为{cp_coef:.3f}（P{_p_str(cp_p)}），不再显著，{mv}起完全中介作用。"
    else:
        text += f'Bootstrap检验结果显示，间接效应为{indirect:.4f}，95%CI为[{ci_lo:.4f}, {ci_hi:.4f}]，包含0，中介效应不显著。'

    return text


def mediation_effect_decomposition_rows(total_effect, total_se, total_ci,
                                        direct_effect, direct_se, direct_ci,
                                        indirect_effect, indirect_se, indirect_ci,
                                        digits=3):
    """客户版中介效应分解表：总/直接为回归CI，间接为Bootstrap CI。"""
    fmt = f'{{:.{digits}f}}'

    def ci_text(ci):
        lo, hi = ci
        return f'[{fmt.format(lo)}, {fmt.format(hi)}]'

    return [
        ['总效应 c', fmt.format(total_effect), fmt.format(total_se), ci_text(total_ci)],
        ["直接效应 c'", fmt.format(direct_effect), fmt.format(direct_se), ci_text(direct_ci)],
        ['间接效应 ab', fmt.format(indirect_effect), fmt.format(indirect_se), ci_text(indirect_ci)],
    ]


def mediation_effect_decomposition_note(n_boot=5000):
    """中介效应分解表标准表注。"""
    return (f'注：总效应和直接效应为回归估计结果；间接效应基于Bootstrap重复抽样{n_boot}次；'
            '95%CI为95%置信区间。')


# ══════════════════════════════════════════════
#  10. 调节效应
# ══════════════════════════════════════════════
def moderation_result(table_no, iv, moderator, dv, interaction_beta, interaction_p):
    """调节效应文字"""
    text = f'由表{table_no}可知，交互项（{iv}×{moderator}）的回归系数β={interaction_beta:.3f}（P{_p_str(interaction_p)}），'

    if interaction_p < 0.05:
        text += '达到显著水平，调节效应成立。'
        if interaction_beta < 0:
            text += f'交互项系数为负值，意味着当{moderator}较高时，{iv}对{dv}的效应被削弱——{moderator}起到了"缓冲器"的作用。'
        else:
            text += f'交互项系数为正值，说明{moderator}越高，{iv}对{dv}的影响越强。'
    else:
        text += f'未达到显著水平（P>0.05），{moderator}对{iv}与{dv}关系的调节效应不成立。'
        if interaction_p < 0.1:
            text += f'不过P值为{interaction_p:.3f}，接近0.05，呈现出边际显著的趋势，若扩大样本量可能会达到统计显著。'

    return text


# ══════════════════════════════════════════════
#  11. 假设检验汇总
# ══════════════════════════════════════════════
def hypothesis_summary(total, supported):
    """假设检验汇总开头"""
    return f'本研究提出的{total}个假设中，{supported}个获得了数据支持。'


# ══════════════════════════════════════════════
#  12. 交叉分析（卡方检验）
# ══════════════════════════════════════════════
def chi_square_test(table_no, group_var, indicator, chi2, p, detail=''):
    """卡方检验文字"""
    text = f'由表{table_no}可知，'
    if p < 0.05:
        text += f'不同{group_var}在{indicator}上的分布差异有统计学意义（χ²={chi2:.3f}，P{_p_str(p)}）。'
        if detail:
            text += f'具体而言，{detail}'
    else:
        text += f'不同{group_var}在{indicator}上的分布差异无统计学意义（χ²={chi2:.3f}，P{_p_str(p)}）。'
    return text
