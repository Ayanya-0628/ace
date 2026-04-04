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

# Ace — 数据分析王牌（v6.0 精简版）

> 一站式覆盖实证分析全套、统计检验、问卷分析、论文格式、学术绘图。
> **读取规则**：先查 §1 路由表定位 → 只读对应章节/文件 → 禁止整文件一次性全读。

---

## §1 快速路由表（接到任务后第一步查这里）

### 按任务类型定位

| 任务类型 | 读取文件 | code_library |
|---------|---------|-------------|
| **接单/需求解析** | 本文件 §4 需求解析模板 | — |
| **问卷分析全套** | `references/workflows/A_questionnaire.md` | `survey.py` `pretest.py` `correlation.py` |
| **实证回归全套** | `references/workflows/B_empirical.md` | `regression.py` `pretest.py` |
| **双因素方差分析** | `references/workflows/C_two_way_anova.md` | `anova.py` `ttest.py` |
| **中介/调节效应** | `references/workflows/D_mediation.md` | `mediation.py` |
| **DID双重差分** | `references/workflows/E_did.md` | 专项脚本 |
| **非参数检验** | `references/workflows/F_nonparametric.md` | `ttest.py` |
| **医学多表** | `references/workflows/G_medical.md` | `descriptive.py` `regression.py` |
| **SERVQUAL** | `references/workflows/H_servqual.md` | `survey.py` |
| **客户反馈修改** | `references/workflows/I_modification.md` | `report_builder.py` |
| **售后任务** | `references/aftercare.md` | — |
| **Word报告格式** | 本文件 §5 + `word_utils.py` | `word_utils.py` |
| **学术绘图** | 本文件 §5.4 + `plot_bindent.py` | `plot_bindent.py` |
| **踩坑排查** | `references/pitfalls.md` | — |
| **术语翻译** | `references/glossary.md` | — |
| **文字分析模板** | `references/text_templates.md` | — |
| **防御性代码** | `references/defense_templates.md` | — |
| **通用检查清单** | `references/workflows/checklist.md` | — |
| **ML/随机森林** | `references/ml_guide.md` | `ml_pipeline.py` |
| **Meta分析** | `references/meta_analysis.md` | `meta_analysis.py` |
| **SPSS语法生成** | `references/spss_workflow.md` | `generate_spss_syntax_template.py` |

### code_library 函数速查

| 文件 | 核心函数 | 用途 |
|------|---------|------|
| `data_clean.py` | `reverse_score()` `calc_dimension_scores()` `check_encoding()` | 数据清洗 |
| `pretest.py` | `normality_decision()` `check_vif()` `check_homogeneity()` | 前置检验 |
| `survey.py` | `cronbachs_alpha()` `kmo_bartlett()` `efa()` `calc_ave()` `calc_cr()` | 信效度 |
| `correlation.py` | `correlation_matrix_stars()` `significance_stars()` `mean_sd()` | 相关分析 |
| `ttest.py` | `independent_ttest()` `paired_ttest()` `mann_whitney_u()` `wilcoxon_test()` | t检验 |
| `anova.py` | `oneway_anova()` `kruskal_test()` | 方差分析 |
| `regression.py` | `ols_regression()` `hierarchical_regression()` `logistic_regression()` | 回归 |
| `mediation.py` | `baron_kenny_mediation()` `bootstrap_mediation()` `moderation_test()` | 中介/调节 |
| `descriptive.py` | `demographic_table()` `chi_square_test()` `descriptive_stats()` `batch_chi_square()` `frequency_table()` `cramers_v()` | 描述统计+卡方 |
| `did.py` | `did_estimate()` `parallel_trend_test()` `iv_2sls()` | DID+工具变量 |
| `word_utils.py` | `add_three_line_table()` `add_body_text()` `add_note()` `create_report_doc()` | Word报告 |
| `report_builder.py` | 三层架构模板 + `verify_report()` | 全盘重算 |
| `ml_pipeline.py` | `train_random_forest()` `optuna_tune()` `shap_explain()` | 机器学习 |
| `plot_bindent.py` | `FONT_SONG` `FONT_HEI` `FONT_TNR` + `grouped_bar()` `line_with_sem()` `horizontal_bar()` `district_choropleth()` `plot_roc()` `add_significance()` `set_ax_fonts()` `save_fig()` | 绘图 |

---

## §2 铁律速查（每次都必须遵守，合并去重后共 25 条）

| # | 铁律 | 一句话 |
|---|------|-------|
| 1 | **全盘重算** | 改了上游必须重跑所有受影响的下游，Word 报告所有内容来自同一次运行 |
| 2 | **表+文字同步** | 每个 `add_three_line_table()` 后面必须紧跟 `add_body_text()` 文字分析 |
| 3 | **正态检验前置** | 分析前先 Shapiro-Wilk 检验，决定用参数/非参数路线，不可跳过 |
| 4 | **三层隔离** | load_and_clean() → analyze(df) → generate_report(results)，禁止跨层引用 |
| 5 | **数据集确认** | 每次分析前先 `df.shape` + `value_counts()` 确认数据集正确 |
| 6 | **eastAsia字体** | 每个 `add_run()` 后必须 `rFonts.set(qn('w:eastAsia'), '宋体')`，用 `set_cell_font()` |
| 7 | **防御性开头** | 每个脚本：`sys.stdout.reconfigure(encoding='utf-8')` + `np.random.seed(42)` + `os.path.join()` |
| 8 | **动态判断** | 所有文字结论用 `if p < 0.05` 动态生成，严禁硬编码"显著""支持" |
| 9 | **术语中文化** | 英文术语首次出现必须附中文全称，详见 `references/glossary.md` |
| 10 | **标准句式** | 文字分析必须使用 `references/text_templates.md` 中的标准句式骨架 |
| 11 | **去AI味** | 删除"值得注意的是""综合来看"，用"降低"不用"下降" |
| 12 | **Matplotlib字体** | 禁用 `rcParams` 全局字体，用 `FontProperties(fname=)` 逐元素指定 |
| 13 | **禁用tight** | `savefig()` 禁用 `bbox_inches='tight'`，用 `fig.subplots_adjust()` 手动布局 |
| 14 | **编码校验** | 分类变量先 `value_counts()` 确认编码，防止性别计数=0 |
| 15 | **子集集中定义** | 脚本顶部统一定义所有子集变量名+注释，禁止在函数内部临时创建 |
| 16 | **PowerShell模板** | `$env:PYTHONUTF8="1"; python "script.py" 2>&1`，用 Cwd 不用 cd |
| 17 | **SPS文件GBK** | `.sps` 文件必须用 GBK + CRLF 写入，禁止用 replace_file_content 编辑 |
| 18 | **不覆盖已交付** | 修改后带日期后缀另存，不覆盖原文件 |
| 19 | **源码保留** | `_tmp_*.py` 改名为描述性名称保留，添加中文文件头注释 |
| 20 | **需求解析** | 接单后必须按 §4 模板输出结构化需求摘要，用户确认后才分析 |
| 21 | **读原始Excel** | 数据核查必须读原始文件 → 与整理表对比 → 有据可查的结论 |
| 22 | **参考论文≠数据** | 参考论文仅参考分析方法/表格格式/量表计分，**严禁从论文推断人口学编码**（如岗位/学历选项）。客户没给编码对照→一律输出数字[A177] |
| 23 | **公式文档按需** | 仅客户明确要求时才生成公式说明文档，不要求则不生成 |
| 24 | **需求变更记录** | 客户每次修改要求必须同步记录到 Obsidian `兼职/{项目}/YYYY-MM-DD_客户需求记录.md` |
| 25 | **代码整理** | 脚本完成后：中文文件头注释 + import排序 + `# ══════` 段落分隔 + 删调试print + 重命名_tmp_*.py |
| 26 | **精准修改** | 售后/修改只做客户明确要求的题目/分析，不扩大修改范围（改Q9不要重做Q1-Q30）；但若修改涉及数据/变量定义变动，受影响的下游表格/文字/图必须联动更新 |
| 27 | **文件清单** | 每个项目根目录维护 `文件清单.md`，新建/修改脚本或交付文件后立即更新清单，模板见 `references/file_registry_template.md` |

---

## §3 统计方法决策树（方法选择）

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
    ├─ 中介效应 → Bootstrap（5000次，控制协变量，CI不含0判显著） + Baron-Kenny/Sobel（补充）
    └─ 调节效应 → 交互项 + 简单斜率分析
```

---

## §4 需求解析模板（接单后第一步必须输出）

> **铁律**：接到任何分析任务后，必须先按此模板输出结构化需求摘要，不能只写一句话。
> 用户确认后才进入分析阶段。

### 4.1 必填项（缺一不可）

```
┌─────────────────────────────────────────────────────┐
│ 【项目名称】：______                                  │
│ 【研究类型】：问卷 / 实证 / 医学 / 实验 / 其他         │
│ 【样本量】：N = ______                                │
│ 【数据格式】：Excel / SPSS(.sav) / CSV / 其他         │
│ 【数据概况】：____行 × ____列，缺失值____个            │
│ 【核心问题】：用一句中文概括客户想知道什么               │
│                                                       │
│ 【变量结构】：                                         │
│   自变量(X)：______ (几个维度，每维度几题)              │
│   因变量(Y)：______                                   │
│   中介变量(M)：______ (无则填"无")                     │
│   调节变量(W)：______ (无则填"无")                     │
│   控制变量：______ (人口学变量列举)                     │
│                                                       │
│ 【编码对照】：                                         │
│   □ 客户提供了编码对照表(1=XX,2=XX)                    │
│   □ 客户未提供 → 一律输出数字(选项1/选项2)，开工前问   │
│                                                       │
│ 【量表类型】：Likert 5点 / 7点 / 连续 / 分类           │
│ 【反向计分题】：有(题号:____) / 无                      │
│ 【分析方法】(根据§3决策树选定)：                        │
│   □ 信效度  □ 描述统计  □ 差异分析                    │
│   □ 相关分析  □ 回归  □ 中介  □ 调节                  │
│   □ 卡方  □ ANOVA  □ 其他:______                      │
│                                                       │
│ 【匹配工作流】：A/B/C/D/E/F/G/H (可组合)              │
│ 【客户特殊要求】：______ (SPSS输出/指定方法/等)         │
│ 【参考论文用途】：仅参考方法 / 参考格式 / 无参考        │
└─────────────────────────────────────────────────────┘
```

### 4.2 填写规则

1. 接到数据后先用 Python 读取 `df.shape`、`df.columns`、关键变量 `value_counts()`
2. 按上述模板填写，**全部使用中文描述**，禁止出现客户看不懂的纯英文术语
3. 输出给用户确认后才进入分析阶段
4. 模板填写内容同步记录到 Obsidian 项目记忆

### 4.3 工作流匹配速查

| 需求描述模式 | 匹配工作流 |
|-------------|-----------|
| "问卷分析+出报告" | A全套 |
| "信效度+差异+回归" | A(Step4-8) |
| "信效度+差异+回归+中介" | A + D |
| "实证分析全套" | B全套 |
| "实证+稳健+内生" | B(Step5-7) |
| "回归+中介+调节" | B + D |
| "方差分析+画图" | C + 绘图 |
| "DID+异质性+绘图" | E + 绘图 |
| "证型分布+影响因素+关联" | G全套 |
| "SPSS出表" | A/C + SPSS |

### 4.4 快速报价参考

| 分析复杂度 | 典型内容 | 参考价格 |
|-----------|---------|---------| 
| 简单 | 单项分析（t检验/卡方/描述统计） | 30-50 |
| 标准 | 问卷全套（信效度+差异+回归） | 70-100 |
| 进阶 | 全套+中介/调节效应 | 100-150 |
| 复杂 | 实证全套（回归+稳健+内生+异质） | 100-200 |
| 大型 | 医学多表40+张/PCOS级 | 300-400 |
| 专项 | 随机森林调参/Meta分析 | 60-120 |

---

## §5 输出格式规范

### 5.1 Word 文档字体规范

| 元素 | 中文字体 | 英文/数字字体 | 字号 |
|------|---------|-------------|------|
| 正文 | 宋体 | Times New Roman | 小四（10.5pt） |
| 标题 | 黑体 | Times New Roman | 按级别递减 |
| 表格 | 宋体 | Times New Roman | 小五（9pt） |
| 注释 | 宋体 | Times New Roman | 五号（10.5pt） |
| 图题 | 宋体 | Times New Roman | 8pt |

- **首行缩进**：2字符（约0.74cm）
- **行距**：1.5倍行距（表格内：单倍行距）
- **字体颜色**：默认黑色
- **所有 Word 生成必须导入** `code_library/word_utils.py`，禁止手写字体设置代码

### 5.2 三线表格式

```
顶粗线 ════════════════════════════
           表头行
栏目细线 ──────────────────────────
 数据行
 数据行
底粗线 ════════════════════════════
注：...
```

**表格单元格必须单独设**：单倍行距 + 段前段后0 + 无缩进 + 居中对齐。
代码使用 `add_three_line_table(doc, headers, data_rows, title='表X ...')`。

### 5.3 交叉分析大表格式（默认）

每个维度一张表，所有指标纵向堆叠：

```
指标 │ 选项 │ 分组A(频数%) │ 分组B(频数%) │ 合计 │ χ² │ P值
```

- 指标名仅首行显示
- χ²和P值仅在每个指标最后一行显示
- 详见 `references/statistics.md`

### 5.4 学术绘图规范

**字体铁律**：`rcParams['font.sans-serif']` 不可靠！必须用 `FontProperties(fname=)` 逐元素指定。

```python
from matplotlib.font_manager import FontProperties
FONT_SONG = FontProperties(fname=r'C:\Windows\Fonts\simsun.ttc')   # 宋体 → 中文正文
FONT_HEI  = FontProperties(fname=r'C:\Windows\Fonts\simhei.ttf')   # 黑体 → 标题
FONT_TNR  = FontProperties(family='Times New Roman')                # TNR  → 英文/数字
```

| 元素 | 中文 | 英文/数字 | 字号 |
|------|------|----------|------|
| 标题 | 宋体/黑体 | TNR | 10pt |
| 轴标签 | 宋体 | TNR | 9pt |
| 刻度 | - | TNR | 8pt |
| 图例 | 宋体 | TNR | 8pt |

**布局铁律**：
- 用 `fig.subplots_adjust()` 手动布局
- **禁止** `bbox_inches='tight'`
- 保存：`fig.savefig('x.png', dpi=200, facecolor='white')`
- 默认**不添加**背景网格线

**图表模板**：优先从 `plot_templates/` 复用已有模板，详见 `references/plot_reuse.md`。

### 5.5 文字分析写作规范

**核心原则**：一整段连贯文字，首行缩进2字符，客观陈述数据，不写推测性语言。

**段落结构**：
1. "由表X可知" 开头 + 宏观概述
2. 用百分比描述组间差异
3. 列出各组具体特征
4. 过渡词：中间用"此外"，最后用"就XX而言"
5. 结尾"这表明..."因果总结

**强制使用标准句式模板**：详见 `references/text_templates.md`。

**去AI味**：详见 `references/text_templates.md` 末尾的检查清单。

### 5.6 文件命名规范

| 文件类别 | 命名格式 | 示例 |
|---------|---------|------|
| **脚本** | `step{NN}_{功能}.py` | `step01_descriptive.py` |
| 脚本修改版 | `step{NN}_v{N}_{功能}.py` | `step06_v2_chi_square.py` |
| 合并脚本 | `merge_all.py`（唯一） | — |
| **交付报告** | `{项目短名}_报告_v{N}_{MMDD}.docx` | `adam_报告_v2_0404.docx` |
| **交付数据** | `step{NN}_{分析名称}.xlsx` | `step01_描述统计.xlsx` |
| 交付数据修改版 | `step{NN}_v{N}_{分析名称}.xlsx` | `step06_v2_卡方分析.xlsx` |
| **清洗数据** | `cleaned_data.xlsx`（唯一） | — |
| **图片** | `fig{NN}_{描述}.png` | `fig01_district_heatmap.png` |
| **SPSS** | `{项目短名}_syntax.sps` / `.sav` | `adam_syntax.sps` |

**核心规则**：
- 修改版加 `_v{N}` 后缀，**保留旧版本不覆盖**（铁律18）
- 报告文件名必须带日期 `_MMDD`
- 禁止空格、中文括号、"新建"、"副本"、"(1)"
- 每个项目根目录维护 `文件清单.md`（铁律27），模板见 `references/file_registry_template.md`

---

## §6 术语中文对照表

> 完整对照表见 `references/glossary.md`

**规则**：英文术语在 Word 报告中**首次出现**时必须用「中文全称(英文缩写)」格式。示例：

| 场景 | ❌ 错误写法 | ✅ 正确写法 |
|------|-----------|-----------|
| 首次提及 | Cronbach's α为0.856 | 克朗巴赫α信度系数(Cronbach's α)为0.856 |
| 后续提及 | Cronbach's α为0.912 | α系数为0.912 |
| 首次提及 | KMO值为0.841 | KMO取样适当性度量为0.841 |
| 首次提及 | Bootstrap检验 | 自抽样法(Bootstrap)检验 |

---

## §7 全盘重算架构（核心）

### 7.1 三层隔离脚本模板

```python
# ══════ 第1层：数据加载与清洗 ══════
def load_and_clean():
    """从原始数据加载，返回清洗后的 DataFrame"""
    df = pd.read_excel(INPUT_FILE)
    return df

# ══════ 第2层：统计分析 ══════
def analyze(df):
    """所有统计分析，返回 results 字典"""
    results = {}
    return results

# ══════ 第3层：报告生成 ══════
def generate_report(results):
    """只从 results 字典取值，禁止跨层引用"""
    doc = Document()
    doc.save(OUTPUT_DOCX)

# ══════ 主入口 ══════
if __name__ == '__main__':
    df = load_and_clean()
    results = analyze(df)
    generate_report(results)
```

### 7.2 判断规则

| 改了什么 | 重跑范围 |
|---------|---------|
| 第1层（清洗规则/变量定义/筛选条件） | 第1+2+3层全部重跑 |
| 第2层（某个分析的参数） | 该分析+对应表格+文字 |
| 第3层（仅格式调整） | 只改第3层 |
| 拿不准 | 全盘重跑最安全 |

### 7.3 验证机制

重跑后必须验证：Word文字中的数字 = 表格中的数字 = 脚本计算结果。
验证脚本见 `scripts/verify_report.py`。

---

## §8 SPSS 注意事项

- 本机 SPSS 27 无法使用无头模式（Java Bug），禁止尝试后台调用
- 如需 SPSS 原生输出：Python 生成 `.sps` 语法 → 用户手动在 SPSS 中运行
- `.sps` 文件必须用 **GBK + CRLF** 编码写入
- 回归语法必加 `TOL`：`/STATISTICS COEFF OUTS R ANOVA COLLIN TOL`
- 详见 `references/spss_workflow.md`

---

## §9 数据质量诊断速查

### 纯随机噪声检测

α<0 且所有题间 r≈0 → 数据是"纯随机噪声"，常规清洗无效。

### 极度失衡因变量

二分类 DV 一类占比 >95% → Logistic 回归出现准完全分离。
处理：重新定义切分标准 / Firth惩罚Logistic。

### 高共线性死锁

多个 IV 间 r>0.80 → SEM/回归路径全不显著。
处理：轻度中心化，中度改逐个OLS，重度因子重构。

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v6.2 | 2026-04-04 | 新增§5.6文件命名规范 + 铁律27「文件清单」；新增 `references/file_registry_template.md` 模板 |
| v6.1 | 2026-04-04 | 新增铁律26「精准修改」；code_library大整理：descriptive.py+batch_chi_square/frequency_table, plot_bindent.py v3.0重写(清理裸代码+新增horizontal_bar/district_choropleth/save_fig), did.py v2.0重写(did_estimate/parallel_trend_test/iv_2sls) |
| v6.0 | 2026-03-31 | 精简重构：2476行→~600行；拆分工作流到独立文件；新增§4需求模板+§6术语表+text_templates |
| v5.1 | 2026-03-30 | 新增§24售后工作流 |
| v5.0 | 2026-03-30 | §21修改追踪 + §22数据质量诊断 + §23问卷前置检查 |
| v4.0 | 2026-03-29 | §20修改追踪系统 + 版本管理 + 文字动态判断规范 |
