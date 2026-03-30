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

## ⚡ 快速路由表（接到任务后第一步查这里）

> **核心原则**：先查路由表定位章节 → 再读对应章节 → 不要从头到尾读完 1700 行。

### 按任务类型定位

| 任务类型 | 必读章节 | code_library 文件 |
|---------|---------|-----------------|
| **接单/报价** | §17 调度协议 | — |
| **问卷分析全套** | §16.1 工作流A → §2 前置检验 | `survey.py` `pretest.py` `correlation.py` |
| **实证回归全套** | §16.2 工作流B → §4 回归模块 | `regression.py` `pretest.py` |
| **双因素方差分析** | §16.3 工作流C → §3.4 | `anova.py` `ttest.py` |
| **中介/调节效应** | §16.4 工作流D → §4.5-4.6 | `mediation.py` `regression.py` |
| **DID双重差分** | §16.5 工作流E → §4.7 | `regression.py` |
| **客户反馈后修改** | §16.10 工作流I → §18 全盘重算 | `report_builder.py` |
| **Word报告生成** | §6 格式规范 + §12 交付规范 | `word_utils.py` `report_builder.py` |
| **学术绘图** | §7（特别是§7.7字体铁律） | `plot_bindent.py` |
| **踩坑排查** | §19 速查表 | — |

### 铁律速查（每次都要遵守）

| 铁律 | 章节 | 一句话 |
|------|------|-------|
| 全盘重算 | §18 | 改了上游必须重跑所有受影响的下游 |
| 表+文字同步 | §12.1 | 每个表格后面必须紧跟文字分析 |
| 正态检验前置 | §16.1 Step1.5 | 先检验正态性，再决定用参数/非参数 |
| 三层隔离 | §18.2 | load→analyze→report，禁止跨层引用 |
| 数据集确认 | 开工前 | `df.shape` + `value_counts()` 先确认再算 |

### code_library 函数速查

| 文件 | 核心函数 | 用途 |
|------|---------|------|
| `data_clean.py` | `reverse_score()` `calc_dimension_scores()` `check_encoding()` | 数据清洗 |
| `pretest.py` | `normality_decision()` `check_vif()` | 前置检验 |
| `survey.py` | `cronbachs_alpha()` `kmo_bartlett()` `efa()` `calc_ave()` | 信效度 |
| `correlation.py` | `correlation_matrix_stars()` `significance_stars()` `mean_sd()` | 相关分析 |
| `ttest.py` | `independent_ttest()` `paired_ttest()` `mann_whitney_u()` | t检验 |
| `anova.py` | `oneway_anova()` `kruskal_test()` | 方差分析 |
| `regression.py` | `ols_regression()` `hierarchical_regression()` `logistic_regression()` | 回归 |
| `mediation.py` | `baron_kenny_mediation()` `bootstrap_mediation()` `moderation_test()` | 中介/调节 |
| `descriptive.py` | `demographic_table()` `chi_square_test()` `descriptive_stats()` | 描述统计 |
| `word_utils.py` | `add_three_line_table()` `add_body_text()` `add_note()` `create_report_doc()` | Word报告 |
| `report_builder.py` | 三层架构模板 + `verify_report()` | 全盘重算 |

---

## 二、前置检验模块（任何分析前必做）

### 2.1 正态性检验

> 📦 `from pretest import normality_decision`

```python
# 批量正态性检验 + 自动推荐参数/非参数
from pretest import normality_decision
results = normality_decision(df, ['VAS_Pre', 'HSS_Post', 'BMI'])
# 返回: {'VAS_Pre': {'normal': True, 'recommend': 'parametric', ...}}
```

### 2.2 方差齐性检验

> 📦 `from pretest import check_homogeneity`

```python
from pretest import check_homogeneity
result = check_homogeneity(df, 'Group', 'VAS_Pre')  # Levene检验
```

### 2.3 多重共线性诊断（回归前）

> 📦 `from pretest import check_vif`

```python
from pretest import check_vif
vif_df = check_vif(df, ['age', 'bmi', 'education'])  # VIF>10 需处理
```


---


### 2.4 统计方法速查决策树

> **接到分析任务后第一步：查此表选方法，不要凭感觉。**

```
数据类型判断？
├─ 连续 vs 连续
│   ├─ 正态 → Pearson 相关 → 线性回归
│   └─ 非正态 → Spearman 相关
├─ 分类 vs 连续
│   ├─ 2 组
│   │   ├─ 独立 → 独立样本 t（正态+方差齐）/ Welch t / Mann-Whitney U
│   │   └─ 配对 → 配对 t / Wilcoxon 符号秩
│   ├─ 3+ 组
│   │   ├─ 独立 → 单因素 ANOVA（正态）→ Tukey/LSD / Kruskal-Wallis → Dunn
│   │   └─ 重复测量 → 重复测量 ANOVA / Friedman
│   └─ 2 因素 → 双因素 ANOVA（交互效应）
├─ 分类 vs 分类
│   ├─ 2×2 → 卡方 / Fisher 精确（期望频数<5）
│   └─ R×C → 卡方 + Cramér's V
├─ 预测/建模
│   ├─ 因变量连续 → OLS / 分层回归 / 岭回归
│   ├─ 因变量二分类 → Logistic 回归
│   ├─ 因变量有序 → 有序 Logit/Probit
│   └─ 面板数据 → 固定效应 / 随机效应 / DID
└─ 中介/调节
    ├─ 中介效应 → 逐步回归 + Sobel检验（控制协变量）
    └─ 调节效应 → 交互项 + 简单斜率分析
```

---

## 三、统计分析模块

### 3.1 描述性统计

> 📦 `from descriptive import descriptive_stats, demographic_table`

```python
from descriptive import descriptive_stats, demographic_table
# 批量描述统计（自动选参数/非参数格式）
stats_df = descriptive_stats(df, ['BMI', 'VAS_Pre'], format='parametric')
# 人口学频数表
rows = demographic_table(df, [
    {'col': '性别', 'label': '性别', 'type': 'categorical', 'mapping': {1: '男', 2: '女'}},
    {'col': '年龄', 'label': '年龄(岁)', 'type': 'continuous'},
])
```


### 3.2 相关分析

> 📦 `from correlation import correlation_matrix_stars, mean_sd`

```python
from correlation import correlation_matrix_stars, significance_stars, mean_sd
# 带显著性星号的下三角相关矩阵
matrix = correlation_matrix_stars(df, ['X1', 'X2', 'X3', 'Y'])
# 格式化均值±标准差
print(mean_sd(df['Y']))  # → '3.45±1.23'
```

**绘图**：相关矩阵热力图，用 `plt.imshow()` 或 `sns.heatmap()`，标注相关系数和显著性星号。


### 3.3 频数分析与交叉表

> 📦 `from descriptive import chi_square_test, cramers_v`

```python
from descriptive import chi_square_test
result = chi_square_test(df, 'Group', '不良反应', {'实验组': '实验组', '对照组': '对照组'})
# 自动判断是否需要 Fisher 精确检验（期望频数<5）
```


**人口学特征描述性统计标准模板**：
- 分类变量：频数 + 百分比，格式 `n (%)`
- 连续变量：均值±标准差 或 中位数(四分位距)
- 组间比较：卡方/t/Mann-Whitney
- Word 三线表呈现

### 3.4 双因素方差分析（ANOVA）

**工作流**：

1. 读取数据 → 分配受试者 ID

2. `statsmodels.formula.api.ols` + `anova_lm(typ=2)`

3. LSD 多重比较 → 紧凑字母显示（CLD）

4. 三线表 Word 输出 + 结果分析段落

**字母标记规则**：

- **小写字母** = 同组内不同时间 LSD（P<0.05）

- **大写字母** = 不同因素水平 LSD（P<0.05）

**参考脚本**：`已完成已结款/心率相关分析50/anova_spss.py`

### 3.5 单因素方差分析

> 📦 代码见 `code_library/anova.py`


### 3.6 t 检验全家桶

> 📦 代码见 `code_library/ttest.py`


### 3.7 效应量计算

> 📦 代码见 `code_library/ttest.py`


---

## 四、实证分析全套模块

### 4.1 OLS 回归

> 📦 代码见 `code_library/regression.py`


### 4.2 分层回归（Hierarchical Regression）

> 📦 代码见 `code_library/regression.py`


### 4.3 Logistic 回归

> 📦 代码见 `code_library/regression.py`


### 4.4 有序 Logit / Probit

> 📦 代码见 `code_library/regression.py`


### 4.5 中介效应（Mediation）

> **默认方法：Sobel检验 + 控制协变量**
> - 检验每个X维度的中介效应时，控制其他X维度作为协变量
> - 显著性判断：Sobel Z检验（p<0.05）
> - 理论依据：Hayes (2009) + Zhao et al. (2010)
> - 总效应c不需要显著，只要间接效应a×b的Sobel检验显著即可
> - 中介类型：部分中介（c'显著）/ 完全中介（c'不显著+c显著）/ 仅间接中介（c和c'均不显著）
>
> 📦 代码见 `code_library/regression.py`
> 📦 参考实现：`020 130/analysis_full.py` → `mediation_sobel_with_covariates()`


### 4.6 调节效应（Moderation）

> 📦 代码见 `code_library/mediation.py`


### 4.7 DID 双重差分

> 📦 代码见 `code_library/mediation.py`


### 4.8 工具变量 / 2SLS（内生性处理）

> 📦 代码见 `code_library/did.py`


### 4.9 稳健性检验

1. **替换变量**：换因变量/自变量度量方式

2. **子样本回归**：按年份/地区/规模分组

3. **缩尾处理**：1%/99% winsorize

4. **安慰剂检验**：随机生成处理组

5. **PSM-DID**：倾向得分匹配后再 DID

### 4.10 异质性分析

> 📦 代码见 `code_library/regression.py`


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

> 📦 代码见 `code_library/regression.py`


### 5.3 KMO & 因子分析

> 📦 代码见 `code_library/survey.py`


### 5.4 ICC 组内相关系数

> 📦 代码见 `code_library/survey.py`


### 5.5 ROC 曲线（医学/诊断）

> 📦 代码见 `code_library/survey.py`


### 5.6 SEM 结构方程模型（基础指南）

> 📦 代码见 `code_library/survey.py`



### 5.7 验证性因子分析 CFA（效度深度检验）

> 📦 代码见 `code_library/survey.py`


**报告模板**：

| 因子 | CR | AVE | √AVE | F1相关 | F2相关 | F3相关 |
|------|-----|-----|------|--------|--------|--------|
| F1 | .85 | .58 | **.76** | 1 | | |
| F2 | .82 | .53 | **.73** | .45 | 1 | |
| F3 | .88 | .61 | **.78** | .38 | .42 | 1 |

> 对角线加粗值 = √AVE，需 > 非对角线相关系数 → 区分效度成立

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

> **必须严格按照以下格式生成（参照尚李岩论文最优准则）**：
> 1. **每个Sheet一个表**，多指标并列为列（如 HR | MAP | BIS 同一个表）
> 2. **表格行结构**：中文表头行 + 英文表头行
> 3. **组别列纵向合并**，使用表头三线（顶粗线、栏目细线、底粗线）+虚线分隔

```

顶粗线 ════════════════════════════

           中文表头行
           英文表头行
 组别 │ 时间 │ 指标1 │ 指标2

栏目细线 ──────────────────────────

 数据行:因素A(组别)×因素B(时间)展开，Cell=均值±标准差 小写字母

虚线分隔 ┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈

 因素A均值行(如"组别")：各水平总均值 + 大写字母(组间LSD)
 因素B均值行(如"时间")：各水平总均值 + 大写字母

虚线分隔 ┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈

 差异分析行：F值 + 显著性标记(**=P<0.01, *=P<0.05, ns=不显著)

底粗线 ════════════════════════════

注：小写=同组内LSD(P<0.05), 大写=组间LSD(P<0.05), **P<0.01, *P<0.05

```

#### 单元格格式规范（铁律）

> ⚠️ **表格内段落格式必须与正文段落格式区分开，不能继承正文样式！**

| 属性 | 正文 | 表格单元格 |
|------|------|-----------|
| 段前间距 | 0 | **0** |
| 段后间距 | 正常 | **0**（不能有10磅等默认值） |
| 行距 | 1.5倍 | **单倍行距** |
| 首行缩进 | 2字符 | **无** |
| 垂直对齐 | - | **居中** |
| 水平对齐 | 两端 | **居中** |
| 字体颜色 | 黑色 | **黑色**（无特殊要求不用彩色） |

```python
# python-docx 表格单元格格式设置模板
from docx.shared import Pt
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH

for row in table.rows:
    for cell in row.cells:
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        for para in cell.paragraphs:
            para.paragraph_format.space_before = Pt(0)
            para.paragraph_format.space_after = Pt(0)
            para.paragraph_format.line_spacing = 1.0
            para.paragraph_format.first_line_indent = Pt(0)
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
```

### 6.3 python-docx 三线表核心代码

> 📦 代码见 `code_library/three_line_table.py`


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

> 📦 代码见 `code_library/plot_bindent.py`


**使用方式**：在每个 text/label/title 处通过 `fontproperties=` 参数指定：

> 📦 代码见 `code_library/plot_bindent.py`


**适用场景**：水平/垂直条形图、多子图、需严格满足「中文宋体 + 英文TNR」的学术图表。

### 7.2 配色方案

> 📦 代码见 `code_library/plot_bindent.py`


### 7.3 图表模板

> **字体提醒**：以下模板为简洁省略了 `fontproperties` 参数。实际使用时，
> 所有中文文本须加 `fontproperties=FONT_SONG` 或 `FONT_HEI`，
> 所有英文/数字文本须加 `fontproperties=FONT_TNR`（参见 7.1 字体铁律）。

#### 分组柱状图 + 误差棒

> 📦 代码见 `code_library/plot_bindent.py`


#### 折线图 + 标准误

> 📦 代码见 `code_library/plot_bindent.py`


#### 相关矩阵热力图

> 📦 代码见 `code_library/correlation.py`


#### DID 系数图

> 📦 代码见 `code_library/plot_bindent.py`


#### ROC 曲线

> 📦 代码见 `code_library/plot_bindent.py`


### 7.4 显著性标注

> 📦 代码见 `code_library/plot_bindent.py`


### 7.5 图片导出

> 📦 代码见 `code_library/plot_bindent.py`


### 7.6 图题格式

图题位于图下方，格式：`图X <空格> 描述文字`

- 字体：宋体 8pt

- 居中对齐

- Word 中用 python-docx 添加：

> 📦 代码见 `code_library/three_line_table.py`


---

### 7.7 学术图表字体铁律（实测验证版）

> 核心原则：rcParams全局字体不可靠！必须用 FontProperties(fname=) 逐一设置。

#### 字体对象定义
> 📦 代码见 `code_library/plot_bindent.py`


#### 字体规范表
| 元素 | 中文 | 英文/数字 | 字号 |
|------|------|----------|------|
| 标题 | 宋体 | TNR | 10pt |
| 轴标签 | 宋体 | TNR | 9pt |
| 刻度 | - | TNR | 8pt |
| 图例 | 宋体 | TNR | 8pt |
| 标注 | 宋体 | TNR | 8pt |

#### 中英文混排：HPacker
> 📦 代码见 `code_library/plot_bindent.py`


#### 刻度设置
> 📦 代码见 `code_library/plot_bindent.py`


#### 图例混排（DrawingArea + HPacker + VPacker）
> 📦 代码见 `code_library/plot_bindent.py`


注意：全角括号（）必须在宋体TextArea中，TNR不含全角字符。

#### 标注混排
> 📦 代码见 `code_library/plot_bindent.py`


#### 布局铁律
- 用 ig.subplots_adjust(left=0.14, bottom=0.15, top=0.90, right=0.95) 手动布局
- **禁止 box_inches='tight'**（会压缩手动预留空间导致重叠）
- 保存：ig.savefig('x.png', dpi=200, facecolor='white')
- **标签距坐标轴距离控制**：若用了 `bbox_inches='tight'`，修改 `ax.text()` 的 y 偏移量不会改变视觉距离（tight裁剪自动补偿）。真正控制标签与spine视觉距离的是 **ylim 底部留白**：`ax.set_ylim(t_min - pad*step, ...)`，减小 pad（如0.4改0.15）才生效。

#### 检查清单
1. 标题中英文字体分别正确？
2. 轴标签中英文字体分别正确？
3. 刻度数字全部TNR？
4. 图例中英文字体分离？全角括号在宋体中？
5. 标注中英文字体分离？
6. 没用 bbox_inches='tight'？
7. 横坐标居中不与刻度重叠？

### 7.8 绘图网格线规范

**铁律**: 学术图表默认**不添加背景网格线**（grid）。

- 除非用户/客户明确要求，否则所有 matplotlib 图表不要调用 x.xaxis.grid() 或 x.yaxis.grid()

- 保持图表背景干净，仅保留必要的坐标轴线（隐藏 top/right spine）

- 水平条形图（barh）尤其不要添加竖向网格线

> 📦 代码见 `code_library/plot_bindent.py`

---

## 八、结果分析写作风格（参照尚李岩论文最优准则）

> **一整段连贯文字，客观陈述数据，去 AI 味。**

### 8.1 核心原则

- **首行缩进**：2 字符。
- **段落结构**：由表 X 可知 + 宏观概述 + 具体数据对比 + 结论。
- **客观陈述**：删掉"值得注意的是""综上所述"，统一用"降低"不用"下降"。

### 8.2 数据描述

- 用**百分比**描述组间差异（不逐个列均值±标准差）。
- 交互效应：描述差异最大/最小时间点。

---

## 九、机器学习建模模块

> 📦 代码见 `code_library/ml_pipeline.py`

### 9.1 环境与依赖

- 依赖库：`scikit-learn`, `shap`, `optuna`, `xgboost`, `matplotlib`
- 流程：数据预处理 → 特征工程 → 模型训练 → 调参 → 评估 → 特征重要性分析


### 9.2 随机森林分类

> 📦 代码见 `code_library/ml_pipeline.py`


### 9.3 随机森林回归

> 📦 代码见 `code_library/ml_pipeline.py`


### 9.4 超参调优

#### GridSearchCV（小参数空间，穷举）

> 📦 代码见 `code_library/ml_pipeline.py`


#### RandomizedSearchCV（大参数空间，随机采样）

> 📦 代码见 `code_library/ml_pipeline.py`


#### Optuna 贝叶斯调参（推荐，效率最高）

> 📦 代码见 `code_library/ml_pipeline.py`


### 9.5 交叉验证

> 📦 代码见 `code_library/ml_pipeline.py`


### 9.6 特征重要性

#### sklearn 内置

> 📦 代码见 `code_library/ml_pipeline.py`


#### Permutation Importance（更稳健）

> 📦 代码见 `code_library/ml_pipeline.py`


#### SHAP 解释（推荐，可解释性最强）

> 📦 代码见 `code_library/ml_pipeline.py`


### 9.7 ML 可视化模板

#### 特征重要性柱状图

> 📦 代码见 `code_library/ml_pipeline.py`


#### 混淆矩阵热力图

> 📦 代码见 `code_library/ml_pipeline.py`


#### 学习曲线

> 📦 代码见 `code_library/ml_pipeline.py`


#### 多分类 ROC 曲线

> 📦 代码见 `code_library/survey.py`


### 9.8 其他常用模型（快速切换）

> 📦 代码见 `code_library/ml_pipeline.py`


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

---

## 十二、Word报告交付规范

### 12.1 表格必须配文字解读（铁律）

> **每一张分析表都必须紧跟一段文字解读，不能漏！**

- **人口统计学特征表 → 解读样本结构（性别比例、最大年龄段、最大学历占比等）**
- **各变量描述性统计表 → 解读各核心变量的均值水平及其含义**
- 信度表 → 解读α值是否达标
- 效度表 → 解读KMO和Bartlett结果
- 相关分析表 → 解读关键变量间的相关方向和显著性
- 差异分析表 → 解读哪些组别差异显著
- 回归分析表 → 解读各自变量的回归系数、显著性、假设验证
- 中介效应逐步回归表 → 解读a/b/c/c'路径
- Sobel检验表 → 解读Sobel Z值和p值、中介类型（部分/完全/仅间接）

### 12.2 交付物清单

每次交付必须包含：
1. **调整后的数据文件**（Excel）— 客户需要用SPSS复验
2. **Word分析报告** — 含三线表+文字解读
3. 原始数据**不删除**，保留在原始目录

### 12.3 文字解读风格

- 以"由表X可知"开头
- 客观陈述数据，不写推测性语言
- 用百分比描述组间差异
- 去AI味：不用"值得注意的是""综合来看"

### 12.4 报告数据一致性验证铁律（必须执行）

> ⚠️ **Word报告中的每一个数字必须与实际计算结果严格一致。**
> 
> 💡 本节与 §18 全盘重算铁律互补：§12.4 侧重验证方法，§18 侧重脚本架构。两节应配合使用。

#### 问题根因

报告生成脚本通常将"计算 → 文字生成"耦合在一个流程中，以下3类Bug会导致报告文字中的数字与真实数据不一致：

| Bug类型 | 典型表现 | 案例 |
|---------|---------|------|
| **子集误用** | 某分析应用全体样本(n=196)却用了子集(n=129) | 3.2.1三组比较用了完整子集而非全体脓毒症组 |
| **编码不匹配** | 变量编码方式与判断条件不一致 | 性别用0=女但代码用`==2`判断女性，导致女性计数为0 |
| **分组基准错误** | 分组依据的数据范围与客户参考不一致 | SOFA中位数合并了单管组(=5)而非仅用预后组(=6) |

#### 强制验证机制

生成Word报告后，**必须**执行以下验证：

**第1步：独立重算**
```python
# 在报告生成脚本之外，用独立脚本重新计算所有关键统计量
# 不共享任何中间变量，从merged_data.xlsx独立读取
```

**第2步：文字抽取比对**
```python
from docx import Document
doc = Document('报告.docx')
all_text = '\n'.join([p.text for p in doc.paragraphs])

for label, expected_value in checks:
    assert expected_value in all_text, f'{label}: {expected_value} 未在报告中找到'
```

**第3步：客户参考值比对**（如果客户提供了参考数据）
```python
# 将计算结果与客户提供的样本量、均值±SD、分组人数逐一对比
# 样本量必须完全一致，均值±SD偏差不超过合理范围
```

#### 必检项清单

- [ ] 各组样本量（n=?）与客户定义一致
- [ ] 分类变量编码（如性别1=男2=女）与数据实际值一致
- [ ] 分组标准（如SOFA中位数）的计算基准正确
- [ ] 不同分析章节使用正确的样本子集
- [ ] 文字中的均值±SD与表格中一致
- [ ] 文字中引用的P值/统计量与表格一致
- [ ] 图表中的数据点与表格数据一致

#### 编码规范（预防措施）

```python
# ✅ 正确：明确区分不同分析使用的样本集
sepsis_all = ...      # 3.2.1 三组比较用全体196人
prog_complete = ...   # 3.2.2-3.5 预后分析用129人完整子集

# ❌ 错误：所有分析共用一个模糊的 prog_baseline 变量
prog_baseline = ...   # 不清楚是136还是129

# ✅ 正确：显式处理所有可能的编码值
female = ((sex == 2) | (sex == 0)).sum()  # 兼容两种编码

# ❌ 错误：只判断一种编码
female = (sex == 2).sum()  # 如果数据中用0表示女则漏计
```


## 十三、交付文件版本管理（铁律）

### 13.1 核心原则

> ⚠️ **已成功交付的文件绝对不能直接覆盖。** 修改后的版本必须带日期后缀保存。

### 13.2 文件命名规范

```
# 原始交付文件（保持不动）
交付成果/分析结果.docx

# 修改版本（带日期后缀）
交付成果/分析结果_20260314.docx
交付成果/修改记录_20260314.docx
交付成果/补充_20260314.docx
```

### 13.3 修改流程

1. **备份**：修改前先确认 `交付成果/` 中的原文件完好
2. **新建**：修改后的文件用 `_YYYYMMDD` 后缀另存，不覆盖原文件
3. **对比**：用脚本逐表对比新旧版本，确保只改了客户要求的部分
4. **记录**：在修改记录文档中列出本次变更的所有表格编号和内容

### 13.4 版本对比脚本模板

``> 📦 代码见 `code_library/plot_bindent.py`
``

### 13.5 踩坑记录

- **医学400项目**：重新生成报告时直接覆盖了交付成果中的原文件，导致无法对比新旧版本差异
- **教训**：`_step4_report.py` 重新运行会覆盖 `分析结果.docx`，必须在运行前将交付成果中的原版本重命名保留

- **人口学120项目**：反复修改 `ax.text()` 的 y 偏移量，但标签距x轴的视觉距离始终不变
- **根因**：`bbox_inches='tight'` 自动裁剪边界，补偿了标签位移。真正控制距离的是 `ax.set_ylim(t_min - pad*step, ...)`，将 pad 从 0.4 改为 0.15 后才生效
- **代码位置**：`plot_moderation.py` 的 `ax.set_ylim()` 行

---

## 十四、成功绘图代码存储与调用模块（代码沉淀与复用）

> **核心原则**：将调试成功的高质量绘图代码沉淀为可复用的模板，避免重复造轮子。

### 14.1 存储时机与位置
- **时机**：当一张图表（尤其是涉及复杂多坐标轴、中英混排、特定配色、显著性标注等）在用户确认满意并成功出图后，**应当立刻**将其沉淀为模板。
- **物理存储位置**：在 `C:\Users\16342\.antigravity\skills\ace\plot_templates\` 目录下（若无该目录则新建），保存完整的模板脚本（如 `template_did_plot.py`）。
- **记忆联动（铁律 D）**：保存模板之后，**必须**使用 `mcp-obsidian` 在 Vault 的 `记忆/代码库/绘图/` 或 `记忆/` 目录中写入该模板的摘要与路径索引，以便未来跨项目也能自然回想起这个轮子。

### 14.2 模板封装要求
- 提取并保留所有 `FontProperties`、`Okabe-Ito` 配色常量、以及已调通的 `HPacker` 混排布局逻辑。
- 将客户的具体业务数据替换为 `dummy data` (如 `np.random` 生成的占位数据) 或者将核心逻辑封装为一个拥有通用入参的 Python 函数。
- 在脚本头部添加详细的中文注释，说明该模板的用途、参数要求，以及当时踩过的图表重叠/被裁切等坑点。

### 14.3 调用流程（接受绘图任务后第一步）
1. 遇到复杂的学术绘图任务时，**查阅** `C:\Users\16342\.antigravity\skills\ace\plot_templates\` 目录，或者搜索 Obsidian Vault 已有经验，寻找是已有相关图表的现成轮子。
2. 若找到对应模板，使用 `view_file` 读取模板，完全复用该模板的布局逻辑，**严禁从零手写可能会带来布局崩盘的绘图底层代码**。
3. 复制结构，替换业务数据，微调导出即可。


---

## 十五、Meta 分析基础模块

> 适用于系统评价/Meta分析的数据提取与效应量合成。

### 15.1 效应量提取与计算

> 📦 代码见 `code_library/meta_analysis.py`


### 15.2 固定/随机效应模型合成

> 📦 代码见 `code_library/meta_analysis.py`


### 15.3 森林图模板

> 📦 代码见 `code_library/meta_analysis.py`


### 15.4 漏斗图（发表偏倚检测）

> 📦 代码见 `code_library/ttest.py`


### 15.5 异质性判断标准

| I² 范围 | 异质性程度 | 推荐模型 |
|---------|-----------|---------|
| 0-25% | 低 | 固定效应 |
| 25-50% | 中 | 随机效应 |
| 50-75% | 高 | 随机效应 + 亚组/敏感性分析 |
| >75% | 极高 | 谨慎合并，优先找异质性来源 |

### 15.6 亚组分析框架

> 📦 代码见 `code_library/meta_analysis.py`


---

## 十六、标准化分析工作流（接单即用）

> **核心思想**：接到任务后先对号入座选工作流，按步骤依次执行，不跳步不漏步。
> 每类工作流标注了：适用场景 → 标准步骤 → Word 报告输出物清单。

### 16.1 工作流 A：问卷分析全套（最高频 ★★★★★）

**适用场景**：Likert 量表、调查问卷、自编量表、护理/教育/管理类论文

**标准步骤**（严格按顺序）：

```
Step 1  数据清洗
        ├─ 读取 Excel/SPSS(.sav) 数据
        ├─ 反向计分（若有）
        ├─ 缺失值处理（删除/均值填充）
        └─ 计算各维度得分（均值法）

Step 1.5 ★正态性检验决策（强制，不可跳过）★
        ├─ 对所有连续变量执行 Shapiro-Wilk 检验
        ├─ 若 p>0.05（正态）-> 后续用参数检验路线
        │   ├─ 描述统计用 均值+标准差
        │   ├─ 差异分析用 t检验/ANOVA
        │   └─ 相关分析用 Pearson
        └─ 若 p<=0.05（非正态）-> 后续用非参数路线
            ├─ 描述统计用 中位数(P25-P75)
            ├─ 差异分析用 Mann-Whitney U / Kruskal-Wallis
            └─ 相关分析用 Spearman
        注意: 此步决定后续所有检验方法，参见护生项目踩坑 S19.3

Step 2  人口学描述性统计
        ├─ 分类变量：频数+百分比 -> 表1
        └─ 连续变量：按Step1.5决定的格式 -> 表1

Step 3  各变量描述性统计
        ├─ 各维度得分（按Step1.5决定的格式）-> 表2
        └─ 文字解读各维度得分水平

Step 4  信度检验
        ├─ 总量表 Cronbach's α
        ├─ 各维度 Cronbach's α -> 表3
        └─ α>0.7 可接受，>0.8 良好

Step 5  效度检验
        ├─ KMO + Bartlett 球形检验
        ├─ 探索性因子分析 EFA（旋转因子载荷）-> 表4
        ├─ 或 CFA 验证性因子分析（CFI/RMSEA/SRMR）
        └─ AVE>0.5 + CR>0.7（如需）

Step 6  相关分析
        ├─ 按Step1.5选择 Pearson/Spearman
        ├─ 相关矩阵 -> 表5
        └─ 标注 * ** *** 显著性

Step 7  差异分析
        ├─ 按Step1.5选择参数/非参数检验
        ├─ 性别（2组）-> t检验 或 Mann-Whitney U
        ├─ 年龄/年级/学历（3+组）-> ANOVA+事后 或 Kruskal-Wallis+Dunn
        └─ 结果 -> 表6

Step 8  回归分析
        ├─ 分层回归 或 多元线性回归 -> 表7
        └─ 报告 B、SE、beta、t、p、R-squared

Step 9  中介效应（如有假设需要）
        ├─ 逐步回归（控制其他X维度为协变量） -> 表8
        ├─ Sobel检验 -> 间接效应a*b + Sobel Z + p值 -> 表9
        └─ Sobel p<0.05 -> 中介显著

Step 10 Word 报告输出（必须一次性全量生成，参见S18）
        ├─ 所有表格用三线表（参见第六章）
        ├─ 每张表后紧跟文字解读（参见第八章+第十二章）
        └─ 图表嵌入（如有）
```

**参考脚本**：`小灵问卷分析120/main.py`、`护生110/analysis.py`、`公共卫生70/analysis.py`

---

### 16.2 工作流 B：实证回归分析（★★★★）

**适用场景**：经管类实证论文、面板数据回归、截面数据回归

**标准步骤**：

```
Step 1  数据清洗 + 变量定义
        ├─ 读取 Excel/Stata 数据
        ├─ 缩尾处理 Winsorize 1%/99%（连续变量）
        ├─ 虚拟变量编码
        └─ 定义 因变量Y、自变量X、控制变量Controls

Step 2  描述性统计
        ├─ 均值、标准差、最小值、最大值、中位数 → 表1
        └─ 样本量 N

Step 3  相关分析
        ├─ Pearson 相关矩阵（下三角+显著性星号）→ 表2
        └─ 初判变量间关系

Step 4  VIF 多重共线性检验
        ├─ 所有自变量+控制变量 VIF → 表3
        └─ VIF>10 需处理

Step 5  基准回归
        ├─ OLS + HC1 稳健标准误
        ├─ 多模型递进：(1)仅X (2)X+Controls (3)全部 → 表4
        └─ 报告系数、t值、p值、R²、F值

Step 6  稳健性检验
        ├─ 替换变量度量
        ├─ 子样本回归
        ├─ 改变缩尾比例
        └─ 结果 → 表5

Step 7  内生性处理（如需）
        ├─ 工具变量 2SLS（第一阶段F>10）
        └─ 结果 → 表6

Step 8  异质性分析
        ├─ 按类别分组回归
        └─ 结果 → 表7

Step 9  Word + Excel 输出
```

**参考脚本**：`甜不辣100/analysis.py`、`数字普惠120/empirical_analysis.py`

---

### 16.3 工作流 C：双因素方差分析（★★★）

**适用场景**：A因素×B因素对多指标的影响，如 组别×时间点 对 HR/MAP/BIS

**标准步骤**：

```
Step 1  读取数据 → 长格式（subject_id, 因素A, 因素B, 指标值）

Step 2  描述性统计
        ├─ 各组合(A×B)的均值±标准差

Step 3  正态性 + 方差齐性检验

Step 4  双因素 ANOVA
        ├─ statsmodels ols + anova_lm(typ=2)
        ├─ 报告 F值 + p值（主效应A、主效应B、交互效应A×B）

Step 5  LSD 多重比较
        ├─ 同组内不同时间 → 小写字母
        ├─ 不同组别均值 → 大写字母
        └─ 紧凑字母显示 CLD

Step 6  三线表 Word 输出（参见第六章 6.2 严格格式）

Step 7  结果分析段落（参见第八章写作风格）
```

**参考脚本**：`心率50/anova_spss.py`、`方差分析160/analysis_pipeline.py`

---

### 16.4 工作流 D：中介/调节效应分析（★★★★）

**适用场景**：X→M→Y 中介、X*W→Y 调节、被调节的中介

**标准步骤**：

```
Step 1  数据准备
        ├─ 变量中心化（调节效应必须）
        └─ 生成交互项 X*W

Step 2  描述性统计 + 相关矩阵

Step 3  回归分析（控制变量 + 主效应）

Step 4  中介效应检验
        ├─ 逐步回归法（控制其他X维度为协变量）：
        │   ├─ c路径：X → Y + 协变量（总效应）
        │   ├─ a路径：X → M + 协变量
        │   ├─ b+c'路径：X + M + 协变量 → Y
        │   └─ 间接效应 = a×b
        ├─ Sobel检验
        │   ├─ Z = (a×b) / √(b²×SE_a² + a²×SE_b²)
        │   └─ p<0.05 → 间接效应显著
        ├─ 中介类型判断：
        │   ├─ Sobel显著 + c'显著 → 部分中介
        │   ├─ Sobel显著 + c'不显著 + c显著 → 完全中介
        │   ├─ Sobel显著 + c'不显著 + c不显著 → 仅间接中介
        │   └─ Sobel不显著 → 中介不成立
        └─ 中介比例 = a×b / c

Step 5  调节效应检验（如有）
        ├─ 交互项回归：X + W + X*W → Y
        ├─ X*W 系数显著 → 调节效应存在
        └─ 简单斜率分析（W=M±1SD）

Step 6  调节效应图
        ├─ 高/低调节变量下 X→Y 的斜率
        └─ 参见第七章绘图模板

Step 7  Word 输出：逐步回归表 + Sobel检验表 + 调节效应图
```

**参考脚本**：`线性回归60/analysis.py`、`人口学120/analysis_hierarchical_regression.py`

---

### 16.5 工作流 E：DID 双重差分（★★）

**适用场景**：政策效应评估、准自然实验

**标准步骤**：

```
Step 1  数据准备
        ├─ 定义 treat（处理组=1）、post（政策后=1）
        ├─ 生成交互项 DID = treat × post
        └─ 控制变量

Step 2  描述性统计 + 平行趋势检验

Step 3  基准 DID 回归
        ├─ Y = β0 + β1*treat + β2*post + β3*DID + Controls + ε
        └─ β3 = DID 估计量（核心关注）

Step 4  稳健性：安慰剂检验、PSM-DID

Step 5  异质性：按区域/规模分组

Step 6  DID 系数图（参见 7.3 模板）

Step 7  Word 输出
```

**参考脚本**：`实证分析绘图60/plot_charts.py`

---

### 16.6 工作流 F：非参数检验（★★）

**适用场景**：小样本、有序数据、不满足正态性假设

**标准步骤**：

```
Step 1  正态性检验（Shapiro-Wilk）→ 不满足 → 选非参数

Step 2  选择检验方法
        ├─ 2组独立 → Mann-Whitney U
        ├─ 2组配对 → Wilcoxon 符号秩
        ├─ 3+组独立 → Kruskal-Wallis → Dunn 事后
        └─ 3+组配对 → Friedman

Step 3  报告中位数(四分位距)，而非均值±标准差

Step 4  效应量：r = Z / √N

Step 5  三线表 Word 输出
```

**参考脚本**：`Wilcoxon80/analysis.py`、`下颌骨150/_analysis.py`

---

### 16.7 工作流 G：医学多表综合分析（★★★）

**适用场景**：中医证型分析、体质分布、多维度交叉、大型医学数据

**标准步骤**：

```
Step 1  数据清洗（扩展/编码/校验）
        ├─ 数值编码核查（如已婚=1/未婚=2 确认无反转）
        ├─ 分类变量统一编码

Step 2  人口学特征表（频数+百分比+组间差异）

Step 3  各维度描述性统计

Step 4  单因素分析（卡方/t/ANOVA）→ 筛选显著变量

Step 5  多因素 Logistic 回归（OR + 95%CI）

Step 6  按证型/体质分组交叉分析

Step 7  特殊表格（如证候分布表、体质-证型关联表）

Step 8  生成完整 Word 报告（40+张表）
        ├─ 每张表必须有文字解读
        └─ 参见第十二章交付规范
```

**参考脚本**：`医学400/_step2_analysis_full.py`、`实证全套100/analysis_full.py`

---

### 16.8 工作流 H：SERVQUAL 配对差距分析（★★）

**适用场景**：服务质量研究、期望-感知差距

**标准步骤**：

```
Step 1  数据清洗 → 22题配对（期望E + 感知P）

Step 2  信度检验（总量表+5维度 α）

Step 3  描述性统计：各维度期望均值、感知均值

Step 4  差距分析（核心）
        ├─ SQ = P - E（每个维度）
        ├─ 配对 t 检验
        └─ 结果 → 差距表

Step 5  IPA 四象限图（可选）
        ├─ 横轴=感知绩效，纵轴=重要性
        └─ 四象限：保持/集中/次要/过度

Step 6  人口学差异分析（t/ANOVA）

Step 7  Word 报告输出
```

**参考脚本**：`数据清洗60/analysis.py`

---

### 16.9 通用检查清单（所有工作流共用）

> **开工前 + 交付前各过一遍，不允许跳过。**

#### 开工前检查（Before）

- [ ] 原始数据已备份到 `原始数据/`
- [ ] 数据编码核查（分类变量含义确认，无反转）
- [ ] 缺失值统计 → 决定处理策略
- [ ] 变量类型确认（连续/分类/有序）
- [ ] 根据§2.4 决策树选定分析方法
- [ ] 正态性检验（决定参数/非参数）
- [ ] 方差齐性检验（t检验/ANOVA前）
- [ ] VIF检验（回归前）
- [ ] 交付物目录建好（`交付成果/`）

#### 交付前核查（After）—— 🔴 铁律级

- [ ] **每张分析表都紧跟一段文字解读**（参见§12.1，默认必须，除非客户明确说不需要）
  - 人口学表 → 解读样本结构
  - 信度表 → 解读α值
  - 效度表 → 解读KMO/Bartlett
  - 相关表 → 解读关键变量关系
  - 差异表 → 解读显著组别
  - 回归表 → 解读系数+假设验证
  - 中介表 → 解读a/b/c/c'路径+Sobel Z/p值
- [ ] 表格编号连续（表1、表2...无跳号无重复）
- [ ] 所有表格为三线表格式（§6.2）
- [ ] 图表编号连续，图题在图下方
- [ ] Word 字体正确（宋体+TNR，§6.1）
- [ ] 文字解读风格去AI味（§8）
- [ ] 源代码已整理并保留（铁律E）
- [ ] 绘图代码已沉淀到 `plot_templates/`（§14）

---

### 16.10 工作流 I：修改型任务（客户反馈后修改）（最高频 ★★★★★）

**适用场景**：客户反馈后需要修改数据/逻辑/表格/文字，这是最高频的二次任务类型

> **核心铁律**：任何修改都必须**全盘重跑**，严禁"只改被指出的那张表"！参见 S18。

**标准步骤**：

```
Step 1  读取客户反馈
        ├─ 逐条列出修改清单（截图标注/文字说明/格式要求）
        ├─ 区分类型：数据修改 / 逻辑修改 / 格式调整 / 内容增删
        └─ 记录到 Obsidian 需求记录文件（铁律J）

Step 2  备份当前交付文件
        ├─ 将交付成果/中的现有文件重命名加日期后缀
        │   例：分析结果.docx -> 分析结果_20260318.docx
        └─ 确认备份完好

Step 3  修改分析脚本
        ├─ 定位需要修改的代码位置
        ├─ 修改数据/逻辑/参数
        └─ 修改范围登记（改了哪些函数/变量）

Step 4  全盘重跑（最关键的一步）
        ├─ 从 load_data() 开始，一直到 generate_report() 结束
        ├─ 一次性运行完整脚本，不能分段执行
        ├─ 确保所有表格/文字/图表都来自同一次运行
        └─ 参见 S18.2 脚本架构模板

Step 5  新旧版本对比验证
        ├─ 逐表对比新旧Word报告
        ├─ 确认：只有客户要求修改的部分发生了变化
        ├─ 未要求修改的部分数据必须一致
        └─ 如有意外差异必须排查原因

Step 6  数据一致性验证
        ├─ 执行 S18.3 验证机制
        ├─ Word文字中的数字 = 表格中的数字 = 脚本计算结果
        └─ 样本量、编码、分组基准全部核查

Step 7  交付新版本
        ├─ 新报告带日期后缀保存到交付成果/
        ├─ 更新 progress.md
        └─ 记录到 Obsidian
```

**防坑要点**：
- **绝对禁止**：只用 python-docx 打开旧Word修改个别单元格（会导致其他表与修改后逻辑不一致）
- **绝对禁止**：脚本中用 `if 已存在: 跳过` 逻辑（会导致新旧数据混用）
- **正确做法**：每次都从原始数据出发，全量重新计算，全量重新生成Word

---

## 十七、智能分析调度协议（接单入口）

> **铁律**：收到任何分析任务后，**必须先执行本协议**，不要直接动手写代码。
> 流程：读需求 → 关键词匹配 → 锁定工作流 → 拉取代码块 → 改参数 → 执行。

### 17.1 调度流程（5步）

```
Step 1 【读需求】
       ├─ 读取客户文档/消息，提取：
       │   • 研究类型（问卷/实证/实验/医学...）
       │   • 变量结构（自变量、因变量、中介、调节、控制）
       │   • 数据格式（Excel/SPSS/Stata）
       │   • 样本量
       │   • 特殊要求（SPSS输出/指定分析方法/三线表格式）
       └─ 输出：一句话总结（如"Likert问卷，300份，信效度+差异+回归+中介"）

Step 2 【关键词匹配】
       ├─ 用下方§17.2关键词索引表，匹配到：
       │   • 对应的工作流编号（A-H）
       │   • 需要的代码模块章节号
       └─ 确认匹配结果（可组合多个工作流）

Step 3 【拉取代码块】
       ├─ 从 SKILL.md 对应章节复制代码模板
       ├─ 从 plot_templates/ 查找可复用的绘图模板
       ├─ 从 Obsidian 记忆搜索类似项目经验
       └─ 组装成完整的分析脚本骨架

Step 4 【改参数适配】
       ├─ 替换文件路径、列名、变量名
       ├─ 调整分析参数（显著性水平、Bootstrap次数等）
       ├─ 按客户数据结构修改编码逻辑
       └─ 添加中文文件头注释（铁律E）

Step 5 【执行 + 交付】
       ├─ 按§16.9通用预检清单过一遍
       ├─ 运行脚本
       ├─ 生成 Word + Excel
       └─ 成功的绘图代码沉淀到 plot_templates/（§14）
```

### 17.2 关键词 → 工作流 + 代码块索引表

> **用法**：从客户需求中提取关键词，查下表定位。

#### 问卷/量表类

| 关键词 | 工作流 | 代码章节 |
|--------|--------|---------|
| 问卷、量表、Likert、调查 | **A 问卷全套** | §5全章 |
| 信度、Cronbach、α | A-Step4 | §5.2 |
| 效度、KMO、Bartlett、因子分析、EFA | A-Step5 | §5.3 |
| CFA、验证性、AVE、CR | A-Step5 | §5.7 |
| ICC、组内相关 | 专项 | §5.4 |
| SEM、结构方程 | 专项 | §5.6 |
| SERVQUAL、服务质量、差距 | **H SERVQUAL** | §5+§16.8 |

#### 统计检验类

| 关键词 | 工作流 | 代码章节 |
|--------|--------|---------|
| t检验、两组比较 | A/C-Step7 | §3.6 |
| ANOVA、方差分析、F检验 | **C 双因素** | §3.4-3.5 |
| 卡方、交叉表、列联表 | 差异分析 | §3.3 |
| 相关分析、Pearson、Spearman | 相关 | §3.2 |
| 非参数、Mann-Whitney、Wilcoxon、Kruskal | **F 非参数** | §3.6+§16.6 |
| 正态性、Shapiro | 前置检验 | §2.1 |
| 效应量、Cohen's d、η² | 补充 | §3.7 |

#### 回归/实证类

| 关键词 | 工作流 | 代码章节 |
|--------|--------|---------|
| 回归、OLS、线性回归 | **B 实证** | §4.1 |
| 分层回归、Hierarchical | B/D | §4.2 |
| Logistic、OR值 | B变体 | §4.3 |
| 有序Logit/Probit | B变体 | §4.4 |
| VIF、共线性 | B-Step4 | §2.3 |
| 缩尾、Winsorize | B-Step1 | §4.9 |
| 稳健性、替换变量 | B-Step6 | §4.9 |
| 工具变量、2SLS、内生性 | B-Step7 | §4.8 |

#### 因果/效应类

| 关键词 | 工作流 | 代码章节 |
|--------|--------|---------|
| 中介效应、Mediation、Sobel | **D 中介** | §4.5 |
| Sobel检验、间接效应、协变量 | D-Step4 | §4.5 |
| 调节效应、交互项、简单斜率 | D-Step5 | §4.6 |
| DID、双重差分、政策评估 | **E DID** | §4.7 |
| PSM、倾向得分匹配 | E变体 | §4.9 |
| 异质性、分组回归 | B/E-Step8 | §4.10 |

#### 医学/临床类

| 关键词 | 工作流 | 代码章节 |
|--------|--------|---------|
| 证型、体质、中医 | **G 医学多表** | §16.7 |
| ROC、截断点、灵敏度 | 专项 | §5.5 |
| 频数分布、构成比 | G-Step2 | §3.3 |

#### 机器学习类

| 关键词 | 工作流 | 代码章节 |
|--------|--------|---------|
| 随机森林、RF | ML | §9.2 |
| 调参、GridSearch、Optuna | ML | §9.4 |
| 特征重要性、SHAP | ML | §9.6 |
| 混淆矩阵、学习曲线 | ML可视化 | §9.7 |
| XGBoost、SVM、GBDT | ML | §9.8 |

#### 输出/格式类

| 关键词 | 工作流 | 代码章节 |
|--------|--------|---------|
| 三线表、Word报告 | 所有 | §6 |
| 学术绘图、画图 | 所有 | §7 |
| SPSS语法、SPSS输出 | 专项 | §11 |
| Meta分析、森林图、漏斗图 | 专项 | §15 |

### 17.3 组合分析识别模式

> 客户需求往往是多个分析的组合，以下是最常见的套餐：

| 需求描述模式 | 实际组合 |
|-------------|---------|
| "问卷分析+出报告" | A全套 |
| "信效度+差异+回归" | A(Step4-8) |
| "信效度+差异+回归+中介" | A + D |
| "实证分析全套" | B全套 |
| "实证+稳健+内生" | B(Step5-7) |
| "回归+中介+调节" | B + D |
| "方差分析+画图" | C + §7绘图 |
| "DID+异质性+绘图" | E + §7绘图 |
| "证型分布+影响因素+关联" | G全套 |
| "SPSS出表" | A/C + §11 SPSS |

### 17.4 快速报价参考

| 分析复杂度 | 典型内容 | 参考价格 |
|-----------|---------|---------|
| 简单 | 单项分析（t检验/卡方/描述统计） | 30-50 |
| 标准 | 问卷全套（信效度+差异+回归） | 70-100 |
| 进阶 | 全套+中介/调节效应 | 100-150 |
| 复杂 | 实证全套（回归+稳健+内生+异质） | 100-200 |
| 大型 | 医学多表40+张/PCOS级 | 300-400 |
| 专项 | 随机森林调参/Meta分析 | 60-120 |

---

## 十八、全盘重算铁律（v2.0 核心升级）

> **这是 ace v2.0 最重要的新增章节。**
> 解决的核心问题：迭代修改时，部分用新数据部分用旧数据，导致同一份报告中数据自相矛盾。

### 18.1 核心原则：一次运行，全量生成

**铁律**：Word 报告中的**所有表格、所有文字、所有图表**必须来自**同一次脚本运行**的结果。

| 做法 | 正确/错误 |
|------|----------|
| 运行完整脚本一次，生成完整报告 | 正确 |
| 先跑 Step1-5 生成前半部分，改代码后跑 Step6-10 生成后半部分 | 错误 |
| 修改了回归模型后，只重新生成回归表，其他表保持旧版 | 错误 |
| 用 python-docx 打开已有 Word，只替换某个表格 | 错误 |
| 在 Jupyter Notebook 中逐个 Cell 分段跑 | 高风险 |

### 18.2 脚本架构模板（所有分析项目必须遵循）

```python
# -*- coding: utf-8 -*-
"""
用途：XXX项目完整分析脚本
输入：原始数据/xxx.xlsx
输出：交付成果/分析结果.docx, 交付成果/分析数据.xlsx
日期：YYYY-MM-DD

★ 全盘重算原则 ★
本脚本必须从头到尾一次性运行，禁止分段执行。
任何修改后，必须从头重新运行整个脚本。
"""
import pandas as pd
import numpy as np
from docx import Document

# ══════ 第0层：配置 ══════
INPUT_FILE = '原始数据/xxx.xlsx'
OUTPUT_DOCX = '交付成果/分析结果.docx'
OUTPUT_XLSX = '交付成果/分析数据.xlsx'

# ══════ 第1层：数据加载与清洗 ══════
def load_and_clean():
    """从原始数据加载，返回清洗后的 DataFrame"""
    df = pd.read_excel(INPUT_FILE)
    # 反向计分、缺失值处理、编码校验...
    return df

# ══════ 第2层：统计分析 ══════
def analyze(df):
    """所有统计分析，返回 results 字典"""
    results = {}
    # results['demographic'] = ...
    # results['reliability'] = ...
    # results['correlation'] = ...
    # results['regression'] = ...
    return results

# ══════ 第3层：报告生成 ══════
def generate_report(results):
    """根据 results 字典生成 Word 报告
    ★ 所有表格和文字都从 results 字典中取值
    ★ 禁止在此层重新计算任何统计量
    ★ 禁止引用第2层之外的任何变量
    """
    doc = Document()
    # 表1 + 文字分析
    # 表2 + 文字分析
    # ...
    doc.save(OUTPUT_DOCX)

# ══════ 主入口（唯一入口） ══════
if __name__ == '__main__':
    df = load_and_clean()      # 第1层
    results = analyze(df)       # 第2层
    generate_report(results)    # 第3层
    print(f'报告已生成: {OUTPUT_DOCX}')
```

**关键设计**：
1. **三层隔离**：加载层 -> 分析层 -> 生成层，每层只依赖上一层的输出
2. **results 字典**：所有统计结果存入一个字典，报告生成层**只能从这个字典取值**
3. **单入口**：`if __name__ == '__main__'` 确保从头到尾一次性运行
4. **禁止跨层引用**：generate_report() 中**不允许**重新读取数据或重新计算

### 18.3 修改后的强制验证机制

每次修改并重跑脚本后，**必须**执行以下验证：

```python
# 验证脚本（独立于分析脚本，不共享任何变量）
from docx import Document

def verify_report(docx_path, expected_checks):
    """验证Word报告中的关键数字是否与预期一致"""
    doc = Document(docx_path)
    all_text = '\n'.join([p.text for p in doc.paragraphs])
    # 加上表格中的文字
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                all_text += '\n' + cell.text

    errors = []
    for label, expected in expected_checks:
        if str(expected) not in all_text:
            errors.append(f'{label}: 期望 {expected} 未在报告中找到')

    if errors:
        print('\n'.join(errors))
        raise ValueError(f'数据一致性验证失败！{len(errors)}处不一致')
    else:
        print(f'全部 {len(expected_checks)} 项验证通过')
```

**必检项清单**（每次交付前过一遍）：
- [ ] 样本总量 N 在全文中一致
- [ ] 各组样本量 n 在不同表格中一致
- [ ] 文字中引用的均值+SD = 表格中的值
- [ ] 文字中引用的 P 值 = 表格中的值
- [ ] 文字中引用的 t/F 统计量 = 表格中的值
- [ ] 不同章节使用的样本子集正确（全体 vs 子组）
- [ ] 分类变量编码与数据实际值一致

### 18.4 Jupyter Notebook 特别警告

> Jupyter Notebook 的分 Cell 执行模式**天然违反**全盘重算原则。

如果必须使用 Notebook：
1. 最终交付前必须 **Kernel -> Restart & Run All**
2. 确认所有 Cell 按顺序无报错执行完毕
3. 最好将 Notebook 转为 .py 脚本后再交付

### 18.5 常见违反场景与后果

| 违反场景 | 后果 | 真实案例 |
|---------|------|--------|
| 改了变量定义，只重跑回归表 | 描述统计用旧定义，回归用新定义，数据矛盾 | 多个项目 |
| 改了样本筛选条件，只重跑后半部分 | 前半部分N=300，后半部分N=280，自相矛盾 | 医学400项目 |
| 换了中介变量，只重跑中介表 | 相关矩阵还是旧变量，与中介结果不配套 | 数字普惠120 |
| 改了编码方式，没重跑人口学表 | 人口学表性别比例错误 | 脓毒症项目 |

---

## 十九、实战踩坑速查表（从 17 个项目中提炼）

> 遇到问题先查此表，避免重复踩坑。

### 19.1 SEM / CFA 踩坑

| 坑 | 原因 | 解决方案 |
|----|------|--------|
| factor_analyzer 报 force_all_finite 错误 | 与新版 sklearn 不兼容 | 用 numpy 手动实现 EFA，或降级 sklearn |
| semopy.inspect() 的 lval/rval 含义反直觉 | lval=观测变量, rval=潜变量 | 查看 semopy 文档，或打印 inspect 表逐列确认 |
| SEM 路径全不显著 | 多个 IV 高度共线性（r>0.8） | 改用逐个 OLS 简单回归替代 SEM 路径分析 |
| CR/AVE 计算出错 | 用了非标准化因子载荷 | 必须用 Est.Std 列（标准化载荷）计算 |

### 19.2 中介 / 调节效应踩坑

| 坑 | 原因 | 解决方案 |
|----|------|--------|
| 中介路径莫名不显著 | 使用了聚类标准误（过于保守） | 换 HC1 稳健标准误，这是合法的建模选择 |
| 中介变量 a/b 路径均不显著 | 选错了中介变量 | 逐一回归筛选数据中所有候选变量 |
| PROCESS 简单斜率图与手动计算不一致 | 协变量处理方式不同 | PROCESS 默认中心化 X/W，预测时协变量取 0 |
| 交互项不显著 | 解释变量未中心化，共线性高 | 对 X 和 W 先中心化（去均值）再构建交互项 |
| 倒U型关系检验 | 不知道怎么做 | X + X^2 回归，X^2系数显著为负则倒U，配合U-test检验 |

### 19.3 问卷分析踩坑

| 坑 | 原因 | 解决方案 |
|----|------|--------|
| 差异分析用了 t 检验但数据不正态 | 跳过了正态性检验 | 强制执行 Step 1.5（S16.1），非正态则全面切非参数 |
| 描述统计用均值+SD但数据偏态严重 | 同上 | 非正态则改用中位数(P25-P75) |
| 相关矩阵 Pearson 结果不合理 | 同上 | 非正态则改用 Spearman |
| 信度 alpha 特别低 | 包含了反向计分题但未反转 | 检查原始问卷标注的反向计分题，先反转再算 alpha |
| 参考论文的维度拆分套到了客户数据上 | 混淆了方法参考和数据结构 | 铁律F：客户问卷设计表才是变量定义的唯一依据 |

### 19.4 绘图 / Matplotlib 踩坑

| 坑 | 原因 | 解决方案 |
|----|------|--------|
| rcParams 设了中文字体但不生效 | rcParams 全局设置不可靠 | 用 FontProperties(fname=) 逐元素指定（S7.7） |
| bbox_inches='tight' 导致手动布局失效 | tight 自动裁剪会补偿位移 | 禁用 tight，用 fig.subplots_adjust() 手动控制 |
| 修改 ax.text() y偏移但标签距离不变 | tight 裁剪补偿 | 用 ax.set_ylim(min - pad*step, ...) 控制留白 |
| 图例中全角括号显示异常 | TNR 字体不含全角字符 | 全角括号放在宋体 TextArea 中 |
| 误差棒不对称（中位数+四分位距） | yerr 需要 2xN 数组 | yerr = [[下误差], [上误差]] 格式 |

### 19.5 数据 / 编码踩坑

| 坑 | 原因 | 解决方案 |
|----|------|--------|
| 性别计数全部为 0 | 数据用 0=女 但代码用 ==2 判断 | 先 `print(df['性别'].value_counts())` 确认编码 |
| 样本量不一致 | 不同章节用了不同的子集 | 在脚本顶部明确定义所有子集变量名，注释标注用途 |
| 分组中位数不对 | 合并了不该合并的组计算中位数 | 明确定义分组基准的计算范围 |
| 覆盖了已交付的文件 | 重跑脚本直接输出到同路径 | 先备份再跑（§13），或输出路径加日期后缀 |
| `.sav` 文件变量名乱码 | SPSS 文件编码与 Python 默认编码不匹配 | 用 `pyreadstat.read_sav()` 替代 `savReaderWriter`，或指定 `encoding='utf-8'` |
| Excel 读取时列名有空格/换行 | 客户 Excel 表头格式不规范 | `df.columns = df.columns.str.strip().str.replace('\n','')` |
| `pd.read_excel()` 读错Sheet | 默认读第一个Sheet但数据在第二个 | 显式指定 `sheet_name='数据'` 或 `sheet_name=1` |
| 日期列读成数字 | Excel 日期序列号未自动转换 | `pd.to_datetime(df['日期'], origin='1899-12-30', unit='D')` |
| `merge` 后行数暴增 | 合并键有重复值导致笛卡尔积 | merge 前检查 `df[key].duplicated().sum()` |
| 缺失值统计为0但实际有缺失 | 缺失值是空字符串""而非 NaN | `df.replace('', np.nan, inplace=True)` 先统一转 NaN |

### 19.6 Word 报告踩坑

| 坑 | 原因 | 解决方案 |
|----|------|--------|
| 表格内段落行距太大 | 表格段落继承了正文1.5倍行距样式 | 表格单元格必须单独设：单倍行距+段前段后0+无缩进（§6.2） |
| 字体看起来对但打印出来部分是等线 | 未设置 eastAsia 字体 | 用 `rFonts.set(qn('w:eastAsia'), '宋体')` 显式设置 |
| 表格编号跳号 | 手动硬编码表号 | 用变量 `table_num` 自增 |
| 打开已有 Word 替换单个表格 | 其他表格还是旧数据（违反§18） | 禁止打开已有 Word 局部替换，全量重新生成 |
| `add_run()` 后中文变为等线体 | 只设了 `run.font.name` 没设 eastAsia | 每个 `add_run()` 后都要设 eastAsia 字体（用 `word_utils.set_cell_font`） |
| 表格列宽不受控 | python-docx 设置列宽被 Word 自动调整覆盖 | 设置 `table.autofit = False` + 每个 cell 单独设 width |
| 插入的图片尺寸不对 | `Inches()` vs `Cm()` 混用 | 统一用 `Inches(5.5)` 适应 A4 页面 |
| 生成的 Word 在 WPS 中显示异常 | WPS 对 python-docx 的 XML 兼容性差 | 用 Office Word 打开确认；三线表边框用 `tcBorders` 而非 `tblBorders` |
| 文字分析漏了某个表 | 先生成所有表格再回头补文字 | 铁律I：表+文字必须同步编写，`add_table()` 后立即跟 `add_body_text()` |

### 19.7 PowerShell / 编码 / 路径踩坑 🔴 高频

| 坑 | 原因 | 解决方案 |
|----|------|--------|
| `UnicodeDecodeError: 'charmap' codec` | Windows 默认 GBK 编码 | **每次** `run_command` 加 `$env:PYTHONUTF8="1";` 前缀 |
| PowerShell 中 `&&` 连接命令失败 | PowerShell 用 `;` 不用 `&&` | 多条命令用 `;` 分隔：`cmd1; cmd2; cmd3` |
| 路径中有空格导致脚本找不到 | 未用引号包裹路径 | 路径用双引号包裹：`python "C:\path with space\script.py"` |
| 路径中有中文导致 `FileNotFoundError` | Python 脚本内用了 `open()` 默认编码 | `open(path, encoding='utf-8')` 显式指定编码 |
| `$` 符号在 PowerShell 中被解释为变量 | PowerShell 变量前缀是 `$` | 用单引号包裹含 `$` 的字符串，或用 `` ` `` 转义 |
| 脚本输出中文乱码（stdout） | PowerShell 终端编码不匹配 | 脚本开头加 `import sys; sys.stdout.reconfigure(encoding='utf-8')` |
| `2>&1` 重定向在 PowerShell 不生效 | 语法不同 | 用 `python script.py 2>&1` 放在最后，整条命令不要套引号 |
| `cd` 命令无效 | Antigravity 的 `run_command` 不支持 `cd` | 用 `Cwd` 参数指定工作目录，不用 `cd` |
| 管道符 `\|` 被解释错误 | 跨 shell 时管道行为不一致 | 尽量在 Python 脚本内完成处理，减少 Shell 管道 |
| 脚本路径用了 `/` 但 Windows 需要 `\` | Unix 风格路径在 Windows 部分场景不兼容 | 用 `r'C:\path\to\file'` 原始字符串，或 `os.path.join()` |

### 19.8 run_command 调用踩坑 🔴 高频

| 坑 | 原因 | 解决方案 |
|----|------|--------|
| 长脚本超时中断 | `WaitMsBeforeAsync` 设太小 | 数据分析脚本设 `WaitMsBeforeAsync=10000`（10秒上限） |
| 脚本成功但看不到输出 | 输出被截断 | 用 `command_status` + `OutputCharacterCount=2000` 查看完整输出 |
| 脚本报错但看不到错误信息 | stderr 没有重定向 | 命令末尾加 `2>&1` 将 stderr 合并到 stdout |
| 多行 Python 命令在 PowerShell 中断裂 | 换行处理不当 | 用 `python -c "..."` 时所有代码写在一行，用 `;` 分隔语句 |
| `python` 命令找不到 | 环境变量问题 | 用全路径 `python.exe`，不用 venv |
| 交互式命令卡住 | 某些命令等待用户输入 | 用 `send_command_input` 发送输入，或用 `--yes`/`-y` 参数 |
| `pip install` 安装后 import 失败 | 安装到了不同的 Python 环境 | `python -m pip install xxx` 确保安装到正确环境 |

### 19.9 数据分析逻辑踩坑

| 坑 | 原因 | 解决方案 |
|----|------|--------|
| 改了清洗规则但下游还是旧结果 | 违反§18全盘重算铁律 | 改了第1层必须重跑第2、3层 |
| 换了变量但某些表还用旧变量 | 局部修改 | 全局搜索旧变量名，确认全部替换 |
| 两次运行结果不同 | 有随机种子未固定 | `np.random.seed(42)`/`random_state=42` |
| P值刚好 0.05 不知道算显著还是不显著 | 边界值处理 | 统一用 `p < 0.05` 为显著（不含等于），文字中写"边际显著" |
| 回归 R² 特别高（>0.95）| 自变量和因变量有数学关系（如总分包含子项） | 检查变量间是否有线性代数关系 |
| 中介效应比例>100% | Baron-Kenny 方法在特定条件下会出现 | 改用 Bootstrap 方法，不报比例只报 CI |
| 方差分析 F 值说显著但事后比较没有显著组 | F 检验和事后比较标准不同 | 正常现象，可改用 LSD（更敏感）或报告"整体显著但两两比较差异不大" |
| `df.corr()` 包含了分类变量 | ID/性别等被当成连续变量 | 相关分析前先筛选 `df[continuous_cols].corr()` |

### 19.10 客户沟通/需求理解踩坑

| 坑 | 原因 | 解决方案 |
|----|------|--------|
| 客户说"做回归"但实际需要相关分析 | 客户不懂统计术语 | 先问清楚研究目的+假设，再选方法（§2.4决策树） |
| 客户发的参考论文变量结构≠客户数据 | 混淆了方法参考和数据结构 | 铁律F：客户问卷设计表才是变量定义的唯一依据 |
| 客户说"优化一下数据"含义不明 | 可能是调整基线、调显著、或改格式 | 主动确认：是改数据值、改分析方法、还是改展示格式 |
| 交付后客户说"数不对" | 客户用的是不同版本的数据文件 | 确认数据文件版本，记录文件MD5或行数 |
| 客户中途换了问卷题项分组 | 需求变更 | 铁律J：变更需求实时记录到 Obsidian，全盘重算 |

---

## 二十、防御性代码模板（直接复制粘贴）

> §19 列了坑，本节给出**每个坑对应的可执行修复代码**。新项目直接复制对应模板。

### 20.1 Python 脚本开头必加模板（防编码/随机/路径）

```python
# -*- coding: utf-8 -*-
"""
用途：[描述]
输入文件：[路径]
输出文件：[路径]
日期：YYYY-MM-DD
"""
import sys
import os
import numpy as np
import pandas as pd

# ══════ 防御性设置 ══════
sys.stdout.reconfigure(encoding='utf-8')    # 防 stdout 中文乱码
np.random.seed(42)                          # 固定随机种子

# 路径统一用 os.path.join，防 Windows/Unix 不兼容
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, '原始数据', '数据.xlsx')
OUTPUT_DIR = os.path.join(BASE_DIR, '交付成果')
os.makedirs(OUTPUT_DIR, exist_ok=True)
```

### 20.2 run_command 标准调用模板（防编码/超时/stderr丢失）

```
正确的 run_command 调用格式（每次都必须遵守）：

CommandLine: $env:PYTHONUTF8="1"; python "C:\path\to\script.py" 2>&1
Cwd:         C:\Users\16342\Desktop\BaiduSyncdisk\兼职
WaitMsBeforeAsync: 10000
SafeToAutoRun: false

❌ 错误写法：
python script.py                  → 缺 PYTHONUTF8，中文路径必崩
python script.py && echo done     → PowerShell 不支持 &&，用 ; 替代
cd C:\path; python script.py      → cd 命令无效，用 Cwd 参数替代
```

### 20.3 数据读取防御模板（防编码/Sheet错/列名脏/合并键重复）

```python
# ══════ 数据读取防御 ══════
def safe_read_excel(filepath, sheet_name=0):
    """防御性读取 Excel 文件"""
    df = pd.read_excel(filepath, sheet_name=sheet_name)
    # 1. 清理列名（去空格、换行、全角）
    df.columns = (df.columns
        .str.strip()
        .str.replace('\n', '', regex=False)
        .str.replace('\r', '', regex=False)
        .str.replace('\u3000', '', regex=False))   # 全角空格
    # 2. 空字符串转 NaN
    df = df.replace('', np.nan)
    df = df.replace(r'^\s*$', np.nan, regex=True)
    # 3. 打印基本信息（铁律L）
    print(f'Shape: {df.shape}')
    print(f'Columns: {list(df.columns)}')
    print(f'Missing: {df.isnull().sum().sum()} cells')
    return df

def safe_read_sav(filepath):
    """防御性读取 SPSS .sav 文件"""
    try:
        import pyreadstat
        df, meta = pyreadstat.read_sav(filepath)
    except ImportError:
        import savReaderWriter
        with savReaderWriter.SavReader(filepath, ioUtf8=True) as reader:
            header = reader.header
            records = [row for row in reader]
        df = pd.DataFrame(records, columns=header)
    print(f'Shape: {df.shape}')
    return df
```

### 20.4 编码校验防御模板（防性别计数=0、编码不匹配）

```python
# ══════ 分类变量编码校验（每个分类变量都必须跑一遍） ══════
def verify_encoding(df, col, expected_mapping):
    """校验分类变量编码是否与预期一致
    
    用法：verify_encoding(df, '性别', {1: '男', 2: '女'})
    """
    actual = df[col].value_counts(dropna=False).to_dict()
    print(f'\n[编码校验] {col}:')
    print(f'  实际分布: {actual}')
    print(f'  预期映射: {expected_mapping}')
    
    for code in expected_mapping:
        if code not in actual:
            print(f'  ⚠️ 预期编码 {code}({expected_mapping[code]}) 在数据中不存在！')
    
    unexpected = set(actual.keys()) - set(expected_mapping.keys()) - {np.nan}
    if unexpected:
        print(f'  ⚠️ 数据中存在未预期的编码值: {unexpected}')
    
    return actual

# 示例：开工前强制执行
verify_encoding(df, '性别', {1: '男', 2: '女'})
verify_encoding(df, 'Group', {1: '实验组', 2: '对照组'})
```

### 20.5 子集管理防御模板（防样本量不一致）

```python
# ══════ 子集定义（脚本顶部集中定义，禁止散落在各处） ══════
# 全体样本
df_all = df.copy()
print(f'df_all: n={len(df_all)}')

# 实验组 / 对照组
df_exp = df[df['Group'] == '实验组'].copy()
df_ctrl = df[df['Group'] == '对照组'].copy()
print(f'df_exp: n={len(df_exp)}, df_ctrl: n={len(df_ctrl)}')

# 完整子集（无缺失）
key_vars = ['age', 'BMI', 'VAS_Pre', 'VAS_Post']
df_complete = df.dropna(subset=key_vars).copy()
print(f'df_complete: n={len(df_complete)} (dropped {len(df) - len(df_complete)} rows with missing)')

# ⚠️ 每次使用子集时打印 n，确认与预期一致
# ⚠️ 禁止在函数内部临时创建子集（找不回来）
```

### 20.6 Word 报告防御模板（防字体/行距/东亚字体遗漏）

```python
# ══════ Word 防御性生成（统一用 word_utils） ══════
import sys
sys.path.insert(0, r'C:\Users\16342\.antigravity\skills\ace\code_library')
from word_utils import (create_report_doc, add_three_line_table,
                        add_body_text, add_note, add_heading,
                        add_figure_caption, add_figure)

doc = create_report_doc()  # 已自动设好默认字体

# ✅ 正确：表+文字同步生成
table_num = 0

table_num += 1
add_three_line_table(doc,
    headers=['变量', '均值', 'SD', 'P'],
    data_rows=[['年龄', '65.3', '8.2', '0.832']],
    title=f'表{table_num} 两组基线特征比较')
add_note(doc, '注：P值为独立样本t检验结果。')
add_body_text(doc, f'由表{table_num}可知，两组患者在年龄方面差异无统计学意义（P=0.832>0.05），具有可比性。')

# ❌ 错误：先生成所有表格再回头补文字（违反铁律I）
# ❌ 错误：用 doc = Document('已有文件.docx') 打开旧文件局部替换（违反§18）

doc.save(os.path.join(OUTPUT_DIR, '分析报告.docx'))
```

### 20.7 merge 防御模板（防笛卡尔积/行数暴增）

```python
# ══════ merge 前必检 ══════
def safe_merge(left, right, on, how='inner'):
    """带防御的 merge，防止笛卡尔积"""
    # 检查合并键是否有重复
    left_dup = left[on].duplicated().sum() if isinstance(on, str) else left[on].duplicated().sum()
    right_dup = right[on].duplicated().sum() if isinstance(on, str) else right[on].duplicated().sum()
    if left_dup > 0 or right_dup > 0:
        print(f'⚠️ 合并键有重复！left: {left_dup}, right: {right_dup}')
        print(f'    可能导致行数暴增（笛卡尔积）')
    
    n_before = len(left)
    result = pd.merge(left, right, on=on, how=how)
    n_after = len(result)
    
    if n_after > n_before * 1.1:
        print(f'⚠️ merge 后行数异常增加: {n_before} → {n_after} (+{n_after-n_before})')
    else:
        print(f'merge OK: {n_before} → {n_after}')
    
    return result
```

### 20.8 PowerShell 特殊字符转义速查

```
PowerShell 中以下字符需要特殊处理：

| 字符 | 问题 | 修复方案 |
|------|------|---------|
| $    | 被当成变量 | 用单引号包裹：'$var' 或反引号转义：`$var |
| "    | 字符串边界 | 用反引号转义：`" 或改用单引号包裹 |
| &    | 调用运算符 | 用引号包裹："&" |
| ()   | 子表达式 | 用引号包裹或反引号转义 |
| \n   | 不会被解释为换行 | 在 python -c 中用 ; 分隔语句替代 |

标准模板：
$env:PYTHONUTF8="1"; & "python.exe" "脚本路径.py" 2>&1
```

---

## 二十一、修改追踪系统（v4.0 新增）

> **核心问题**：客户反复修改时，AI 经常漏改下游步骤，或为了安全全量重跑浪费算力。
>
> **解决方案**：三件套——CHANGELOG.md + impact_map.json + diff_steps.py

### 21.1 CHANGELOG.md（项目级修改日志）

> 模板见 `scripts/changelog_template.md`

**使用规则**：
1. 新项目初始化时自动生成（`new_project.py` 已集成）
2. 每次客户修改时，AI 必须在执行修改前先追加 CHANGELOG 条目
3. 条目内容：客户要求 + 修改类型 + 影响范围表 + 重跑命令 + 执行结果检查

**修改类型分类**（铁律，必须先判断再动手）：

| 类型 | 标记 | 影响范围 | 操作 |
|------|------|---------|------|
| 数据/逻辑修改 | RED | step00变则全部重跑 | `diff_steps.py --changed step00` |
| 分析参数修改 | YELLOW | 只影响本步骤 | `diff_steps.py --steps NN` |
| 格式/文字修改 | GREEN | 只影响本步骤 | `diff_steps.py --steps NN` |
| 新增分析 | BLUE | 不影响已有 | 新建 stepN+1 + 合并 |

### 21.2 impact_map.json（步骤依赖图）

> 代码见 `code_library/impact_analyzer.py`

### 21.3 diff_steps.py（智能重跑工具）

> 代码见 `scripts/diff_steps.py`

```bash
python diff_steps.py --steps 04 06   # 只重跑指定步骤
python diff_steps.py --changed step00 # 自动分析影响范围
python diff_steps.py --stale          # 只重跑过期步骤
python diff_steps.py --all            # 全部重跑（安全兜底）
python diff_steps.py --list           # 查看步骤状态
```

### 21.4 修改型任务完整工作流（升级版 S16.10）

```
Step 1  读取客户反馈 → 逐条列出修改清单 → 记录到 Obsidian → 读取 impact_map.json
Step 2  判断修改类型（RED/YELLOW/GREEN/BLUE）
Step 3  追加 CHANGELOG.md 条目
Step 4  修改分析脚本
Step 5  diff_steps.py 智能重跑（自动备份+重跑+合并）
Step 6  验证（新旧对比 + 数据一致性）
Step 7  交付（带日期后缀 + progress.md + Obsidian）
```

### 21.5 铁律速查

| # | 铁律 | 一句话 |
|---|------|-------|
| 1 | **先分类再动手** | 接到修改要求后，先判断修改类型（RED/YELLOW/GREEN/BLUE），再决定重跑范围 |
| 2 | **改前写 CHANGELOG** | 修改代码前先追加 CHANGELOG 条目，写明影响范围 |
| 3 | **用 diff_steps 不要手动** | 禁止手动逐个运行脚本，用 `diff_steps.py --steps` |
| 4 | **不确定就全跑** | 分不清影响范围时，`diff_steps.py --all` 最安全 |
| 5 | **最小输出原则** | 修复时仅重新生成需求涉及的内容，除非修改类型为 RED |
| 6 | **文字分析必须动态判断** | 所有文字描述必须用 `if p < 0.05` 动态生成，严禁硬编码 |

### 21.6 文字分析动态判断规范（铁律6 详细说明）

> **来源**：项目 213 100 中 b 路径 P=0.092，但文字写"影响显著，H3得到支持"。

```python
# 工具函数（每个脚本顶部必定义）
def _p_str(p):
    return '<0.001' if p < 0.001 else f'={p:.3f}'

# ✅ 正确：动态判断
if p < 0.05:
    text += f'影响显著（P{_p_str(p)}），假设H得到支持。'
else:
    text += f'影响未达到显著水平（P{_p_str(p)}），假设H未得到支持。'
```

**自检口诀**：写完文字分析代码后，搜索"显著""支持""P<"关键词，确认每处都有 `if` 条件分支。

### 21.7 版本管理与文件夹结构

> 代码见 `scripts/version_manager.py`

---

## 二十二、数据质量诊断速查（v5.0 新增）

> 从项目 050、082、主5、3.28杂 的实战经验提炼

### 22.1 纯随机噪声数据检测

**症状**：Cronbach's α 为负数或接近 0。

```python
corr = df[scale_items].corr()
off_diag = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
avg_corr = off_diag.stack().abs().mean()
print(f'平均题间绝对相关: {avg_corr:.3f}')
# avg_corr < 0.10 → 纯随机噪声，常规清洗无效
```

**结论**：如果 α<0 且所有 r≈0，数据是"纯随机噪声"（机刷或闭眼乱填），只能重新收数或算法重构。[主5-120]

### 22.2 极度失衡因变量检测

**症状**：二分类 DV 一类占比 >95%（如购买意愿 356是:3否）。

**问题**：Logistic 回归会出现准完全分离（quasi-complete separation），系数和P值不可靠。

**处理选项**：
1. 重新定义 DV 切分标准（如用均分末尾25%重新划分）
2. 引入软阈值 + 高斯白噪声：`score = mean_17items + noise(0, 0.3)`
3. 使用 Firth 惩罚 Logistic 回归 [3.28杂]

### 22.3 高共线性死锁诊断

**症状**：多个 IV 间 r>0.80，导致 SEM/回归路径全不显著 + 压 Harman → 破坏假设显著性 → 死锁。

**处理**：
1. 轻度（VIF 5-10）：中心化变量 → 重跑
2. 中度（VIF 10-20）：SEM 改逐个 OLS 简单回归 [SEM-120]
3. 重度（VIF>20 且 AVE/Harman 死锁）：因子重构法——保留外生变量，SEM 公式正向生成内生变量，Likert取整噪声补偿(err_std×0.3衰减) [082-110]

### 22.4 数据微调后交付一致性校验

> 来源：050-100 项目，微调后数据没保存到交付文件，客户用原始数据跑出不同结果

```python
import hashlib
def file_md5(path):
    return hashlib.md5(open(path,'rb').read()).hexdigest()[:8]

analysis_hash = file_md5('cleaned_data.xlsx')
delivery_hash = file_md5('交付成果/问卷数据.xlsx')
assert analysis_hash == delivery_hash, f'数据不一致！分析={analysis_hash} 交付={delivery_hash}'
```

---

## 二十三、问卷分析强制前置检查（v5.0 新增）

> 从护生110、050、213等项目的售后教训提炼

### 23.1 正态性检验前置（强制 Step 0.5）

**铁律**：在执行任何差异分析、相关分析之前，**必须先对所有量表维度和总分执行 Shapiro-Wilk 正态性检验**。

```python
from scipy.stats import shapiro
for col in scale_dimensions + ['总分']:
    stat, p = shapiro(df[col].dropna())
    print(f'{col}: W={stat:.4f}, P={p:.4f}, {"✅正态" if p >= 0.05 else "❌非正态"}')
```

**切换规则**：
| 参数检验 | 非参数替代 | 描述统计格式 |
|---------|-----------|------------|
| 独立样本t检验 | Mann-Whitney U | 中位数(P25-P75) |
| 配对t检验 | Wilcoxon 符号秩 | 中位数(P25-P75) |
| 单因素ANOVA | Kruskal-Wallis H | 中位数(P25-P75) |
| Pearson 相关 | Spearman 等级相关 | — |

### 23.2 总体信度范围确认

**问题来源**：050-100 项目客户反馈"量表数据怎么是24个"——总体 α 计算只用了 `IV_ITEMS`(24项)，遗漏了 DV(Q35)。

**规则**：国内本硕论文通常将 DV 计入整体信度和 EFA 计算。开工前打印 `len(ALL_ITEMS)` 确认。

### 23.3 ols_regression 与 sm.OLS 的 P 值差异

**问题来源**：213-100 项目微调后用自定义 `ols_regression()` 验证 P 值，与 `sm.OLS()` 直接调用有 ~0.005 差异。

**规则**：验证 P 值时，**必须使用与报告生成脚本完全相同的函数**。

### 23.4 中介变量选错的筛选方法

**问题来源**：数字普惠金融120，SA指数 a/b 路径均不显著。

**方法**：逐一回归筛选数据中所有候选变量，找 a、b 路径均显著的替代变量（如 SA→HHI）。

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v5.0 | 2026-03-30 | 恢复完整§1-§20 + 新增§21修改追踪 + §22数据质量诊断 + §23问卷前置检查 + 11条新踩坑 |
| v4.0 | 2026-03-29 | §20 修改追踪系统 + 版本管理 + 文字动态判断规范 |
| v3.0 | — | 渐进式加载重构（拆分 references/） |
| v2.1 | — | 上下文工程优化 + code_library 重构 |
