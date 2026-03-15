---
name: ace
description: >
  数据分析王牌 Skill。用于统计分析、方差分析、ANOVA、回归分析、实证分析、
  DID双重差分、中介效应、调节效应、稳健性检验、工具变量、内生性、
  问卷分析、SERVQUAL、Likert量表、信度检验、效度检验、因子分析、
  卡方检验、描述性统计、交叉分析、相关分析、非参数检验、
  正态性检验、方差齐性、效应量、ROC曲线、ICC、SEM结构方程、
  机器学习、随机森林、RandomForest、XGBoost、SVM、分类模型、
  预测模型、超参调优、GridSearch、Optuna、特征重要性、SHAP、
  交叉验证、混淆矩阵、学习曲线、Pipeline、模型评估、
  数据清洗、SPSS格式、三线表、Word报告、论文格式修改、
  图表绘制、matplotlib、学术绘图、配色方案。
  触发词：分析数据、做方差分析、问卷分析、清洗数据、格式修改、画图、
  出报告、实证分析、回归、相关分析、信度、效度、随机森林、
  机器学习、建模、调参、预测、分类、特征重要性
---

# Ace — 数据分析王牌

> 一站式覆盖实证分析全套、统计检验、问卷分析、论文格式、学术绘图。

---

## 一、何时触发

- 统计/实证：方差分析、ANOVA、回归、DID、中介效应、前后测
- 检验/诊断：正态性、方差齐性、相关分析、非参数检验
- 问卷/调研：Likert、SERVQUAL、信度、效度、因子分析
- **机器学习**：随机森林、XGBoost、SVM、调参、特征重要性、SHAP
- 格式/输出：论文格式、三线表、页眉页码、Word报告
- 绘图：matplotlib、配色、DID系数图、误差棒、热力图、混淆矩阵、学习曲线

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

> ⚠️ **踩坑记录**：`factor_analyzer` 库与 sklearn ≥ 1.6 不兼容（`force_all_finite` → `ensure_all_finite`），
> 导致 `FactorAnalyzer.fit()` 抛出 `TypeError`。以下为不依赖该库的手动实现。

```python
import numpy as np
from numpy.linalg import inv, eig, det
from scipy.stats import chi2 as chi2_dist

# ── 手动 KMO ──
def manual_kmo(data):
    corr = data.corr().values
    try:
        corr_inv = inv(corr)
    except:
        corr_inv = np.linalg.pinv(corr)
    n = corr.shape[0]
    A = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            A[i, j] = -corr_inv[i, j] / np.sqrt(corr_inv[i, i] * corr_inv[j, j])
    sum_r2 = sum(corr[i, j]**2 for i in range(n) for j in range(n) if i != j)
    sum_a2 = sum(A[i, j]**2 for i in range(n) for j in range(n) if i != j)
    return sum_r2 / (sum_r2 + sum_a2)

# ── 手动 Bartlett 球形检验 ──
def manual_bartlett(data):
    n, p = len(data), data.shape[1]
    corr = data.corr().values
    det_val = max(det(corr), 1e-300)
    chi_sq = -(n - 1 - (2 * p + 5) / 6) * np.log(det_val)
    df = p * (p - 1) / 2
    p_val = 1 - chi2_dist.cdf(chi_sq, df)
    return chi_sq, p_val

# ── 手动 EFA + Varimax 旋转 ──
def varimax_rotation(loadings, max_iter=100, tol=1e-6):
    n, k = loadings.shape
    R = np.eye(k)
    d = 0
    for _ in range(max_iter):
        old_d = d
        L = loadings @ R
        u, s, vt = np.linalg.svd(
            loadings.T @ (L**3 - (1.0/n) * L @ np.diag(np.diag(L.T @ L))))
        R = u @ vt
        d = np.sum(s)
        if abs(d - old_d) < tol:
            break
    return loadings @ R

# PCA 提取 + Varimax 旋转
corr_matrix = np.corrcoef(data_standardized, rowvar=False)
eigenvalues, eigenvectors = eig(corr_matrix)
idx = np.argsort(eigenvalues)[::-1]
eigenvalues, eigenvectors = eigenvalues[idx].real, eigenvectors[:, idx].real
raw_loadings = eigenvectors[:, :n_factors] * np.sqrt(eigenvalues[:n_factors])
rotated = varimax_rotation(raw_loadings)
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

> **字体铁律**：不要用 `rcParams['font.sans-serif']` 设全局中文字体，
> 改用 `FontProperties` 对象逐元素指定，严格保证「中文宋体 + 英文 Times New Roman」。
> 此方案在 `plot_nitrogen.py`（土壤铵态氮/硝态氮水平条形图）中验证通过。

```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.font_manager import FontProperties
import numpy as np

# ══════ 字体对象（精确控制，按元素指定） ══════
FONT_SONG = FontProperties(fname=r'C:\Windows\Fonts\simsun.ttc')   # 宋体 → 中文正文、轴标签
FONT_HEI  = FontProperties(fname=r'C:\Windows\Fonts\simhei.ttf')   # 黑体 → 子图标题
FONT_TNR  = FontProperties(family='Times New Roman')                # TNR  → 英文/数字/字母标记

# ══════ 仅设serif回退 + 负号，不设全局字体 ══════
rcParams['font.serif'] = ['Times New Roman', 'SimSun']
rcParams['axes.unicode_minus'] = False

# ── 分辨率 ──
rcParams['figure.dpi'] = 300
rcParams['savefig.dpi'] = 300

# ── 图形尺寸（A4适配） ──
rcParams['figure.figsize'] = (5.5, 4.0)  # 英寸

# ── 字体大小（全局默认值，可被 fontproperties 覆盖） ──
rcParams['font.size'] = 9
rcParams['axes.titlesize'] = 10
rcParams['axes.labelsize'] = 9
rcParams['xtick.labelsize'] = 8
rcParams['ytick.labelsize'] = 8
rcParams['legend.fontsize'] = 8

# ── 边框/刻度 ──
rcParams['axes.spines.top'] = False
rcParams['axes.spines.right'] = False
rcParams['xtick.direction'] = 'out'
rcParams['ytick.direction'] = 'out'

# ── 输出 ──
rcParams['savefig.bbox'] = 'tight'
rcParams['savefig.pad_inches'] = 0.1
```

**使用方式**：在每个 text/label/title 处通过 `fontproperties=` 参数指定：

```python
# 子图标题 → 黑体
ax.set_title('返青期', fontproperties=FONT_HEI, fontsize=11, fontweight='bold')

# 中英混排轴标签 → 拆成两个 ax.text，分别用宋体和TNR
ax.text(-0.13, 0.50, '(cm)', transform=ax.transAxes,
        fontproperties=FONT_TNR, fontsize=10, ha='center', va='bottom', rotation=90)
ax.text(-0.13, 0.49, '土层深度', transform=ax.transAxes,
        fontproperties=FONT_SONG, fontsize=10, ha='center', va='top', rotation=90)

# 刻度数字 → TNR
for label in ax.get_xticklabels():
    label.set_fontproperties(FONT_TNR)
    label.set_fontsize(9)

# 图例文字 → TNR（处理名），图例标题 → 宋体
leg = ax.legend(title='处理', title_fontproperties=FONT_SONG.copy())
for text in leg.get_texts():
    text.set_fontproperties(FONT_TNR)

# 显著性字母标记 → TNR
ax.text(x, y, 'ab', fontproperties=FONT_TNR, fontsize=9)

# 保存（学术投稿推荐 300 DPI）
plt.savefig('output.png', dpi=300, bbox_inches='tight', facecolor='white')
```

**适用场景**：水平/垂直条形图、多子图、需严格满足「中文宋体 + 英文TNR」的学术图表。

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

> **字体提醒**：以下模板为简洁省略了 `fontproperties` 参数。实际使用时，
> 所有中文文本须加 `fontproperties=FONT_SONG` 或 `FONT_HEI`，
> 所有英文/数字文本须加 `fontproperties=FONT_TNR`（参见 7.1 字体铁律）。

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
    ax.set_xticklabels(categories, fontproperties=FONT_TNR)
    ax.set_ylabel(ylabel, fontproperties=FONT_SONG)
    for lbl in ax.get_yticklabels():
        lbl.set_fontproperties(FONT_TNR)
    leg = ax.legend(frameon=False)
    for t in leg.get_texts():
        t.set_fontproperties(FONT_TNR)
    if title:
        ax.set_title(title, fontproperties=FONT_HEI)
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
    ax.set_xticklabels(time_labels, rotation=30, ha='right', fontproperties=FONT_TNR)
    ax.set_ylabel(ylabel, fontproperties=FONT_SONG)
    for lbl in ax.get_xticklabels() + ax.get_yticklabels():
        lbl.set_fontproperties(FONT_TNR)
    leg = ax.legend(frameon=False)
    for t in leg.get_texts():
        t.set_fontproperties(FONT_TNR)
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
    ax.set_xticklabels(cols, rotation=45, ha='right', fontsize=7, fontproperties=FONT_TNR)
    ax.set_yticklabels(cols, fontsize=7, fontproperties=FONT_TNR)
    # 标注系数
    for i in range(len(cols)):
        for j in range(len(cols)):
            if not mask[i, j]:
                ax.text(j, i, f'{corr.iloc[i,j]:.2f}', ha='center',
                        va='center', fontsize=7, color='black',
                        fontproperties=FONT_TNR)
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
    ax.set_xlabel('时间（相对于政策实施）', fontproperties=FONT_SONG)
    ax.set_ylabel('DID 估计系数', fontproperties=FONT_SONG)
    for lbl in ax.get_xticklabels() + ax.get_yticklabels():
        lbl.set_fontproperties(FONT_TNR)
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
                   zorder=5, label='最佳截断点')
    # 中英混排轴标签：拆成两个 text
    ax.set_xlabel('')
    ax.text(0.5, -0.08, '1 - 特异度 ', transform=ax.transAxes,
            ha='right', va='top', fontproperties=FONT_SONG, fontsize=9)
    ax.text(0.5, -0.08, '(FPR)', transform=ax.transAxes,
            ha='left', va='top', fontproperties=FONT_TNR, fontsize=9)
    ax.set_ylabel('')
    ax.text(-0.10, 0.5, '(TPR)', transform=ax.transAxes,
            ha='center', va='bottom', rotation=90, fontproperties=FONT_TNR, fontsize=9)
    ax.text(-0.10, 0.49, '灵敏度 ', transform=ax.transAxes,
            ha='center', va='top', rotation=90, fontproperties=FONT_SONG, fontsize=9)
    for lbl in ax.get_xticklabels() + ax.get_yticklabels():
        lbl.set_fontproperties(FONT_TNR)
    leg = ax.legend(loc='lower right', frameon=False)
    for t in leg.get_texts():
        t.set_fontproperties(FONT_TNR)
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
    ax.text((x1+x2)/2, y_max, text, ha='center', va='bottom',
            fontsize=8, fontproperties=FONT_TNR)
```

### 7.5 图片导出

```python
# 标准导出（嵌入Word / 投稿用，统一 300 DPI）
fig.savefig('figure1.png', dpi=300, bbox_inches='tight',
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

## 九、机器学习建模模块

### 9.1 数据预处理 Pipeline

```python
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
import pandas as pd
import numpy as np

# ── 数据集划分 ──
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y  # 分类任务加 stratify
)

# ── 数值+分类混合 Pipeline ──
num_cols = X.select_dtypes(include='number').columns.tolist()
cat_cols = X.select_dtypes(include='object').columns.tolist()

preprocessor = ColumnTransformer([
    ('num', Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ]), num_cols),
    ('cat', Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ]), cat_cols)
])
```

### 9.2 随机森林分类

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (classification_report, confusion_matrix,
                             roc_auc_score, accuracy_score)

# ── 基础模型 ──
rf_clf = Pipeline([
    ('prep', preprocessor),
    ('clf', RandomForestClassifier(
        n_estimators=200,
        max_depth=None,         # 先不限制，调参时再约束
        min_samples_split=5,
        min_samples_leaf=2,
        max_features='sqrt',
        class_weight='balanced', # 类别不平衡时使用
        random_state=42,
        n_jobs=-1
    ))
])
rf_clf.fit(X_train, y_train)
y_pred = rf_clf.predict(X_test)
y_proba = rf_clf.predict_proba(X_test)

# ── 评估 ──
print(classification_report(y_test, y_pred, digits=4))
print(f'Accuracy: {accuracy_score(y_test, y_pred):.4f}')
# 多分类 AUC
auc = roc_auc_score(y_test, y_proba, multi_class='ovr', average='weighted')
print(f'AUC (weighted OVR): {auc:.4f}')
```

### 9.3 随机森林回归

```python
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

rf_reg = Pipeline([
    ('prep', preprocessor),
    ('reg', RandomForestRegressor(
        n_estimators=200,
        max_depth=None,
        min_samples_split=5,
        min_samples_leaf=2,
        max_features='sqrt',
        random_state=42,
        n_jobs=-1
    ))
])
rf_reg.fit(X_train, y_train)
y_pred = rf_reg.predict(X_test)

print(f'R²:   {r2_score(y_test, y_pred):.4f}')
print(f'RMSE: {np.sqrt(mean_squared_error(y_test, y_pred)):.4f}')
print(f'MAE:  {mean_absolute_error(y_test, y_pred):.4f}')
```

### 9.4 超参调优

#### GridSearchCV（小参数空间，穷举）

```python
from sklearn.model_selection import GridSearchCV

param_grid = {
    'clf__n_estimators': [100, 200, 500],
    'clf__max_depth': [5, 10, 20, None],
    'clf__min_samples_split': [2, 5, 10],
    'clf__min_samples_leaf': [1, 2, 4],
    'clf__max_features': ['sqrt', 'log2'],
}

grid = GridSearchCV(
    rf_clf, param_grid,
    cv=5, scoring='accuracy',  # 或 'roc_auc_ovr_weighted'
    n_jobs=-1, verbose=1, refit=True
)
grid.fit(X_train, y_train)

print(f'最优参数: {grid.best_params_}')
print(f'最优CV分数: {grid.best_score_:.4f}')
best_model = grid.best_estimator_
```

#### RandomizedSearchCV（大参数空间，随机采样）

```python
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import randint, uniform

param_dist = {
    'clf__n_estimators': randint(100, 1000),
    'clf__max_depth': [5, 10, 15, 20, 30, None],
    'clf__min_samples_split': randint(2, 20),
    'clf__min_samples_leaf': randint(1, 10),
    'clf__max_features': ['sqrt', 'log2', 0.3, 0.5],
}

random_search = RandomizedSearchCV(
    rf_clf, param_dist,
    n_iter=100, cv=5, scoring='accuracy',
    random_state=42, n_jobs=-1, verbose=1
)
random_search.fit(X_train, y_train)
print(f'最优参数: {random_search.best_params_}')
```

#### Optuna 贝叶斯调参（推荐，效率最高）

```python
import optuna
from sklearn.model_selection import cross_val_score

def objective(trial):
    params = {
        'n_estimators': trial.suggest_int('n_estimators', 100, 1000),
        'max_depth': trial.suggest_int('max_depth', 3, 30),
        'min_samples_split': trial.suggest_int('min_samples_split', 2, 20),
        'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 10),
        'max_features': trial.suggest_categorical('max_features', ['sqrt', 'log2']),
    }
    clf = Pipeline([
        ('prep', preprocessor),
        ('clf', RandomForestClassifier(**params, random_state=42, n_jobs=-1))
    ])
    score = cross_val_score(clf, X_train, y_train, cv=5, scoring='accuracy').mean()
    return score

study = optuna.create_study(direction='maximize')
study.optimize(objective, n_trials=100, show_progress_bar=True)
print(f'最优参数: {study.best_params}')
print(f'最优CV分数: {study.best_value:.4f}')

# Optuna 可视化
from optuna.visualization.matplotlib import (
    plot_optimization_history, plot_param_importances
)
plot_optimization_history(study)
plot_param_importances(study)
plt.tight_layout()
plt.savefig('optuna_history.png', dpi=200, bbox_inches='tight')
```

### 9.5 交叉验证

```python
from sklearn.model_selection import cross_validate, StratifiedKFold

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

scoring = {
    'accuracy': 'accuracy',
    'precision_weighted': 'precision_weighted',
    'recall_weighted': 'recall_weighted',
    'f1_weighted': 'f1_weighted',
    'roc_auc_ovr_weighted': 'roc_auc_ovr_weighted',
}

cv_results = cross_validate(best_model, X_train, y_train,
                            cv=cv, scoring=scoring, return_train_score=True)

for metric, scores in cv_results.items():
    if metric.startswith('test_'):
        name = metric.replace('test_', '')
        print(f'{name}: {scores.mean():.4f} ± {scores.std():.4f}')
```

### 9.6 特征重要性

#### sklearn 内置

```python
# 从 Pipeline 中提取模型
rf_model = best_model.named_steps['clf']
importances = rf_model.feature_importances_

# 获取特征名（Pipeline 处理后）
feature_names = best_model.named_steps['prep'].get_feature_names_out()

feat_imp = pd.DataFrame({
    'feature': feature_names,
    'importance': importances
}).sort_values('importance', ascending=False)

print(feat_imp.head(15))
```

#### Permutation Importance（更稳健）

```python
from sklearn.inspection import permutation_importance

perm_imp = permutation_importance(
    best_model, X_test, y_test,
    n_repeats=10, random_state=42, n_jobs=-1
)

perm_df = pd.DataFrame({
    'feature': feature_names if hasattr(best_model, 'named_steps') else X.columns,
    'importance_mean': perm_imp.importances_mean,
    'importance_std': perm_imp.importances_std
}).sort_values('importance_mean', ascending=False)
```

#### SHAP 解释（推荐，可解释性最强）

```python
import shap

# 对 Pipeline，先 transform 再用 TreeExplainer
X_test_transformed = best_model.named_steps['prep'].transform(X_test)
rf_model = best_model.named_steps['clf']
explainer = shap.TreeExplainer(rf_model)
shap_values = explainer.shap_values(X_test_transformed)

# Summary plot（全局特征重要性）
fig, ax = plt.subplots(figsize=(5.5, 6))
shap.summary_plot(shap_values, X_test_transformed,
                  feature_names=feature_names, show=False)
plt.tight_layout()
plt.savefig('shap_summary.png', dpi=200, bbox_inches='tight')

# Bar plot（平均绝对 SHAP 值）
shap.summary_plot(shap_values, X_test_transformed,
                  feature_names=feature_names, plot_type='bar', show=False)
```

### 9.7 ML 可视化模板

#### 特征重要性柱状图

```python
def plot_feature_importance(feat_df, top_n=15, title='特征重要性'):
    """feat_df: DataFrame with 'feature' and 'importance' columns"""
    top = feat_df.head(top_n).sort_values('importance')
    fig, ax = plt.subplots(figsize=(5.5, 0.35 * top_n))
    colors = ['#C44E52' if v >= top['importance'].quantile(0.75)
              else '#4C72B0' for v in top['importance']]
    ax.barh(top['feature'], top['importance'], color=colors, edgecolor='white')
    ax.set_xlabel('重要性')
    ax.set_title(title)
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    plt.tight_layout()
    return fig, ax
```

#### 混淆矩阵热力图

```python
from sklearn.metrics import ConfusionMatrixDisplay

def plot_confusion(y_true, y_pred, labels=None, title='混淆矩阵'):
    fig, ax = plt.subplots(figsize=(5, 4.5))
    ConfusionMatrixDisplay.from_predictions(
        y_true, y_pred, display_labels=labels,
        cmap='Blues', ax=ax, colorbar=False,
        text_kw={'fontsize': 10}
    )
    ax.set_title(title)
    ax.set_xlabel('预测类别')
    ax.set_ylabel('真实类别')
    plt.tight_layout()
    return fig, ax
```

#### 学习曲线

```python
from sklearn.model_selection import learning_curve

def plot_learning_curve(estimator, X, y, title='学习曲线', cv=5):
    train_sizes, train_scores, val_scores = learning_curve(
        estimator, X, y, cv=cv,
        train_sizes=np.linspace(0.1, 1.0, 10),
        scoring='accuracy', n_jobs=-1
    )
    train_mean = train_scores.mean(axis=1)
    train_std = train_scores.std(axis=1)
    val_mean = val_scores.mean(axis=1)
    val_std = val_scores.std(axis=1)

    fig, ax = plt.subplots()
    ax.fill_between(train_sizes, train_mean - train_std,
                    train_mean + train_std, alpha=0.15, color='#4C72B0')
    ax.fill_between(train_sizes, val_mean - val_std,
                    val_mean + val_std, alpha=0.15, color='#C44E52')
    ax.plot(train_sizes, train_mean, 'o-', color='#4C72B0',
            label='训练集', markersize=4)
    ax.plot(train_sizes, val_mean, 'o-', color='#C44E52',
            label='验证集', markersize=4)
    ax.set_xlabel('训练样本数')
    ax.set_ylabel('准确率')
    ax.set_title(title)
    ax.legend(frameon=False)
    plt.tight_layout()
    return fig, ax
```

#### 多分类 ROC 曲线

```python
from sklearn.metrics import roc_curve, auc
from sklearn.preprocessing import label_binarize

def plot_multiclass_roc(y_true, y_proba, classes):
    y_bin = label_binarize(y_true, classes=classes)
    fig, ax = plt.subplots()
    colors = OKABE_ITO[:len(classes)]
    for i, (cls, color) in enumerate(zip(classes, colors)):
        fpr, tpr, _ = roc_curve(y_bin[:, i], y_proba[:, i])
        roc_auc = auc(fpr, tpr)
        ax.plot(fpr, tpr, color=color, lw=1.5,
                label=f'{cls} (AUC={roc_auc:.3f})')
    ax.plot([0, 1], [0, 1], 'k--', lw=0.8)
    ax.set_xlabel('1 - 特异度 (FPR)')
    ax.set_ylabel('灵敏度 (TPR)')
    ax.legend(loc='lower right', frameon=False, fontsize=7)
    ax.set_title('多分类 ROC 曲线')
    plt.tight_layout()
    return fig, ax
```

### 9.8 其他常用模型（快速切换）

```python
from sklearn.svm import SVC
from sklearn.ensemble import GradientBoostingClassifier

# ── XGBoost ──
try:
    from xgboost import XGBClassifier
    xgb_clf = XGBClassifier(
        n_estimators=200, max_depth=6, learning_rate=0.1,
        subsample=0.8, colsample_bytree=0.8,
        eval_metric='mlogloss', random_state=42, n_jobs=-1
    )
except ImportError:
    pass

# ── SVM ──
svm_clf = Pipeline([
    ('prep', preprocessor),
    ('clf', SVC(kernel='rbf', C=1.0, gamma='scale', probability=True))
])

# ── GBDT ──
gbdt_clf = Pipeline([
    ('prep', preprocessor),
    ('clf', GradientBoostingClassifier(
        n_estimators=200, max_depth=5, learning_rate=0.1, random_state=42
    ))
])

# ── 模型对比 ──
from sklearn.model_selection import cross_val_score
models = {'RF': rf_clf, 'SVM': svm_clf, 'GBDT': gbdt_clf}
for name, model in models.items():
    scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
    print(f'{name}: {scores.mean():.4f} ± {scores.std():.4f}')
```

### 9.9 ML 交付物检查清单

- [ ] 数据预处理说明（缺失值、编码、标准化方式）
- [ ] 模型选择理由 + 基线模型性能
- [ ] 超参调优过程（搜索空间 + 最优参数）
- [ ] 交叉验证结果（Acc / Precision / Recall / F1 / AUC）
- [ ] 混淆矩阵 + 分类报告
- [ ] 特征重要性排序（Top 15）
- [ ] SHAP 解释图（如客户需要可解释性）
- [ ] 学习曲线（判断过拟合/欠拟合）

---

## 十、通用规范

### 10.1 PowerShell 编码

```powershell
$env:PYTHONUTF8="1"; & "python.exe" "script.py" 2>&1
```

### 10.2 依赖库

```
核心：pandas, numpy, scipy, statsmodels, openpyxl, python-docx, matplotlib
ML：scikit-learn, shap, optuna, xgboost
可选：savReaderWriter, pingouin, factor_analyzer, semopy, linearmodels
```

### 10.3 交付物检查清单

- [ ] Excel 分析附表（原始数据 + 统计结果）
- [ ] Word 报告（三线表 + 结果分析文字 + 图表）
- [ ] 图表文件（PNG 200dpi，已嵌入 Word）
- [ ] 脚本代码（可复现）

---

## 十一、SPSS 原生输出专项工作流 (针对挑剔客户)

### 11.1 环境限制与结论
由于该机器上的 SPSS 27 底层 Java 组件 Bug，**无法使用 `stats.exe -production silent` 或任何无头模式 (Headless / Silent) 自动静默导出表单**（运行时会抛出 `NullPointerException` 或卡死）。因此，**禁止尝试在后台悄悄调 SPSS**。

### 11.2 标准化替代方案（脑力代码化，体力手动化）
当客户明确要求提交 SPSS 原始分析过程和结果表时，必须遵循以下“代码生成+手动执行”工作流：

1. **Python 生成语法**：读取客户数据后，使用 Python 按照要求生成完整的 SPSS Syntax 语法脚本（`.sps`）。
   - 代码中需包含 `GET DATA` 来读取客户的数据文件。
   - 包含各种分析命令（如 `FREQUENCIES`, `DESCRIPTIVES`, `GLM` 等）。
   - **结尾必须**附上自动导出到同目录 Excel 或 Word 的命令：
     ```spss
     OUTPUT EXPORT
       /CONTENTS  EXPORT=ALL  LAYERS=PRINTSETTING  MODELVIEWS=PRINTSETTING
       /XLSX DOCUMENTFILE='C:\\绝对路径\\导出的结果表.xlsx'
       OPERATION=CREATEFILE.
     ```
2. **交付语法进行验证**：将这段 `.sps` 脚本内容发送给客户或项目负责人（即现在的你），让他们手动在电脑上双击打开本机的 SPSS 界面。
3. **人工"一键点击"**：在 SPSS 中新建或打开语法文件，贴入代码，点击“运行” -> “全部”，即可完美生成无任何误差的原版结果报表。


---

## ʮ����ʵ֤�������� Checklist���ؼ��

> ��Դ����������ʵ֤������Ŀ�ȿ��ܽᡣ����ÿ���ڽ���ǰ������һ�˲顣

### 12.1 ���ݴ���
- ��׼��ʱ����ȷ���Ƿ���Ҫ Z-score����β֮�󡢻ع�֮ǰ���
- ������ͳ����ԭʼֵ����1������β��ԭʼֵ

### 12.2 ����Է���
- ����������Ʊ�����Pearson�����������Size/Board�ȿ��Ʊ���

### 12.3 VIF ���ع�����
- �������к��ı������Ա���+�н�+����+����ȫ������
- ����ӳ����sm.add_constant()������VIF

### 12.4 ��ЧӦ�ع�
- �������Լ��裺���ļ��赹U�ͱ������������
- ����ָ�귽��|DA|��Խ��Խ��ʱX2��=��U��
- �յ�=-B1/(2B2)����֤�����ݷ�Χ��

### 12.5 �Ƚ��Լ���
- ��������ɾ������
- ���������Է���������IV��PSM

### 12.6 ������
- 2SLS��һ�׶�F>10
- ��pip install linearmodels

### 12.7 �����ļ�
- ͳһ�ļ��к�Word+Excel+Stata+��������
- �������ݰ���ű�ע
- ������ʱ�ļ�

### 12.8 �������״�
- |DA|ϵ����=�������
- ����ָ��ʱU/��U�ж��෴
- HC1�Ƚ�SE�ǺϷ�ѡ��



### 7.8 绘图网格线规范

**铁律**: 学术图表默认**不添加背景网格线**（grid）。
- 除非用户/客户明确要求，否则所有 matplotlib 图表不要调用 x.xaxis.grid() 或 x.yaxis.grid()
- 保持图表背景干净，仅保留必要的坐标轴线（隐藏 top/right spine）
- 水平条形图（barh）尤其不要添加竖向网格线

`python
# 正确做法：不添加网格线
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# 错误做法（除非客户明确要求）：
# ax.xaxis.grid(True, linestyle='--', alpha=0.3)
`\n\n\n\n### 7.7 学术图表字体铁律（实测验证版）

> 核心原则：rcParams全局字体不可靠！必须用 FontProperties(fname=) 逐一设置。

#### 字体对象定义
`python
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.offsetbox import AnchoredOffsetbox, HPacker, VPacker, TextArea, DrawingArea
import matplotlib.lines as mlines

plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 200

F_SONG = FontProperties(fname=r'C:\Windows\Fonts\simsun.ttc')  # 宋体
F_TNR  = FontProperties(family='Times New Roman')
`

#### 字体规范表
| 元素 | 中文 | 英文/数字 | 字号 |
|------|------|----------|------|
| 标题 | 宋体 | TNR | 10pt |
| 轴标签 | 宋体 | TNR | 9pt |
| 刻度 | - | TNR | 8pt |
| 图例 | 宋体 | TNR | 8pt |
| 标注 | 宋体 | TNR | 8pt |

#### 中英文混排：HPacker
`python
# 标题（如含英文字符如U、AI等）
title_box = HPacker(children=[
    TextArea('中文部分', textprops=dict(fontproperties=F_SONG, fontsize=10)),
    TextArea('U', textprops=dict(fontproperties=F_TNR, fontsize=10)),
    TextArea('中文', textprops=dict(fontproperties=F_SONG, fontsize=10)),
], align='baseline', pad=0, sep=0)
ax.add_artist(AnchoredOffsetbox(loc='upper center', child=title_box, pad=0,
    bbox_to_anchor=(0.5, 1.08), bbox_transform=ax.transAxes, frameon=False))

# 横坐标（中文宋体 + 英文TNR）
xlabel_box = HPacker(children=[
    TextArea('中文标签  ', textprops=dict(fontproperties=F_SONG, fontsize=9)),
    TextArea('log(x+1)', textprops=dict(fontproperties=F_TNR, fontsize=9)),
], align='baseline', pad=0, sep=0)
fig.add_artist(AnchoredOffsetbox(loc='center', child=xlabel_box, pad=0,
    bbox_to_anchor=(0.54, 0.06), bbox_transform=fig.transFigure, frameon=False))

# 纵坐标（HPacker无法旋转90度，用set_ylabel统一宋体）
ax.set_ylabel('审计质量(DA)', fontproperties=F_SONG, fontsize=9, labelpad=8)
`

#### 刻度设置
`python
ax.tick_params(axis='both', labelsize=8)
for lb in ax.get_xticklabels() + ax.get_yticklabels():
    lb.set_fontproperties(F_TNR); lb.set_fontsize(8)
`

#### 图例混排（DrawingArea + HPacker + VPacker）
`python
def make_legend_row(color, ls, cn1, en, cn2):
    da = DrawingArea(25, 8, 0, 0)
    da.add_artist(mlines.Line2D([0,25],[4,4], color=color, linestyle=ls, linewidth=2))
    label = HPacker(children=[
        TextArea(cn1, textprops=dict(fontproperties=F_SONG, fontsize=8, color=color)),
        TextArea(en, textprops=dict(fontproperties=F_TNR, fontsize=8, color=color)),
        TextArea(cn2, textprops=dict(fontproperties=F_SONG, fontsize=8, color=color)),
    ], align='baseline', pad=0, sep=0)
    return HPacker(children=[da, label], align='center', pad=0, sep=4)

row1 = make_legend_row('#C44E52', '-', '高数字化基础（', '+1SD', '）')
row2 = make_legend_row('#4C72B0', '--', '低数字化基础（', '-1SD', '）')
legend_box = VPacker(children=[row1, row2], align='left', pad=0, sep=4)
ax.add_artist(AnchoredOffsetbox(loc='upper left', child=legend_box, pad=0.5,
    bbox_to_anchor=(0.02, 0.98), bbox_transform=ax.transAxes, frameon=False))
`

注意：全角括号（）必须在宋体TextArea中，TNR不含全角字符。

#### 标注混排
`python
ann_box = HPacker(children=[
    TextArea('拐点 ', textprops=dict(fontproperties=F_SONG, fontsize=8, color='#333')),
    TextArea('x*=0.450', textprops=dict(fontproperties=F_TNR, fontsize=8, color='#333')),
], align='baseline', pad=0, sep=1)
ax.add_artist(AnchoredOffsetbox(loc='lower left', child=ann_box, pad=0,
    bbox_to_anchor=(x+0.03, y+0.001), bbox_transform=ax.transData, frameon=False))
`

#### 布局铁律
- 用 ig.subplots_adjust(left=0.14, bottom=0.15, top=0.90, right=0.95) 手动布局
- **禁止 box_inches='tight'**（会压缩手动预留空间导致重叠）
- 保存：ig.savefig('x.png', dpi=200, facecolor='white')

#### 检查清单
1. 标题中英文字体分别正确？
2. 轴标签中英文字体分别正确？
3. 刻度数字全部TNR？
4. 图例中英文字体分离？全角括号在宋体中？
5. 标注中英文字体分离？
6. 没用 bbox_inches='tight'？
7. 横坐标居中不与刻度重叠？

---

## 十一、SPSS 过程数据导出模块

### 11.1 SPSS 风格过程数据 Excel 模板

每次问卷/统计分析，**必须同时生成 SPSS 风格过程数据 Excel**，内容包括：

| Sheet 类型 | 内容 |
|-----------|------|
| 可靠性统计 | 各维度 Cronbach's α |
| 项总计统计 | 校正项总计相关、删项后 α |
| KMO/Bartlett | KMO 整体 + 个别 KMO + 卡方/df/p |
| 描述统计 | N/Min/Max/Mean/SD/Var/Skew/Kurt |
| 相关性 | 三层矩阵：Pearson r + Sig.(双尾) + N |
| t检验-组统计 | N/均值/标准差/标准误均值 |
| t检验-检验结果 | Levene F/Sig + 等方差/不等方差两行(t/df/p/均值差/CI) |
| ANOVA-描述 | 各组 N/Mean/SD/SE/95%CI/Min/Max + 合计 |
| ANOVA-齐性检验 | Levene 统计量/df1/df2/Sig |
| ANOVA-方差分析 | SS/df/MS/F/Sig（组间/组内/总计） |
| ANOVA-事后LSD | (I)组-(J)组 均值差/SE/Sig/95%CI |
| 回归-模型摘要 | R/R²/Adj.R²/SE/Durbin-Watson |
| 回归-ANOVA | SS/df/MS/F/Sig |
| 回归-系数 | B/SE/β/t/Sig/95%CI/Tolerance/VIF |
| 回归-残差统计 | 预测值/残差/标准化预测值/标准化残差 |
| 因子-总方差解释 | 全部成分的初始特征值 + 提取/旋转载荷平方和 |
| 因子-成分矩阵 | 未旋转因子载荷 |
| 因子-旋转成分矩阵 | Varimax 旋转后因子载荷 |
| 因子-共同度 | 初始=1 + 提取共同度 |
| CFA拟合指标 | χ²/df/GFI/CFI/TLI/RMSEA/SRMR/AIC/BIC |

### 11.2 生成 SPSS .sps 语法文件

> ⚠️ **编码铁律**：.sps 文件必须用 **GBK 编码**保存，UTF-8 会在 SPSS 中显示乱码。

```python
# 保存为 GBK
with open('analysis.sps', 'w', encoding='gbk') as f:
    f.write(syntax_content)
```

**语法模板要点**：

```spss
* 读取数据.
GET FILE='path/to/data.sav'.

* 信度分析.
RELIABILITY /VARIABLES=Q1 Q2 Q3
  /SCALE('维度名') ALL
  /MODEL=ALPHA
  /STATISTICS=DESCRIPTIVE SCALE
  /SUMMARY=TOTAL.

* 因子分析（含 KMO）.
FACTOR /VARIABLES=Q1 TO Q20
  /PRINT INITIAL KMO EXTRACTION ROTATION
  /CRITERIA FACTORS(5) ITERATE(25)
  /EXTRACTION PC
  /ROTATION VARIMAX.

* 独立样本 t 检验.
T-TEST GROUPS=gender(1 2)
  /VARIABLES=dim1 dim2 dim3
  /CRITERIA=CI(.95).

* ANOVA + LSD 事后比较.
ONEWAY dim1 dim2 dim3 BY age
  /STATISTICS DESCRIPTIVES HOMOGENEITY
  /POSTHOC=LSD ALPHA(0.05).

* 多元回归.
REGRESSION
  /STATISTICS COEFF OUTS R ANOVA COLLIN TOL
  /DEPENDENT satisfaction
  /METHOD=ENTER dim1 dim2 dim3
  /RESIDUALS DURBIN.

* 保存输出.
OUTPUT SAVE OUTFILE='path/to/output.spv'.
```

**SPSS 命令行运行**（SPSS 27 无 `statisticsb`）：
- `stats.com` 不支持 `-f`/`-type`/`-out` 参数
- 正确方式：用 `stats.com syntax.sps` 打开 → SPSS GUI 中运行全部
- 或在语法末尾写 `OUTPUT SAVE` 自动保存 .spv
