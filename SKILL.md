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


## 0.0 工作区整洁规则

- 在用户项目目录内执行 `ace` 任务时，**所有新建分析脚本、清洗脚本、绘图脚本、临时验证脚本，默认统一放入项目内的 `scripts/` 文件夹**，不要直接散落在主目录。
- 若任务较大或包含多个子任务，允许在 `scripts/` 下继续分支，例如：
  - `scripts/eda/`
  - `scripts/regression/`
  - `scripts/2026-04-16_rice_quality/`
- 若项目本身已经存在集中管理脚本的目录，则优先复用该目录并继续分层；若没有，则主动创建 `scripts/`。
- 主目录应尽量只保留数据、文稿、最终交付物和必要配置文件，避免被一次性脚本、临时调试文件污染。
- 本 Skill 自带的模板脚本仍位于 Skill 包内的 `scripts/`，而**针对当前用户任务新生成的脚本**应放在用户项目自己的集中脚本目录中。


## 0. 附带代码模板

- `scripts/precheck.py`：环境、文件、依赖与输入前置检查
- `scripts/check_assumptions.py`：正态性、方差齐性、VIF 等前置检验
- `scripts/questionnaire_pipeline.py`：问卷全套流水线（清洗、描述、信度、KMO/Bartlett、EFA）
- `scripts/anova_pipeline.py`：方差分析、LSD、多重比较、结果输出
- `scripts/generate_spss_syntax.py`：SPSS 语法生成
- `scripts/three_line_table.py`：三线表输出
- `scripts/merge_report.py`：结果合并与报告装配
- `scripts/verify_report.py`：报告一致性核查

- `code_library/descriptive.py` / `correlation.py` / `ttest.py` / `anova.py`：基础统计函数
- `code_library/regression.py` / `did.py` / `mediation.py`：实证分析核心函数
- `code_library/survey.py`：问卷信效度、EFA、AVE/CR
- `code_library/ml_pipeline.py`：机器学习基线与调参代码库
- `code_library/plot_bindent.py`：学术绘图初始化、字体、配色与图模板
- `code_library/report_builder.py` / `word_utils.py`：Word 报告写作与格式辅助

使用原则：
- `scripts/` 优先用于可直接运行的流水线与检查脚本
- `code_library/` 优先用于按需 import 的函数与片段库
- 优先复用这些入口并按任务改参数，不要每次从零重写

## 0.1 模板引擎与报告模板预设

- `_ace_templates/engine.py`：模板装配入口，用于按预设生成结构化交付
- `_ace_templates/text_library/blocks.py`：标准分析文字块库，适合问卷、信效度、相关、回归、中介等段落复用
- `_ace_templates/text_library/word_engine.py`：Word 段落与格式写入辅助
- `_ace_templates/format_presets/`：报告格式预设
  - `report_delivery.json`：客户交付报告
  - `spss_mimic.json`：SPSS 风格输出
  - `thesis_songti.json`：论文宋体风格
  - `thesis_strict.json`：更严格的论文格式
  - `compact_mini.json`：轻量简版
- `_ace_templates/templates/`：场景化流水线模板
  - `A1_questionnaire`
  - `A2_questionnaire_mediation`
  - `B1_cross_section`
  - `C1_anova`
  - `D1_medical`

- 使用原则：
  - 若任务需要“脚本 + Word 报告 + 固定格式预设”一体化交付，优先考虑 `_ace_templates`
  - 若只是常规单次统计分析，优先复用 `scripts/` 与 `code_library/`，避免过度模板化

## 0.1.1 Word 默认格式规范

- 对中文论文、分析报告、提纲、三线表配套说明等 Word 输出，默认优先使用 `_ace_templates/format_presets/thesis_strict.json`。
- 若用户明确要求更常见的毕业论文宋体版式，可退回 `thesis_songti.json`。
- 默认规范如下：
  - 中文标题与各级标题：`黑体`、黑色、加粗
  - 正文中文：`宋体`
  - 正文英文与数字：`Times New Roman`
  - 任何位置的英文和数字都必须使用 `Times New Roman`，包括标题中的英文、表头英文、图例、年份角标、括号中的英文单位、处理缩写（CK、GA、BR、MeJA、6-BA）和显著性字母。
  - 正文：首行缩进 `2` 字符，`1.5` 倍行距，段前段后 `0`
  - 表题：黑体；表内文字：宋体 + Times New Roman
- 禁止依赖 Word 主题字体或系统默认东亚字体，避免出现 `MS Gothic`、彩色标题或模板化样式污染正式文稿。
- 若用户提供学校模板、期刊模板或既有格式文件，则以用户模板优先覆盖此默认规范。

## 0.1.2 图表与三线表默认规范

- 正式论文图片文件本体默认不放图题，图题统一写在 Word 正文中。
- 坐标轴名称必须完整；有单位的指标必须显式写单位。
- 单指标主图默认优先使用原始均值 ± 误差；效应总览图可用相对 CK 变化百分比；综合评价图可用标准化指数。
- 图例默认放在不遮挡数据的位置，优先右上角或左上角；必要时应主动调大 Y 轴范围。
- 柱状图若存在多处理比较，默认优先使用字母显著性分组，不只保留误差线。
- Word 中正式表格默认使用三线表，不使用 `Table Grid` 式网格表。
- 需要 Word 输出时，优先复用 `scripts/three_line_table.py` 或等价三线表逻辑，不要临时生成普通网格表。
- 若未被用户明确要求增加分隔线，三线表默认只保留顶线、表头下横线和底线，不额外添加中间横线、虚线或分块线。
- Word 中表格默认整体居中；若表后需要说明，表注必须紧跟对应表格下方，不得挪到正文末尾或下一张表之后。
- 对描述统计表、样本特征表、单因素比较表等分组表，默认将“变量”和“类别/组别”拆成不同列，不把变量名与类别值混在同一列；变量名默认只在该变量首行出现，后续类别行留空或按用户提供模板排版。
- 若交付的是“单一核心因变量”的单因素分析表，默认优先采用 `变量 | 组别 | 例数 | 因变量均值±标准差 | t/F | P` 的纵向分组样式；统计量与 P 值仅在该变量首行显示，后续组别行留空，默认对齐参考常见医学论文表格格式。
- Word 表格的“默认居中”不仅指表格对象整体居中，也指表头与单元格文字默认居中；除非用户明确要求左对齐，不要只把表框居中而把表内文字保留左对齐。
- 客户版 Word 报告中，表格、表注、结果分析之间默认顺序为：表格 → 表注 → 空一行 → 结果分析。
- 图表中英混排时必须逐元素指定字体：中文用 `宋体/黑体`，英文和数字用 `Times New Roman`；不得依赖系统自动回退或主题字体。
- 若交付对象是客户或外部收件人，Word/PDF 正文默认禁止出现“给内部看的元说明”，例如“本次参考截图/文献”“变量按当前字段重建”“以下为说明”“本轮修正了”等过程性文字。
- 客户版分析交付正文默认只保留：标题、表格/图、表注、结果分析、必要统计口径与直接结论；方法来源、截图参考、核查说明、版本差异等内容应写入核查日志、脚本注释或项目记录，不进入客户正文。

## 0.2 多 Agent 补充路由

| 任务类型 | 触发方式 | 说明 |
|---------|---------|------|
| 多 Agent 分析编排 | 条件式触发 | 在当前环境支持并行代理且任务预计输出不少于 2 个产物时，优先尝试多 Agent |

## 0.3 多 Agent 编排（轻量三省六部版）

- 默认策略：条件式多 Agent，不是所有任务一开始都并行
- 启动条件：
  - 存在 2 个及以上彼此独立的子任务，可并行推进
  - 主任务规模较大，且可拆为实现 / 审查 / 测试 / 检索中的并行支线
  - 需要外部检索、代码实现、质量校验同时推进以缩短总耗时
  - 数据分析任务且预计输出不少于 2 个产物，例如脚本+报告、表格+报告
  - 用户明确要求多 Agent / 三省六部模式
- 不默认并行的场景：
  - 单文件小改、一次性问答、简单润色、几分钟可完成的小修复
  - 强串行依赖任务：下一步完全依赖上一步结果
  - 根因尚未定位的疑难 bug：先由主 Agent 本地排查，再决定是否拆分
- 推荐角色：
  - 主 Agent：Planner / Integrator，负责拆任务、保上下文、做最终合并决策
  - Side Agent 1：Context / Research，负责文档、GitHub、代码库定向检索
  - Side Agent 2：Reviewer / Tester，负责静态审查、回归风险和验证
  - 需要时再增加 Worker，但必须明确文件边界，避免多人改同一处
- 执行铁律：
  - 先由主 Agent 完成最小必要的本地理解，再决定是否派生子 Agent
  - 子 Agent 只做边界清晰、可独立交付的子任务
  - 多个 Worker 并行时，写入范围必须互不重叠
  - 非阻塞原则：派发后主 Agent 继续做本地工作，不要立刻 wait
  - 仅当主流程被结果卡住时才等待子 Agent 返回
  - 不重复劳动：已委派出去的子任务，主 Agent 不再自己重做
- 角色映射：
  - 中书省 = Planner / Integrator
  - 门下省 = Reviewer / Gatekeeper
  - 尚书省 = Dispatcher
  - 六部 = Researcher / Builder / Tester / Writer / Data Analyst / Verifier

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

### 4.5.1 中介效应交付默认口径

- 若客户给的参考 `SPV` / 截图只有 `c路径(X→Y)`、`a路径(X→M)`、`b+c'路径(X+M→Y)` 三段回归，则默认先按 **Baron & Kenny / 逐步回归口径** 对齐，不要一上来强切 `PROCESS`。
- 若客户明确要“Bootstrap 中介效应”“间接效应置信区间”“BootLLCI / BootULCI”，或需要更规范地证明间接效应显著，再追加 `PROCESS Model 4` 或等价 bootstrap 输出。
- 对客户最稳的默认交付是：**三步回归表 + Bootstrap 间接效应表** 同时保留；若客户只认传统 SPSS 表，再裁掉 bootstrap 部分。
- 报告写法中要严格区分：总效应 `c`、直接效应 `c'`、间接效应 `ab`、以及 `BootLLCI / BootULCI`；不要用零阶相关或普通回归系数替代间接效应表述。
- 若 SPSS / PROCESS 对长变量名不稳定，先生成短别名再跑，例如 `X_mean`、`M_mean`、`Y_mean`；正式报告里再还原成中文变量名。


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


### 5.1.1 兼容性 fallback

如果 `factor_analyzer` 与当前 `scikit-learn` 版本不兼容，按以下顺序降级，不要卡死在环境问题上：

1. 保留 `Cronbach's α`
2. 保留 `KMO + Bartlett`
3. 因子载荷改用 `PCA + varimax rotation` 生成探索性载荷近似结果
4. 在结果说明中明确写“为兼容当前环境，旋转载荷采用 PCA+varimax 近似输出”

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

- 默认紧贴对应表格下方；除非用户明确要求，表注不单独漂移到结果段落之后或文末集中放置。


---


## 七、学术绘图模块


### 7.1 全局绘图初始化（每个脚本开头必加）

核心原则：

- 不要用 `rcParams['font.sans-serif']` 全局兜底中文字体
- 中英文混排时，优先逐元素指定：中文宋体/黑体，英文和数字 Times New Roman
- 默认 `dpi=300`，默认白底导出
- 布局优先手动控制，避免依赖 `bbox_inches='tight'`

最小骨架：

```python
from plot_bindent import FONT_SONG, FONT_HEI, FONT_TNR
from plot_bindent import grouped_bar, line_with_sem, correlation_heatmap

ax.set_title('返青期', fontproperties=FONT_HEI, fontsize=11)
for label in ax.get_xticklabels() + ax.get_yticklabels():
    label.set_fontproperties(FONT_TNR)
fig.savefig('output.png', dpi=300, facecolor='white')
```

完整实现入口：

- `code_library/plot_bindent.py`
- `scripts/plot_utils.py`

若任务需要图表与 Word 报告一体化交付，再联动：

- `_ace_templates/text_library/word_engine.py`

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

> 字体、导出、网格线规则统一遵循 7.1 / 7.5 / 7.8，不在本节重复展开长代码。

推荐图种与用途：

- 分组柱状图 + 误差棒：组间均值比较
- 折线图 + 标准误：前后测、时间趋势
- 相关矩阵热力图：多变量相关展示
- DID 系数图：动态效应与事件研究
- ROC 曲线：医学/诊断/分类模型判别能力

最小骨架：

```python
from plot_bindent import grouped_bar, line_with_sem, correlation_heatmap

fig, ax = grouped_bar(data, groups, categories, ylabel='得分', title='组间比较')
fig.savefig('grouped_bar.png', dpi=300, facecolor='white')
```

实现入口：

- `code_library/plot_bindent.py`
- `scripts/plot_utils.py`

使用要求：

- 图种选择先由研究问题决定，不为“好看”而堆图
- 中文/英文/数字字体规则统一遵循 7.1
- 导出规则统一遵循 7.5

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
fig.savefig('figure1.png', dpi=300,
            facecolor='white', edgecolor='none')

# 高清版（印刷用）
fig.savefig('figure1_hires.tiff', dpi=300)


# 矢量图（编辑用）

fig.savefig('figure1.svg')

fig.savefig('figure1.pdf')

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


### 7.7 学术图表字体铁律（精简版）

- 核心原则：中文字体不要靠 `rcParams['font.sans-serif']` 全局兜底，优先使用 `FontProperties(fname=...)` 逐元素指定。
- 中文默认：宋体 / 黑体；英文与数字默认：Times New Roman。
- 刻度数字、统计量、英文缩写统一使用 TNR。
- 图例、标题、标注中若中英混排，按元素拆分设置字体，不要混用单一字体硬顶。
- 布局优先手动控制：`fig.subplots_adjust(...)`；导出时默认 `facecolor='white'`。
- 若版式依赖手工预留空白，禁止 `bbox_inches='tight'`。

### 7.8 绘图网格线规范

- 学术图表默认不加背景网格线。
- 除非用户或客户明确要求，否则不要调用 `ax.xaxis.grid()` / `ax.yaxis.grid()`。
- 保持图表背景干净，仅保留必要坐标轴线；通常隐藏 `top/right spine`。
- 水平条形图（`barh`）尤其不要加竖向网格线。

---

## 八、结果分析写作风格


### 要求


- **一整段连贯文字**，不按指标分列
- 默认规则：**同一分析模块的结果解读应尽量合并为 1 个连续段落**。除非用户明确要求分点、分段或逐指标拆写，否则不要把描述统计、相关分析、回归分析、稳健性分析等结果拆成多段模板句连排。
- 连续段落不是堆砌句子：同一段内部按“核心结果 → 补充结果 → 解释/收束”顺序组织，避免每句都以“由表X可知”“此外”“综上”机械起头。

- 首行缩进 2 字符，客观陈述

- 去 AI 味：删"值得注意的是""综合来看"，统一"降低"不用"下降"
- 若交付物是正式文稿或客户版分析，在数值与结论核对完成后，**默认优先再走一轮 `awesome-ai-research-writing` 风格润色**；`phd-writing` / `scholar-write` 仅作备选或补充，重点压缩模板化句式、减少空泛过渡词、校正因果措辞，并保持统计表述与 `p` 值完全一致。
- 若交付物面向客户，结果分析应直接进入数据结论，不写“这里这样做是因为”“本次采用了某截图思路”“变量依据当前问卷重建”等面向内部沟通的话。
- 若交付物面向客户，默认不写“以下为说明”“本次分析采用”“参考某截图/文献”“变量按当前字段重建”等面向委托方无价值的过程句。


### 段落结构


1. "由表X可知" + 宏观概述哪些指标受显著影响

2. **百分比**描述组间差异（不逐个列均值±标准差）

3. 过渡词：首个直接跟概述，中间"此外"，末尾"就XX而言"

4. 交互效应：差异最大/最小时间点

5. 结尾"这表明..."因果总结


---


## 九、机器学习建模模块


### 9.1 数据预处理 Pipeline

保留信息：

- 先划分训练集/测试集，分类任务优先 `stratify=y`
- 数值列与分类列分流处理
- 缺失值插补、标准化、OneHot 编码要写进可复现流程

最小骨架：

```python
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
```

完整实现入口：

- `code_library/ml_pipeline.py`
- 如需可直接运行的完整项目脚手架，优先走项目内脚本或 `_ace_templates`

### 9.2 随机森林分类

默认步骤：

1. 建立 `preprocessor + classifier` 的 Pipeline
2. 先跑随机森林基线
3. 输出 `Accuracy / Precision / Recall / F1 / AUC`
4. 若类别不平衡，优先考虑 `class_weight='balanced'`

完整实现入口：

- `code_library/ml_pipeline.py`

### 9.3 随机森林回归

- 适合连续因变量预测
- 默认报告 `R² / RMSE / MAE`
- 若只做基线比较，先与线性回归或 GBDT 保持同一切分口径

完整实现入口：

- `code_library/ml_pipeline.py`

### 9.4 超参调优

适用场景：

- `GridSearchCV`：参数空间小、需要穷举
- `RandomizedSearchCV`：参数空间大、先做粗搜
- `Optuna`：默认推荐，效率更高

保留要求：

- 记录搜索空间
- 记录最优参数
- 记录交叉验证得分
- 若用了 Optuna，建议保留优化历史图和参数重要性图

完整实现入口：

- `code_library/ml_pipeline.py`

### 9.5 交叉验证

- 模型对比时，至少报告交叉验证均值与标准差
- 不要只报一次测试集分数
- 分类任务优先分层交叉验证

完整实现入口：

- `code_library/ml_pipeline.py`

### 9.6 特征重要性

默认解释顺序：

1. `sklearn` 内置重要性：最快，适合初筛
2. `Permutation Importance`：更稳健，适合正式报告
3. `SHAP`：解释性最强，适合答辩/论文/客户要求可解释性时

何时必须用 SHAP：

- 用户明确要求“解释模型”
- 需要说明单个特征如何影响预测
- 需要做论文或答辩层面的可解释性展示

完整实现入口：

- `code_library/ml_pipeline.py`

### 9.7 ML 可视化模板

推荐图种：

- 特征重要性柱状图：解释 Top 特征
- 混淆矩阵：看分类错分结构
- 学习曲线：诊断过拟合/欠拟合
- 多分类 ROC：看类别层面的判别能力

默认要求：

- ML 图仍然遵循第七章的字体、导出、网格线规范
- 如果只交最小结果，优先保留：混淆矩阵 + 特征重要性图
- 若用户强调模型解释，再补 SHAP 图和学习曲线

完整实现入口：

- `code_library/ml_pipeline.py`
- 如需统一图风格，可复用 `scripts/plot_utils.py`

### 9.8 其他常用模型（快速切换）

可切换模型：

- `XGBoost`：通常作为随机森林之后的增强对照
- `SVM`：特征维度高、边界复杂时可试
- `GBDT`：树模型的轻量替代

统一要求：

- 模型对比时，统一训练/验证切分与交叉验证口径
- 不要只比单次测试集分数，至少报告交叉验证均值和波动

完整实现入口：

- `code_library/ml_pipeline.py`

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

本节与“自动化分析工作流 -> Step 6. 输出交付”重复，默认以 Step 6 为准；若用户只要部分交付物，再按需求裁剪。


---


## 十一、SPSS 原生输出专项工作流 (针对挑剔客户)


### 11.1 环境限制与结论

由于该机器上的 SPSS 27 底层 Java 组件 Bug，**无法使用 `stats.exe -production silent` 或任何无头模式 (Headless / Silent) 自动静默导出表单**（运行时会抛出 `NullPointerException` 或卡死）。因此，**禁止尝试在后台悄悄调 SPSS**。


### 11.2 标准化替代方案（脑力代码化，体力手动化）

当客户明确要求提交 SPSS 原始分析过程和结果表时，必须遵循以下“代码生成+手动执行”工作流：


1. **Python 生成语法**：读取客户数据后，使用 Python 按照要求生成完整的 SPSS Syntax 语法脚本（`.sps`）。

   - `.sps` 默认采用 `utf-8-sig + CRLF` 写出；本机 `SPSS 27` 对中文变量名、中文路径和中文注释的兼容性以此方案最稳。
   - 回归前必须按当前 `.sav` 实际字段核对变量名，并排除零方差哑变量。
   - 手动在 SPSS GUI 中直接运行 `.sps` 时，导出区可保留 `OUTPUT EXPORT` 和 `OUTPUT SAVE`，不要附带大段说明文字进入 `Viewer`。
   - 若通过 SPSS Python 接口批量生成 `.spv`，默认优先 `OMS /DESTINATION FORMAT=SPV`，因为本机已实测 `SpssClient + OUTPUT SAVE` 在某些回归类表上会出现“可能由更高版本创建”的伪兼容提示。

   - 代码中需包含 `GET DATA` 来读取客户的数据文件。

   - 包含各种分析命令（如 `FREQUENCIES`, `DESCRIPTIVES`, `GLM` 等）。

   - **结尾必须**附上自动导出到同目录 Excel 或 Word 的命令：

     ```spss

     OUTPUT EXPORT

       /CONTENTS  EXPORT=ALL  LAYERS=PRINTSETTING  MODELVIEWS=PRINTSETTING

       /XLSX DOCUMENTFILE='C:\\绝对路径\\导出的结果表.xlsx'

       OPERATION=CREATEFILE.

     ```

2. **交付语法进行验证**：将这段 `.sps` 脚本内容交给本机操作人，在 SPSS 界面中手动打开并执行。

3. **人工"一键点击"**：在 SPSS 中新建或打开语法文件，贴入代码，点击“运行” -> “全部”，即可完美生成无任何误差的原版结果报表。

### 11.3 SPV 导出双路线（2026-04-19 实测补充）

- 路线 A：`SpssClient.RunSyntax(...) + OUTPUT SAVE OUTFILE='xxx.spv'.`
  - 优点：理论上更接近 GUI 输出，中文标题更完整。
  - 风险：本机在回归类对象上可能出现“无法显示这个表（这个表可能是使用更高版本创建的）”的伪兼容提示。
  - 结论：仅作回退方案，不再作为默认推荐。

- 路线 B：`spss.Submit(...) + OMS /DESTINATION FORMAT=SPV OUTFILE='xxx.spv'.`
  - 优点：本机 SPSS 27 下兼容性更稳，回归表可正常打开。
  - 风险：输出风格更接近 OMS 捕获结果，个别标题可能不如 GUI 路线自然。
  - 结论：当前机器默认优先路线 B。

- 默认决策：
  - `手动打开 .sps 在 GUI 里直接运行`：保留 `OUTPUT SAVE` 没问题。
  - `用 SPSS Python 接口批量产出 .spv`：默认优先 `OMS -> SPV`。

### 11.4 PROCESS v5 中介语法补充（2026-04-19 实测补充）

- **宏载入方式**：
  - 在本机 SPSS Python / 批量入口里，默认用 `INSERT FILE='...\\process.sps'.`
  - 不要在该入口里优先用 `INCLUDE '...\\process.sps'.`，本机实测容易报 `Cannot complete this action while the syntax is incomplete.`

- **v5 语法口径**：
  - 不再沿用旧版 `PROCESS vars = ... /y = ... /x = ...` 写法；本机实测会触发 `You are using outdated syntax`。
  - 默认改写为：

    ```spss
    PROCESS y = Y_mean
     /x = X_mean
     /m = M_mean
     /cov = gender age edu tenure company position
     /model = 4
     /boot = 5000
     /seed = 20260419
     /total = 1
     /normal = 1
     /effectsize = 1.
    ```

- **变量名限制**：
  - `PROCESS v5` 在本机对变量名长度更敏感，默认按“变量名不超过 8 个字符”处理。
  - 若原始变量名过长，先生成短变量名，例如 `X_mean / M_mean / Y_mean`，再交给 `PROCESS`。

- **与参考件对齐**：
  - 若客户给的参考 `SPV` 本质上是三步回归而不是 `PROCESS`，正式交付时应先复现 `c路径`、`a路径`、`b+c'路径` 三张回归表，再视需求追加 `PROCESS Bootstrap` 结果。

- **回归语法顺序**：
  - `REGRESSION` 中的 `/STATISTICS`、`/CRITERIA`、`/NOORIGIN` 应放在 `/DEPENDENT` 前，避免 `Invalid REGRESSION subcommand order` 警告污染 `Viewer`。


---


## 自动化分析工作流

当用户提出“自动分析”“跑分析”“出结果”“全套分析”等请求时，默认启用以下 6 步固定流程。该流程适用于问卷分析、描述统计、相关分析、ANOVA、回归、DID、基础机器学习与常见实证任务。

### 触发词

- 自动分析
- 跑分析
- 出结果
- 全套分析

### 默认原则

- 优先复用当前技能包中已有实现入口，不从零重写分析主流程：
  - 先运行 `scripts/precheck.py`，确认依赖、字体、输入文件和输出目录都可用
  - 前置检验：`scripts/check_assumptions.py`
  - 问卷分析：`scripts/questionnaire_pipeline.py` / `code_library/survey.py`
  - 方差分析：`scripts/anova_pipeline.py` / `code_library/anova.py`
  - 回归 / DID / 中介：`code_library/regression.py` / `code_library/did.py` / `code_library/mediation.py`
  - 机器学习：`code_library/ml_pipeline.py`
- 只有当现有模板无法覆盖任务时，才允许做最小范围补丁或增加薄封装。
- 中介、调节、被调节中介默认先用 `Bootstrap 500 ~ 1000` 调试，最终交付再升到 `5000`。
- 每次分析结束后，必须执行 Step 5 结果核查。
- 如果 Step 5 发现问题，必须自动回溯到 Step 4 修正；必要时可回溯到 Step 2 或 Step 3，最多回溯 `2` 次。
- 最终固定交付 4 类结果：终端摘要 + Excel 统计表 + Word 三线表报告 + 核查日志。

### Step 1. 探查数据

- 识别文件类型、工作表、变量名、编码方式、缺失值、异常值、样本量和量表范围。
- 判断数据属于：问卷原始数据、问卷汇总表、实验/面板数据、分类/回归建模数据。
- 识别因变量、自变量、分组变量、控制变量、题项维度、反向题和主键字段。
- 若只有汇总表而无原始明细，明确标注可做与不可做的分析边界。

### Step 2. 选方法

- 基于数据结构自动选择最合适的方法，不堆砌分析。
- 优先映射到现有实现入口：
  - 前置检验 -> `scripts/check_assumptions.py`
  - 问卷流水线 -> `scripts/questionnaire_pipeline.py` 或 `code_library/survey.py`
  - 方差分析 -> `scripts/anova_pipeline.py` 或 `code_library/anova.py`
  - 描述/相关 -> `code_library/descriptive.py` + `code_library/correlation.py`
  - OLS/Logit/分层回归 -> `code_library/regression.py`
  - DID/面板/2SLS -> `code_library/did.py`
  - 中介 -> `code_library/mediation.py`
  - 机器学习 -> `code_library/ml_pipeline.py`
- 如果任务跨多个模块，按“描述 -> 检验 -> 主模型 -> 稳健性/补充分析”顺序组织。
- 选定方法后，要同步确定输出表格口径、显著性标记规则和图表口径。

### Step 3. 前置检验

- 在正式分析前，按方法执行必要检验：
  - 问卷/量表：反向题处理、量表汇总、信度、可选 KMO/Bartlett
  - 均值比较：正态性、方差齐性、组间样本量检查
  - 回归：缺失机制、异常值、多重共线性、变量编码、必要的稳健标准误
  - DID/面板：主键唯一性、时间字段、处理组/对照组标记、政策时点正确性
  - 机器学习：标签分布、训练/验证切分、特征泄漏检查
- 前置检验不通过时，不直接输出结论，先修正数据或切换到更合适的方法。

### Step 4. 执行分析

- 优先直接运行或小幅改造现有模板脚本，不重新发明主逻辑。
- 结果至少应包含：
  - 关键统计量
  - 显著性结果
  - 结果表格
  - 必要图表或模型诊断信息
- 需要多模型时，保持变量命名、样本口径、显著性标记和导出格式一致。

### Step 5. 结果核查

每次分析完成后必须自动运行核查清单，并写入核查日志。核查至少包括以下 4 类：

1. 数值合理性
- 均值是否落在量表范围内
- 标准差、比例、系数、概率值是否存在明显越界或不可能值
- 反向题处理后是否仍出现方向异常

2. 方向一致性
- 系数方向是否符合理论预期或题意
- 反向题、负向指标、反向编码变量的解释方向是否一致
- 图表、正文、表格中的方向表述是否一致
- 若零阶相关方向与控制后回归方向不一致，正文必须以对应模型结果为准，不得沿用相关分析方向

3. 完整性校验
- `N` 是否前后一致
- 频数合计是否等于样本量
- 百分比是否加总到 `100%`，若存在四舍五入误差需注明
- 分组样本量、回归样本量、有效样本量是否对得上

4. 显著性一致性
- 星号标记与 `p` 值是否一一对应
- 置信区间、标准误、t/z/F/卡方值与显著性结论是否冲突
- 表格、图注、正文中的显著性结论是否一致

若核查失败：

- 第一次失败：回溯到 Step 4 修正分析或导出逻辑，然后重新核查。
- 第二次失败：允许回溯到 Step 2 或 Step 3，调整方法或前置处理后重跑。
- 最多回溯 `2` 次；若仍失败，停止自动定稿，明确列出未通过项与建议人工复核点。

### Step 6. 输出交付

默认输出以下 4 项：

1. 终端摘要
- 用简洁文字汇总样本量、方法、核心结果、显著性与一句话结论。

2. Excel 统计表
- 输出描述统计表、相关矩阵、ANOVA 表、回归表、模型评估表等可复用结果表。

3. Word 三线表报告
- 输出适合论文/结题材料的三线表和结果解读段落。
- 若报告含样本特征表、描述统计表或单因素比较表，默认优先采用“变量列 + 类别列”拆分结构，再补频数/百分比或均值±标准差等统计列，不把变量名与类别标签塞进同一列。
- 结果解读段落默认按“每个模块 1 个连续段落”生成，不拆成多段模板化短句。
- 若用于正式提交或老师审阅版，默认在导出前补一轮写作润色，优先消除模板痕迹、过度分段和 AI 味表述。

4. 核查日志
- 单独记录核查项目、是否通过、发现的问题、修正动作、回溯次数和最终状态。

### 执行约束

- 没有完成 Step 5 核查前，不得宣称“分析完成”。
- 没有生成核查日志前，不得交付最终版结果。
- 如果用户只给汇总表，必须先说明只能做描述性与汇总级分析，不能伪造原始数据层面的显著性检验。

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v6.7 | 2026-04-19 | 补充客户版描述统计/样本特征/单因素比较表格式：变量与类别默认分列，变量名仅首行显示；表格居中默认同时包含表框与单元格文字居中 |
| v6.6 | 2026-04-19 | 补充客户版 Word 交付铁律：三线表默认只保留三条线、表格整体居中、表注紧跟表格下方；客户版结果分析禁放元说明；默认写作技能切换为 `awesome-ai-research-writing` |
| v6.5 | 2026-04-17 | 强化结果写作规则：同一分析模块默认输出连续段落；正式交付前默认补一轮 `phd-writing` / `scholar-write` 风格润色 |
| v6.4 | 2026-04-16 | 清理乱码与错位章节；引入模板引擎说明；统一图表导出规则并去除与 `bbox_inches='tight'` 的冲突示例 |
| v6.3 | 2026-04-15 | 新增多 Agent 分析编排（轻量三省六部版）与数据分析双产物默认并行触发规则 |
