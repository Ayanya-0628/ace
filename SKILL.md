---
name: ace
description: >
  数据分析王牌 Skill。用于统计分析、方差分析、ANOVA、回归分析、实证分析、
  DID双重差分、中介效应、调节效应、稳健性检验、工具变量、内生性、
  问卷分析、SERVQUAL、Likert量表、信度检验、效度检验、因子分析、
  卡方检验、描述性统计、交叉分析、相关分析、非参数检验、
  正态性检验、方差齐性、效应量、ROC曲线、ICC、SEM结构方程、
  数据清洗、SPSS格式、三线表、Word报告、论文格式修改、
  图表绘制、matplotlib、学术绘图、配色方案。
  触发词：分析数据、做方差分析、问卷分析、清洗数据、格式修改、画图、
  出报告、实证分析、回归、相关分析、信度、效度
---

# Ace — 数据分析王牌

> 一站式覆盖实证分析全套、统计检验、问卷分析、论文格式、学术绘图。

---

## 一、何时触发

- 统计/实证：方差分析、ANOVA、回归、DID、中介效应、前后测
- 检验/诊断：正态性、方差齐性、相关分析、非参数检验
- 问卷/调研：Likert、SERVQUAL、信度、效度、因子分析
- 格式/输出：论文格式、三线表、页眉页码、Word报告
- 绘图：matplotlib、配色、DID系数图、误差棒、热力图

---

## 二、前置检验模块（任何分析前必做）

### 2.1 正态性检验

```python
from scipy import stats

# Shapiro-Wilk（n<5000，首选）
stat, p = stats.shapiro(data)

# Kolmogorov-Smirnov（大样本）
stat, p = stats.kstest(data, 'norm', args=(data.mean(), data.std()))

# 判断：p>0.05 → 正态，否则用非参数检验
```

### 2.2 方差齐性检验

```python
# Levene 检验（稳健，首选）
stat, p = stats.levene(group1, group2)

# Bartlett 检验（严格正态假设下）
stat, p = stats.bartlett(group1, group2)
```

### 2.3 多重共线性诊断（回归前）

```python
from statsmodels.stats.outliers_influence import variance_inflation_factor

vif = pd.DataFrame({
    'Variable': X.columns,
    'VIF': [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
})
# VIF>10 → 严重共线性，需剔除或合并
```

---

## 三、统计分析模块

### 3.1 描述性统计

```python
desc = df.describe().T
desc['median'] = df.median()
desc['skewness'] = df.skew()
desc['kurtosis'] = df.kurtosis()
# 分类变量：频率表 + 百分比
```

### 3.2 相关分析

```python
# Pearson（连续+正态）
r, p = stats.pearsonr(x, y)

# Spearman（有序/非正态）
rho, p = stats.spearmanr(x, y)

# 相关矩阵热力图
corr_matrix = df[num_cols].corr()
```

**绘图**：相关矩阵热力图，用 `plt.imshow()` 或 `sns.heatmap()`，标注相关系数和显著性星号。

### 3.3 双因素方差分析（ANOVA）

**工作流**：
1. 读取数据 → 分配受试者 ID
2. `statsmodels.formula.api.ols` + `anova_lm(typ=2)`
3. LSD 多重比较 → 紧凑字母显示（CLD）
4. 三线表 Word 输出 + 结果分析段落

**字母标记规则**：
- **小写字母** = 同组内不同时间 LSD（P<0.05）
- **大写字母** = 不同因素水平 LSD（P<0.05）

**参考脚本**：`已完成已结款/心率相关分析50/anova_spss.py`

### 3.4 单因素方差分析

```python
# 参数检验（正态+方差齐）
F, p = stats.f_oneway(g1, g2, g3)

# 事后比较
from statsmodels.stats.multicomp import pairwise_tukeyhsd
tukey = pairwise_tukeyhsd(df['value'], df['group'])

# 非参数替代：Kruskal-Wallis
H, p = stats.kruskal(g1, g2, g3)
# 事后：Dunn 检验 + Bonferroni 校正
```

### 3.5 t 检验全家桶

```python
# 独立样本 t 检验
t, p = stats.ttest_ind(g1, g2, equal_var=True)  # 方差齐
t, p = stats.ttest_ind(g1, g2, equal_var=False)  # Welch's t

# 配对样本 t 检验
t, p = stats.ttest_rel(pre, post)

# 单样本 t 检验
t, p = stats.ttest_1samp(data, popmean=0)

# 非参数替代
U, p = stats.mannwhitneyu(g1, g2)        # Mann-Whitney U
W, p = stats.wilcoxon(pre, post)          # Wilcoxon 符号秩
stat, p = stats.friedmanchisquare(t1, t2, t3)  # Friedman
```

### 3.6 效应量计算

```python
import numpy as np

# Cohen's d（t 检验）
def cohens_d(g1, g2):
    n1, n2 = len(g1), len(g2)
    pooled_std = np.sqrt(((n1-1)*np.std(g1,ddof=1)**2 + (n2-1)*np.std(g2,ddof=1)**2) / (n1+n2-2))
    return (np.mean(g1) - np.mean(g2)) / pooled_std
# |d|: 0.2小, 0.5中, 0.8大

# η²（ANOVA）
eta_sq = ss_between / ss_total

# Cramér's V（卡方检验）
def cramers_v(contingency_table):
    chi2 = stats.chi2_contingency(contingency_table)[0]
    n = contingency_table.sum().sum()
    k = min(contingency_table.shape) - 1
    return np.sqrt(chi2 / (n * k))
```

---

## 四、实证分析全套模块

### 4.1 OLS 回归

```python
import statsmodels.api as sm

X = sm.add_constant(df[['x1', 'x2', 'x3']])
model = sm.OLS(df['y'], X).fit()
print(model.summary())
# 关注：R², adj R², F统计量, 各系数 t值/p值
```

### 4.2 分层回归（Hierarchical Regression）

```python
# 模型1：仅控制变量
m1 = sm.OLS(y, sm.add_constant(controls)).fit()
# 模型2：加入自变量
m2 = sm.OLS(y, sm.add_constant(pd.concat([controls, predictors], axis=1))).fit()
# 模型3：加入交互项
m3 = sm.OLS(y, sm.add_constant(pd.concat([controls, predictors, interactions], axis=1))).fit()
# 比较：ΔR², ΔF 检验
```

### 4.3 Logistic 回归

```python
from statsmodels.formula.api import logit

model = logit('y ~ x1 + x2 + x3', data=df).fit()
# OR值 = np.exp(model.params)
odds_ratios = np.exp(model.params)
conf = np.exp(model.conf_int())
```

### 4.4 有序 Logit / Probit

```python
from statsmodels.miscmodels.ordinal_model import OrderedModel

model = OrderedModel(y, X, distr='logit').fit()  # 或 'probit'
```

### 4.5 中介效应（Mediation）

```python
# Baron & Kenny 四步法
# Step1: X → Y 显著（总效应 c）
# Step2: X → M 显著（a路径）
# Step3: X+M → Y，M显著（b路径），X减弱（c'路径）
# Step4: 间接效应 = a*b, Sobel检验或Bootstrap

# Bootstrap 中介检验（推荐）
from scipy import stats
n_boot = 5000
indirect_effects = []
for _ in range(n_boot):
    idx = np.random.choice(len(df), len(df), replace=True)
    boot_df = df.iloc[idx]
    a = sm.OLS(boot_df['M'], sm.add_constant(boot_df['X'])).fit().params[1]
    b = sm.OLS(boot_df['Y'], sm.add_constant(boot_df[['X','M']])).fit().params[2]
    indirect_effects.append(a * b)
ci_lower, ci_upper = np.percentile(indirect_effects, [2.5, 97.5])
# CI不含0 → 中介效应显著
```

### 4.6 调节效应（Moderation）

```python
# 交互项法
df['X_W'] = df['X'] * df['W']  # 交互项
model = sm.OLS(df['Y'], sm.add_constant(df[['X', 'W', 'X_W']])).fit()
# X_W 系数显著 → 调节效应存在

# 简单斜率分析（Simple Slope）
w_low = df['W'].mean() - df['W'].std()
w_high = df['W'].mean() + df['W'].std()
```

### 4.7 DID 双重差分

```python
# Y = β0 + β1*Treat + β2*Post + β3*Treat×Post + Controls + ε
df['DID'] = df['treat'] * df['post']
model = sm.OLS(df['Y'], sm.add_constant(df[['treat', 'post', 'DID'] + controls])).fit()
# β3 = DID估计量
```

### 4.8 工具变量 / 2SLS（内生性处理）

```python
from linearmodels.iv import IV2SLS

# 第一阶段：X = π0 + π1*Z + ε
# 第二阶段：Y = β0 + β1*X_hat + ε
model = IV2SLS(dependent=df['Y'], exog=df[controls],
               endog=df['X'], instruments=df['Z']).fit()
# 检查：第一阶段F>10，Sargan过度识别检验
```

### 4.9 稳健性检验

1. **替换变量**：换因变量/自变量度量方式
2. **子样本回归**：按年份/地区/规模分组
3. **缩尾处理**：1%/99% winsorize
4. **安慰剂检验**：随机生成处理组
5. **PSM-DID**：倾向得分匹配后再 DID

### 4.10 异质性分析

```python
# 分组回归
for subgroup in df['category'].unique():
    sub_df = df[df['category'] == subgroup]
    model = sm.OLS(sub_df['Y'], sm.add_constant(sub_df[X_cols])).fit()
    # 报告各子样本系数差异
```

---

## 五、问卷分析模块

### 5.1 标准流程

1. **数据清洗**：缺失值、异常值、反向计分
2. **描述性统计**：频率、百分比、均值±标准差
3. **信度检验**：Cronbach's α（总量表+各维度）
4. **效度检验**：KMO + Bartlett → 探索性因子分析（EFA）
5. **交叉分析**：卡方检验 + 列联表
6. **差异分析**：t 检验 / ANOVA

### 5.2 信度检验

```python
def cronbachs_alpha(df):
    k = df.shape[1]
    item_vars = df.var(axis=0, ddof=1)
    total_var = df.sum(axis=1).var(ddof=1)
    return (k / (k - 1)) * (1 - item_vars.sum() / total_var)
# α > 0.7 可接受，> 0.8 良好
```

### 5.3 KMO & 因子分析

```python
from factor_analyzer import FactorAnalyzer
from factor_analyzer.factor_analyzer import calculate_kmo, calculate_bartlett_sphericity

# KMO 检验（>0.6 适合因子分析）
kmo_all, kmo_model = calculate_kmo(df)

# Bartlett 球形检验（p<0.05 适合）
chi2, p = calculate_bartlett_sphericity(df)

# 探索性因子分析
fa = FactorAnalyzer(n_factors=3, rotation='varimax')
fa.fit(df)
loadings = pd.DataFrame(fa.loadings_, index=df.columns)
variance = fa.get_factor_variance()  # 方差解释率
```

### 5.4 ICC 组内相关系数

```python
import pingouin as pg

icc = pg.intraclass_corr(data=df, targets='subject', raters='rater', ratings='score')
# ICC(3,1) 常用于信度评估
```

### 5.5 ROC 曲线（医学/诊断）

```python
from sklearn.metrics import roc_curve, auc

fpr, tpr, thresholds = roc_curve(y_true, y_score)
roc_auc = auc(fpr, tpr)
# 最佳截断点：Youden Index = max(tpr - fpr)
optimal_idx = np.argmax(tpr - fpr)
optimal_threshold = thresholds[optimal_idx]
```

### 5.6 SEM 结构方程模型（基础指南）

```python
# Python: semopy 库
import semopy

model_spec = """
    # 测量模型
    F1 =~ x1 + x2 + x3
    F2 =~ x4 + x5 + x6
    # 结构模型
    F2 ~ F1
"""
model = semopy.Model(model_spec)
model.fit(df)
# 拟合指标：CFI>0.9, RMSEA<0.08, SRMR<0.08, χ²/df<3
stats = semopy.calc_stats(model)
```

---

## 六、论文格式模块

### 6.1 Word 文档字体规范

| 元素 | 中文字体 | 英文/数字字体 | 字号 |
|------|---------|-------------|------|
| 正文 | 宋体 | Times New Roman | 小四（10.5pt） |
| 标题 | 黑体 | Times New Roman | 按级别递减 |
| 表格 | 宋体 | Times New Roman | 小五（9pt） |
| 注释 | 宋体 | Times New Roman | 8pt |
| 图题 | 宋体 | Times New Roman | 8pt |

- **首行缩进**：2字符（约0.74cm）
- **行距**：1.5倍行距
- **字体颜色**：默认黑色

### 6.2 三线表格式

```
顶粗线 ════════════════════════════
 组别 │ 时间 │ 指标1 │ 指标2
栏目细线 ──────────────────────────
 数据行...
虚线分隔 ┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
 因素均值行 + 大写字母
虚线分隔 ┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
 差异分析 F值 + 显著性(**/*/ ns)
底粗线 ════════════════════════════
注：小写=同组内LSD, 大写=组间LSD, **P<0.01, *P<0.05
```

### 6.3 python-docx 三线表核心代码

```python
from docx.oxml.ns import nsdecls, qn
from docx.oxml import parse_xml
from docx.shared import Pt, Cm, RGBColor

def clear_table_borders(table):
    tblPr = table._tbl.tblPr or table._tbl._add_tblPr()
    borders = parse_xml(
        '<w:tblBorders %s>'
        '<w:top w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        '<w:left w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        '<w:bottom w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        '<w:right w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        '<w:insideH w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        '<w:insideV w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        '</w:tblBorders>' % nsdecls('w'))
    for existing in tblPr.findall(qn('w:tblBorders')):
        tblPr.remove(existing)
    tblPr.append(borders)

def set_row_border(row, position, sz=12, val="single", color="000000"):
    for cell in row.cells:
        tc = cell._tc
        tcPr = tc.tcPr or tc._add_tcPr()
        borders = tcPr.find(qn('w:tcBorders'))
        if borders is None:
            borders = parse_xml('<w:tcBorders %s/>' % nsdecls('w'))
            tcPr.append(borders)
        el = parse_xml(f'<w:{position} {nsdecls("w")} w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>')
        existing = borders.find(qn(f'w:{position}'))
        if existing is not None:
            borders.remove(existing)
        borders.append(el)

def set_cell_font(cell, text, font_cn='宋体', font_en='Times New Roman', size=9, bold=False):
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    cell.text = ''
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(str(text))
    run.font.name = font_en
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = RGBColor(0, 0, 0)
    rPr = run._element.find(qn('w:rPr'))
    if rPr is None:
        rPr = parse_xml('<w:rPr %s/>' % nsdecls('w'))
        run._element.insert(0, rPr)
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = parse_xml('<w:rFonts %s/>' % nsdecls('w'))
        rPr.insert(0, rFonts)
    rFonts.set(qn('w:eastAsia'), font_cn)
```

### 6.4 表注格式

- 中文宋体、英文 Times New Roman、五号
- 两端对齐、首行缩进2字符
- 段前/段后 0 行、单倍行距

---

## 七、学术绘图模块

### 7.1 全局绘图初始化（每个脚本开头必加）

```python
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

# ── 中文字体 ──
mpl.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun']
mpl.rcParams['axes.unicode_minus'] = False

# ── 分辨率 ──
mpl.rcParams['figure.dpi'] = 200
mpl.rcParams['savefig.dpi'] = 200

# ── 图形尺寸（A4适配） ──
mpl.rcParams['figure.figsize'] = (5.5, 4.0)  # 英寸

# ── 字体大小 ──
mpl.rcParams['font.size'] = 9
mpl.rcParams['axes.titlesize'] = 10
mpl.rcParams['axes.labelsize'] = 9
mpl.rcParams['xtick.labelsize'] = 8
mpl.rcParams['ytick.labelsize'] = 8
mpl.rcParams['legend.fontsize'] = 8

# ── 边框/刻度 ──
mpl.rcParams['axes.spines.top'] = False
mpl.rcParams['axes.spines.right'] = False
mpl.rcParams['xtick.direction'] = 'out'
mpl.rcParams['ytick.direction'] = 'out'

# ── 输出 ──
mpl.rcParams['savefig.bbox'] = 'tight'
mpl.rcParams['savefig.pad_inches'] = 0.1
```

### 7.2 配色方案

```python
# ── Okabe-Ito 色盲友好（学术首选） ──
OKABE_ITO = ['#E69F00', '#56B4E9', '#009E73', '#F0E442',
             '#0072B2', '#D55E00', '#CC79A7', '#000000']

# ── 红灰显著性 ──
SIG_COLORS = {
    'p<0.01': '#C44E52',     # 深红
    'p<0.05': '#E8866A',     # 浅红
    'ns':     '#8C8C8C',     # 灰色
}

# ── 分组对比（2-4组常用） ──
GROUP_COLORS = ['#4C72B0', '#DD8452', '#55A868', '#C44E52']

# ── 渐变色（热力图） ──
HEATMAP_CMAP = 'RdBu_r'     # 红蓝色阶
CORR_CMAP = 'coolwarm'       # 相关矩阵
```

### 7.3 图表模板

#### 分组柱状图 + 误差棒

```python
def grouped_bar(data, groups, categories, ylabel, title='', colors=None):
    """
    data: dict {group: [values]}
    categories: x轴类别标签
    """
    if colors is None:
        colors = GROUP_COLORS
    x = np.arange(len(categories))
    width = 0.8 / len(groups)
    fig, ax = plt.subplots()
    for i, (group, vals) in enumerate(data.items()):
        means = [np.mean(v) for v in vals]
        sems = [np.std(v, ddof=1)/np.sqrt(len(v)) for v in vals]
        ax.bar(x + i*width - width*(len(groups)-1)/2, means,
               width, yerr=sems, label=group, color=colors[i],
               capsize=3, edgecolor='white', linewidth=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_ylabel(ylabel)
    ax.legend(frameon=False)
    if title:
        ax.set_title(title)
    plt.tight_layout()
    return fig, ax
```

#### 折线图 + 标准误

```python
def line_with_sem(data, time_labels, ylabel, groups=None, colors=None):
    if colors is None:
        colors = GROUP_COLORS
    fig, ax = plt.subplots()
    x = np.arange(len(time_labels))
    for i, (group, vals) in enumerate(data.items()):
        means = [np.mean(v) for v in vals]
        sems = [np.std(v, ddof=1)/np.sqrt(len(v)) for v in vals]
        ax.errorbar(x, means, yerr=sems, label=group,
                    color=colors[i], marker='o', markersize=5,
                    capsize=3, linewidth=1.5)
    ax.set_xticks(x)
    ax.set_xticklabels(time_labels, rotation=30, ha='right')
    ax.set_ylabel(ylabel)
    ax.legend(frameon=False)
    plt.tight_layout()
    return fig, ax
```

#### 相关矩阵热力图

```python
def correlation_heatmap(df, cols, method='pearson'):
    corr = df[cols].corr(method=method)
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    fig, ax = plt.subplots(figsize=(5.5, 5))
    im = ax.imshow(np.where(mask, np.nan, corr), cmap=CORR_CMAP,
                   vmin=-1, vmax=1, aspect='equal')
    ax.set_xticks(range(len(cols)))
    ax.set_yticks(range(len(cols)))
    ax.set_xticklabels(cols, rotation=45, ha='right', fontsize=7)
    ax.set_yticklabels(cols, fontsize=7)
    # 标注系数
    for i in range(len(cols)):
        for j in range(len(cols)):
            if not mask[i, j]:
                ax.text(j, i, f'{corr.iloc[i,j]:.2f}', ha='center',
                        va='center', fontsize=7, color='black')
    plt.colorbar(im, ax=ax, shrink=0.8)
    plt.tight_layout()
    return fig, ax
```

#### DID 系数图

```python
def did_coefficient_plot(periods, coefs, ci_lower, ci_upper, event_time=0):
    fig, ax = plt.subplots()
    ax.errorbar(periods, coefs, yerr=[np.array(coefs)-np.array(ci_lower),
                np.array(ci_upper)-np.array(coefs)],
                fmt='o', color='#0072B2', capsize=4, markersize=6)
    ax.axhline(y=0, color='gray', linestyle='--', linewidth=0.8)
    ax.axvline(x=event_time, color='red', linestyle='--', linewidth=0.8, alpha=0.5)
    ax.set_xlabel('时间（相对于政策实施）')
    ax.set_ylabel('DID 估计系数')
    plt.tight_layout()
    return fig, ax
```

#### ROC 曲线

```python
def plot_roc(fpr, tpr, roc_auc, optimal_point=None):
    fig, ax = plt.subplots()
    ax.plot(fpr, tpr, color='#C44E52', lw=2,
            label=f'ROC (AUC = {roc_auc:.3f})')
    ax.plot([0, 1], [0, 1], 'k--', lw=0.8)
    if optimal_point:
        ax.scatter(*optimal_point, marker='*', s=100, color='#E69F00',
                   zorder=5, label=f'最佳截断点')
    ax.set_xlabel('1 - 特异度 (FPR)')
    ax.set_ylabel('灵敏度 (TPR)')
    ax.legend(loc='lower right', frameon=False)
    plt.tight_layout()
    return fig, ax
```

### 7.4 显著性标注

```python
def add_significance(ax, x1, x2, y, p_value, height=0.02):
    """在柱状图上添加显著性标注线和星号"""
    if p_value < 0.001:
        text = '***'
    elif p_value < 0.01:
        text = '**'
    elif p_value < 0.05:
        text = '*'
    else:
        text = 'ns'
    y_max = y + height * (ax.get_ylim()[1] - ax.get_ylim()[0])
    ax.plot([x1, x1, x2, x2], [y, y_max, y_max, y], 'k-', lw=0.8)
    ax.text((x1+x2)/2, y_max, text, ha='center', va='bottom', fontsize=8)
```

### 7.5 图片导出

```python
# 标准导出（嵌入Word / 投稿用）
fig.savefig('figure1.png', dpi=200, bbox_inches='tight',
            facecolor='white', edgecolor='none')

# 高清版（印刷用）
fig.savefig('figure1_hires.tiff', dpi=300, bbox_inches='tight')

# 矢量图（编辑用）
fig.savefig('figure1.svg', bbox_inches='tight')
fig.savefig('figure1.pdf', bbox_inches='tight')
```

### 7.6 图题格式

图题位于图下方，格式：`图X <空格> 描述文字`
- 字体：宋体 8pt
- 居中对齐
- Word 中用 python-docx 添加：

```python
fig_caption = doc.add_paragraph()
fig_caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = fig_caption.add_run(f'图{fig_num} {caption_text}')
run.font.name = 'Times New Roman'
run.font.size = Pt(8)
# 设置东亚字体为宋体（同 set_cell_font 方法）
```

---

## 八、结果分析写作风格

### 要求

- **一整段连贯文字**，不按指标分列
- 首行缩进 2 字符，客观陈述
- 去 AI 味：删"值得注意的是""综合来看"，统一"降低"不用"下降"

### 段落结构

1. "由表X可知" + 宏观概述哪些指标受显著影响
2. **百分比**描述组间差异（不逐个列均值±标准差）
3. 过渡词：首个直接跟概述，中间"此外"，末尾"就XX而言"
4. 交互效应：差异最大/最小时间点
5. 结尾"这表明..."因果总结

---

## 九、通用规范

### 9.1 PowerShell 编码

```powershell
$env:PYTHONUTF8="1"; & "python.exe" "script.py" 2>&1
```

### 9.2 依赖库

```
核心：pandas, numpy, scipy, statsmodels, openpyxl, python-docx, matplotlib
可选：savReaderWriter, pingouin, factor_analyzer, semopy, linearmodels, scikit-learn
```

### 9.3 交付物检查清单

- [ ] Excel 分析附表（原始数据 + 统计结果）
- [ ] Word 报告（三线表 + 结果分析文字 + 图表）
- [ ] 图表文件（PNG 200dpi，已嵌入 Word）
- [ ] 脚本代码（可复现）

---

## 十、scripts/ 可执行工具脚本

> 位于 `scripts/` 目录下，可直接 `python` 执行或作为模块 `import`。

### 10.1 check_assumptions.py — 前置检验一键工具

```bash
python scripts/check_assumptions.py data.xlsx --cols HR MAP BIS --group 组别
python scripts/check_assumptions.py data.xlsx --cols score --vif x1 x2 x3
```
- 正态性检验（Shapiro-Wilk / K-S）
- 方差齐性检验（Levene）
- 多重共线性诊断（VIF）
- 彩色终端报告 + 综合建议

### 10.2 anova_pipeline.py — 方差分析流水线

```bash
python scripts/anova_pipeline.py data.xlsx --indicators HR MAP --group 组别 --time 时间 \
    --time-order T1 T2 T3 --output result.docx
```
- 双因素 ANOVA（组别×时间）
- LSD 多重比较 → CLD 紧凑字母
- 三线表 Word 自动输出
- 可作为模块导入: `from anova_pipeline import do_two_way_anova, cld_from_pmatrix`

### 10.3 questionnaire_pipeline.py — 问卷分析流水线

```bash
python scripts/questionnaire_pipeline.py data.xlsx \
    --dims 维度1:Q1,Q2,Q3 维度2:Q4,Q5 --reverse Q3 --kmo --efa 3
```
- 数据清洗 + 反向计分
- Cronbach's α（总量表+各维度）+ CITC
- KMO + Bartlett → EFA
- 结果导出 Excel

### 10.4 three_line_table.py — 三线表 Word 生成器

```python
from three_line_table import ThreeLineTable, create_doc_portrait
doc = create_doc_portrait()
ThreeLineTable.add_table_title(doc, '表1 描述性统计')
ThreeLineTable.build_simple(doc, ['变量','M','SD'], [['X1','3.2','0.8']])
ThreeLineTable.build_regression(doc, models=[...])  # 回归结果表
doc.save('output.docx')
```

### 10.5 plot_utils.py — 学术绘图工具集

```python
from plot_utils import init_style, grouped_bar, correlation_heatmap, save_figure
init_style()  # 中文字体 + 200dpi + 去右上边框
fig, ax = grouped_bar(data, categories, 'Y轴')
save_figure(fig, 'fig1.png')
```
- 配色方案: `OKABE_ITO`, `GROUP_COLORS`, `SIG_COLORS`
- 图表: `grouped_bar`, `line_with_sem`, `correlation_heatmap`, `did_coefficient_plot`, `roc_plot`
- 辅助: `add_significance`, `save_figure`

---

## 十一、SPSS SPV 过程文件生成

> 客户常要求交付 SPSS 过程文件（.spv），需通过 SPSS 内置 Python 接口生成。

### 11.1 技术方案对比

| 方案 | 中文标题 | OUTPUT SAVE | 稳定性 | 推荐度 |
|------|---------|-------------|--------|--------|
| **SpssClient**（GUI接口） | ✅ | ✅ | 高 | ⭐⭐⭐ 首选 |
| **OMS + spss.Submit** | ❌ 英文 | N/A（OMS替代） | 高 | ⭐⭐ 回退 |
| stats.exe -production | ❌ | ❌ | 低 | ❌ |
| stats.com -f -type -out | ❌ | ❌ | 不支持 | ❌ |

### 11.2 踩坑记录（SPSS 27 非 GUI 模式限制）

- `OUTPUT NEW` / `OUTPUT SAVE`：非 GUI 模式（statisticspython3.bat 直接调 spss.Submit）不可用，报 errLevel 3
- `SET OLANG=CHINESE`：非 GUI 模式不可用；SpssClient 模式下报错误号 833 但**不影响分析结果**
- **OMS**：非 GUI 模式下导出 SPV 的唯一可靠方式，但输出标题为英文
- **SpssClient**：GUI 模式接口，自动继承系统语言（中文），支持 OUTPUT SAVE
- SPS 文件编码：SPSS 语法编辑器默认用系统编码（GBK），UTF-8 保存的中文会乱码

### 11.3 推荐用法

```python
# 通过 statisticspython3.bat 执行
# "C:\Program Files\IBM\SPSS\Statistics\27\statisticspython3.bat" your_script.py

from spss_spv_generator import run_spss_analysis

syntax_list = [
    "LOGISTIC REGRESSION VARIABLES 分组 /METHOD=ENTER x1 /PRINT=CI(95) /CRITERIA=PIN(0.05) POUT(0.10) ITERATE(20) CUT(0.5).",
    "ROC x1 BY 分组 (1) /PLOT=CURVE(REFERENCE) /PRINT=SE COORDINATES /CRITERIA=CUTOFF(INCLUDE) TESTPOS(LARGE) DISTRIBUTION(FREE) CI(95).",
]
run_spss_analysis('data.sav', syntax_list, 'output.spv', 'data_with_pred.sav')
```

**完整脚本**：`scripts/spss_spv_generator.py`（含 SpssClient → OMS 自动回退）

### 11.4 PowerShell 调用

```powershell
& "C:\Program Files\IBM\SPSS\Statistics\27\statisticspython3.bat" "run_spss_save_spv.py" 2>&1
```
