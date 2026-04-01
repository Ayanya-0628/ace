# 标准化文字分析句式模板

> **使用规则**：生成 Word 报告文字分析时，必须使用以下句式骨架，动态填入数据。
> 所有统计结论必须用 `if p < 0.05` 动态判断，严禁硬编码"显著"。

## 工具函数（每个脚本顶部必定义）

```python
def _p_str(p):
    """格式化P值"""
    return '<0.001' if p < 0.001 else f'={p:.3f}'

def _sig_text(p, positive_text, negative_text):
    """根据P值动态判断显著性描述"""
    return positive_text if p < 0.05 else negative_text
```

---

## 1. 人口学特征表

```python
text = (
    f'由表{t}可知，本研究共纳入{N}名受访者。'
    f'其中，男性{n_male}名（{pct_male:.1f}%），女性{n_female}名（{pct_female:.1f}%）；'
    f'年龄以{age_max_group}为主（{age_max_pct:.1f}%）；'
    f'学历分布方面，{edu_max_group}占{edu_max_pct:.1f}%。'
)
```

## 2. 各变量描述性统计表

```python
text = (
    f'由表{t}可知，各变量的描述性统计结果显示：'
    f'{var_highest}维度得分最高（M={m_high:.2f}，SD={sd_high:.2f}），'
    f'{var_lowest}维度得分最低（M={m_low:.2f}，SD={sd_low:.2f}）。'
    f'总体而言，受访者的{scale_name}处于{level}水平。'
)
# level 根据均值/量表中点动态判断：>中点="中等偏上"，<中点="中等偏下"
```

## 3. 信度检验表

```python
text = (
    f'由表{t}可知，量表总体{g("Cronbach\'s α")}为{total_alpha:.3f}，'
    f'各维度的α系数介于{alpha_min:.3f}~{alpha_max:.3f}之间，'
)
if alpha_min >= 0.8:
    text += '均大于0.8，表明量表具有良好的内部一致性信度。'
elif alpha_min >= 0.7:
    text += '均大于0.7的可接受标准，表明量表具有较好的内部一致性信度。'
else:
    text += f'其中{low_dim}维度α系数为{low_alpha:.3f}，略低于0.7，建议谨慎解读该维度结果。'
```

## 4. 效度检验表（KMO + Bartlett + EFA）

```python
text = (
    f'由表{t}可知，{g("KMO")}为{kmo:.3f}，'
)
if kmo >= 0.8:
    text += '大于0.8，适合进行因子分析；'
elif kmo >= 0.6:
    text += '大于0.6，基本适合进行因子分析；'
else:
    text += '低于0.6，因子分析结果需谨慎解读；'

text += (
    f'{g("Bartlett")}结果显示χ²={bartlett_chi2:.1f}，P{_p_str(bartlett_p)}，'
)
if bartlett_p < 0.05:
    text += '达到显著水平，表明变量间存在共同因子，适合进行因子分析。'
else:
    text += '未达到显著水平，变量间可能不存在共同因子。'

text += (
    f'采用主成分分析法提取公因子，经最大方差旋转后共提取{n_factors}个因子，'
    f'累计方差解释率为{var_explained:.2f}%。'
)
```

## 5. 相关分析表

```python
# 筛选显著和不显著的变量对
sig_pairs = [(x, y, r, p) for x, y, r, p in all_pairs if p < 0.05]
nonsig_pairs = [(x, y, r, p) for x, y, r, p in all_pairs if p >= 0.05]

text = f'由表{t}可知，'
for i, (x, y, r, p) in enumerate(sig_pairs):
    direction = '正' if r > 0 else '负'
    if i == 0:
        text += f'{x}与{y}呈显著{direction}相关（r={r:.3f}，P{_p_str(p)}）'
    else:
        text += f'，{x}与{y}呈显著{direction}相关（r={r:.3f}，P{_p_str(p)}）'

if nonsig_pairs:
    text += f'。{nonsig_pairs[0][0]}与{nonsig_pairs[0][1]}的相关未达到显著水平（P>0.05）'

text += '。上述结果为后续回归分析提供了初步依据。'
```

## 6. 差异分析表（独立样本t检验）

```python
text = f'由表{t}可知，'
sig_dims = []
nonsig_dims = []
for dim, t_val, p_val, m1, sd1, m2, sd2 in results:
    if p_val < 0.05:
        higher = group1_name if m1 > m2 else group2_name
        sig_dims.append(
            f'不同{group_var}的受访者在{dim}维度得分上差异有统计学意义'
            f'（t={t_val:.3f}，P{_p_str(p_val)}），'
            f'其中{higher}得分较高'
        )
    else:
        nonsig_dims.append(dim)

text += '；'.join(sig_dims) + '。'
if nonsig_dims:
    text += f'在{"、".join(nonsig_dims)}维度上，差异无统计学意义（P>0.05）。'
```

## 7. 差异分析表（单因素ANOVA）

```python
text = f'由表{t}可知，'
for dim, f_val, p_val, post_hoc_text in results:
    if p_val < 0.05:
        text += (
            f'不同{group_var}的受访者在{dim}维度得分上差异有统计学意义'
            f'（F={f_val:.3f}，P{_p_str(p_val)}）。'
            f'经事后多重比较发现，{post_hoc_text}。'
        )
    else:
        text += f'{dim}维度在不同{group_var}间差异无统计学意义（F={f_val:.3f}，P{_p_str(p_val)}）。'
```

## 8. 回归分析表

```python
text = f'由表{t}可知，'
text += f'模型的调整R²为{adj_r2:.3f}，解释了因变量{adj_r2*100:.1f}%的方差。'
for var, beta, p_val in predictors:
    if p_val < 0.05:
        direction = '正向' if beta > 0 else '负向'
        text += f'{var}对{dv_name}有显著{direction}预测作用（β={beta:.3f}，P{_p_str(p_val)}），'
    else:
        text += f'{var}对{dv_name}的预测作用未达到显著水平（β={beta:.3f}，P{_p_str(p_val)}），'
```

## 9. 中介效应表

```python
text = f'由表{t}可知，'
# a路径
if p_a < 0.05:
    text += f'{iv}对{mv}的正向预测作用显著（a={coef_a:.3f}，P{_p_str(p_a)}），'
else:
    text += f'{iv}对{mv}的预测作用未达显著水平（a={coef_a:.3f}，P{_p_str(p_a)}），'

# b路径
if p_b < 0.05:
    text += f'{mv}对{dv}的正向预测作用显著（b={coef_b:.3f}，P{_p_str(p_b)}）。'
else:
    text += f'{mv}对{dv}的预测作用未达显著水平（b={coef_b:.3f}，P{_p_str(p_b)}）。'

# 间接效应
if ci_lower > 0 or ci_upper < 0:  # CI不含0
    text += (
        f'{g("Bootstrap")}检验结果显示，'
        f'{iv}通过{mv}对{dv}的间接效应为{indirect:.3f}，'
        f'95%置信区间为[{ci_lower:.3f}, {ci_upper:.3f}]，不包含0，'
        f'表明中介效应显著。'
    )
    if p_c_prime < 0.05:
        text += f'直接效应仍然显著（c\'={c_prime:.3f}，P{_p_str(p_c_prime)}），属于部分中介。'
    else:
        text += f'直接效应不显著（c\'={c_prime:.3f}，P{_p_str(p_c_prime)}），属于完全中介。'
else:
    text += (
        f'{g("Bootstrap")}检验结果显示，间接效应的95%置信区间为'
        f'[{ci_lower:.3f}, {ci_upper:.3f}]，包含0，中介效应不成立。'
    )
```

## 10. 交叉分析表（卡方检验）

```python
text = f'由表{t}可知，'
for indicator, chi2, p_val, detail_text in results:
    if p_val < 0.05:
        text += (
            f'不同{group_var}在{indicator}上的分布差异有统计学意义'
            f'（χ²={chi2:.3f}，P{_p_str(p_val)}）。'
            f'具体而言，{detail_text}。'
        )
    else:
        text += (
            f'不同{group_var}在{indicator}上的分布差异无统计学意义'
            f'（χ²={chi2:.3f}，P{_p_str(p_val)}）。'
        )
```

---

## 去AI味检查清单

写完文字分析后，搜索以下词汇并替换：

| ❌ 删除/替换 | ✅ 正确写法 |
|-------------|-----------|
| 值得注意的是 | （直接写结论） |
| 综上所述、综合来看 | （直接陈述） |
| 不难发现、显而易见 | （直接陈述） |
| 进一步分析发现 | 此外 |
| 有趣的是、令人意外的是 | （客观陈述） |
| 下降 | 降低 |
| 上升 | 提高/升高 |
| 差异显著（口语化） | 差异有统计学意义 |
| 不显著（口语化） | 差异无统计学意义（P>0.05） |
