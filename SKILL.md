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

> **核心原则**：先查路由表定位 → 核心内容在本文件 → 详细参考在 `references/` 目录按需加载。
>
> **references/ 目录**：`statistics.md`(统计/实证/问卷) | `ml_guide.md`(机器学习) | `spss_workflow.md`(SPSS) | `meta_analysis.md`(Meta分析) | `pitfalls.md`(踩坑+防御)

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
| **分步执行/合并报告** | 🔴 分步执行架构 | `scripts/step_template.py` `scripts/merge_report.py` |

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
| `mediation.py` | `bootstrap_mediation()`(默认) `baron_kenny_mediation()`(补充) `moderation_test()` | 中介/调节 |
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
    ├─ 中介效应 → 🔴 Bootstrap（5000次，默认）+ Baron-Kenny（补充）
    └─ 调节效应 → 交互项 + 简单斜率分析
```

---

## 📂 统计分析 / 实证分析 / 问卷分析 → 按需加载

> §3 统计分析、§4 实证分析、§5 问卷分析的详细方法和代码已移至 `references/statistics.md`。
> 日常直接调用 `code_library/` 中对应函数即可。

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

## 📂 机器学习 → 按需加载

> §9 机器学习建模模块已移至 `references/ml_guide.md`。
> 仅在涉及随机森林、XGBoost、SHAP 等 ML 任务时加载。

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

## 📂 SPSS 专项 → 按需加载

> §11 SPSS 原生输出工作流已移至 `references/spss_workflow.md`。

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
- 中介效应表 → 解读间接效应值 + Bootstrap 95% CI（🔴 默认 Bootstrap）

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

## 📂 绘图代码沉淀 + Meta 分析 → 按需加载

> §14 绘图代码存储规范 → `references/plot_reuse.md`
> §15 Meta 分析模块 → `references/meta_analysis.md`

---

## 🔴 分步执行架构（v3.1 核心升级 — 替代一次性全跑）

> **核心原则**：每个独立分析步骤生成独立 `.docx`（完整三线表+文字分析），最后合并为一份报告。
> 
> **替代关系**：本架构替代旧的 "Step 10 一次性全量生成" 模式。旧工作流的步骤定义（清洗→信度→效度→...）仍然有效，只是执行方式从"一个脚本全跑"改为"分步独立执行"。

### 架构总览

```
项目目录/
├── 原始数据/                          ← 客户数据（只读）
├── 交付成果/
│   ├── cleaned_data.xlsx              ← Step 0 输出（所有后续步骤共用）
│   ├── 01_人口学基本特征.docx          ← Step 1 独立文档
│   ├── 02_信度效度分析.docx            ← Step 2 独立文档
│   ├── 03_描述性统计.docx              ← Step 3 独立文档
│   ├── 04_差异分析.docx                ← Step 4 独立文档
│   ├── 05_相关分析.docx                ← Step 5 独立文档
│   ├── 06_回归分析.docx                ← Step 6 独立文档
│   ├── 07_中介效应.docx                ← Step 7 独立文档（如有）
│   └── 分析报告（合并版）.docx          ← merge_report.py 合并
├── step00_clean.py                     ← 数据清洗（唯一写 cleaned_data.xlsx 的脚本）
├── step01_demographic.py               ← 复制自 scripts/step_template.py
├── step02_reliability.py
├── step03_descriptive.py
├── step04_difference.py
├── step05_correlation.py
├── step06_regression.py
├── step07_mediation.py                 ← 按需
└── merge_all.py                        ← 调用 scripts/merge_report.py
```

### 执行流程

```
Phase 1  数据清洗（step00_clean.py）
         ├─ 读原始数据 → 清洗 → 保存 cleaned_data.xlsx
         ├─ 包含：反向计分、缺失值处理、编码校验、维度得分计算
         ├─ 正态性检验决策（决定后续所有步骤用参数/非参数）
         └─ ⚠️ 这是唯一会被其他步骤依赖的脚本

Phase 2  分步独立分析（step01 ~ stepN，可并行/按序执行）
         ├─ 每步：读 cleaned_data.xlsx → 分析 → 生成独立 .docx
         ├─ 每个 .docx 包含完整的：标题 + 三线表 + 表注 + 文字分析
         ├─ 步骤间不共享 Python 变量（通过文件传递数据）
         └─ 每步完成后立即打印 OK / 汇报要点

Phase 3  合并（merge_all.py → 调用 scripts/merge_report.py）
         ├─ 按文件名编号排序合并所有 .docx
         ├─ 自动重新编号（表1、表2、... 全局连续）
         └─ 输出：分析报告（合并版）.docx
```

### 分步执行铁律

| # | 铁律 | 说明 |
|---|------|------|
| 1 | **每步独立读 cleaned_data.xlsx** | 不从上一步 import 变量，不用 pickle 传中间结果 |
| 2 | **每个 .docx 必须完整** | 包含标题、三线表、表注、文字分析段落（和最终版完全一致） |
| 3 | **改了 step00 必须重跑所有** | 清洗逻辑变了 → cleaned_data.xlsx 变了 → 所有步骤重跑 |
| 4 | **改了 stepN 只需要重跑 stepN** | 分析参数变了只重跑该步骤，然后重新合并 |
| 5 | **合并前检查所有步骤的 n** | 每步文档中的样本量必须一致 |
| 6 | **文件命名必须带编号前缀** | `01_xxx.docx`、`02_xxx.docx`，保证合并顺序 |

### 模板和工具

| 工具 | 路径 | 用途 |
|------|------|------|
| **分步脚本模板** | `scripts/step_template.py` | 复制为 `stepXX_xxx.py`，改 `STEP_CONFIG` 和 `analyze()` |
| **合并报告脚本** | `scripts/merge_report.py` | `python scripts/merge_report.py "交付成果/"` |
| **项目初始化** | `scripts/new_project.py` | `python scripts/new_project.py "项目名"` |
| **报告验证** | `scripts/verify_report.py` | `python scripts/verify_report.py "报告.docx"` |

### 与旧工作流的关系

> 旧的 §16 工作流（A-I）定义了**分析步骤和统计方法**，这些仍然有效。
> 本架构改变的是**执行方式**：从"一个脚本从头跑到尾"改为"分步独立执行+合并"。
> 
> 示例：问卷分析全套（工作流A）
> - **旧方式**：一个 `analysis.py` 包含 Step 1-10，一次性运行生成一个完整报告
> - **新方式**：`step00_clean.py` + `step01_demographic.py` + ... + `merge_all.py`
> - **分析步骤完全一样**（清洗→信度→效度→相关→差异→回归），只是每步独立出文件

### 客户修改时的处理

```
客户要求修改 → 判断影响范围：
├─ 改了数据清洗条件 → 重跑 step00 + 所有后续步骤 + 重新合并
├─ 改了某个分析的参数 → 只重跑对应 stepN + 重新合并
├─ 改了某个表的格式 → 只重跑对应 stepN + 重新合并
└─ 加了一个新分析 → 新建 stepN+1 + 重新合并
```

### 与 §18 全盘重算的关系

> §18 铁律仍然有效，但适用范围缩小：
> - **step00 变了** → 等价于"改了上游"，需要全部重跑（但每步独立执行，出错好定位）
> - **stepN 变了** → 只需要重跑 stepN，不需要重跑其他步骤（这就是分步的优势）
> - **合并** → 始终最后执行，确保最终报告的所有数据来自最新的独立文档

---

## 十六、标准化分析工作流（接单即用）

> **核心思想**：接到任务后先对号入座选工作流，按步骤依次执行，不跳步不漏步。
> 每类工作流标注了：适用场景 → 标准步骤 → Word 报告输出物清单。
> 
> **🔴 执行方式**：使用上方"分步执行架构"，每个 Step 对应一个独立脚本和独立文档。

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

Step 9  中介效应（如有假设需要，🔴 默认 Bootstrap）
        ├─ bootstrap_mediation(df, x, m, y, n_boot=5000) -> 表8
        ├─ 95% CI 不含0 -> 间接效应显著 -> 表9
        └─ 中介类型判断（部分/完全）

Step 10 报告输出（🔴 使用分步执行架构）
        ├─ 每个 Step 独立生成 .docx（完整三线表+文字分析）
        ├─ 最后 merge_report.py 合并为一份
        └─ 参见上方「分步执行架构」
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

Step 9  报告输出（🔴 使用分步执行架构）
        ├─ 每个 Step 独立生成 .docx
        └─ merge_report.py 合并
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

Step 6  报告输出（🔴 使用分步执行架构）
        ├─ 三线表格式（§6.2）+ 结果分析段落（§8）
        └─ 每步独立 .docx → merge_report.py 合并
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

Step 4  中介效应检验（🔴 默认 Bootstrap）
        ├─ Bootstrap 法（默认，5000次重采样）：
        │   ├─ from mediation import bootstrap_mediation
        │   ├─ result = bootstrap_mediation(df, x, m, y, n_boot=5000)
        │   ├─ 95% CI 不含0 → 间接效应显著
        │   └─ 报告：间接效应值 + 95% CI [lower, upper]
        ├─ Baron-Kenny 法（补充，客户指定时才用）：
        │   ├─ c路径：X → Y（总效应）
        │   ├─ a路径：X → M
        │   ├─ b+c'路径：X + M → Y
        │   └─ Sobel检验 + 中介比例
        ├─ 中介类型判断：
        │   ├─ CI不含0 + c'显著 → 部分中介
        │   ├─ CI不含0 + c'不显著 → 完全中介
        │   └─ CI包含0 → 中介不成立
        └─ ⚠️ 不报中介比例（Bootstrap 下无意义），只报 CI

Step 5  调节效应检验（如有）
        ├─ 交互项回归：X + W + X*W → Y
        ├─ X*W 系数显著 → 调节效应存在
        └─ 简单斜率分析（W=M±1SD）

Step 6  调节效应图
        ├─ 高/低调节变量下 X→Y 的斜率
        └─ 参见第七章绘图模板

Step 7  报告输出（🔴 使用分步执行架构）
        ├─ 回归表 + Bootstrap CI 表 + 调节效应图
        └─ 每步独立 .docx → merge_report.py 合并
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

Step 7  报告输出（🔴 使用分步执行架构）
        └─ 每步独立 .docx → merge_report.py 合并
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

Step 5  报告输出（🔴 使用分步执行架构）
        └─ 每步独立 .docx → merge_report.py 合并
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

Step 8  报告输出（🔴 使用分步执行架构）
        ├─ 每步独立 .docx（每张表必须有文字解读）
        └─ merge_report.py 合并（40+张表自动重编号）
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

Step 7  报告输出（🔴 使用分步执行架构）
        └─ 每步独立 .docx → merge_report.py 合并
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
  - 中介表 → 解读间接效应值+Bootstrap 95% CI（🔴 默认Bootstrap）
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

> **核心铁律**：分步架构下，修改范围精确到 step 级别。改了 step00 → 全部重跑；改了 stepN → 只重跑 stepN + 重新合并。

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

Step 4  重跑受影响的步骤（🔴 分步架构下）
        ├─ 改了 step00（清洗）→ 重跑所有 step01-stepN
        ├─ 改了 stepN（某个分析）→ 只重跑 stepN
        ├─ 每步独立执行，出错好定位
        └─ 重跑后执行 merge_report.py 重新合并

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
- **绝对禁止**：只用 python-docx 打开旧Word修改个别单元格
- **绝对禁止**：脚本中用 `if 已存在: 跳过` 逻辑
- **正确做法**：重跑受影响的 stepN 脚本 → 重新合并，确保一致性

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
| 中介效应、Mediation、Bootstrap、Sobel | **D 中介** | §4.5 |
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

---

## 📂 踩坑速查 + 防御模板 → 按需加载

> §19 实战踩坑速查表（65+条）→ `references/pitfalls.md`
> §20 防御性代码模板（8个模板）→ `references/pitfalls.md`
> 遇到问题时加载排查，新项目时加载复制防御模板。
