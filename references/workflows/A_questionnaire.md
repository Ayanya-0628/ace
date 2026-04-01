# 工作流 A：问卷分析全套（最高频 ★★★★★）

**适用场景**：Likert 量表、调查问卷、自编量表、护理/教育/管理类论文

## 标准步骤（严格按顺序）

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

Step 2  人口学描述性统计
        ├─ 分类变量：频数+百分比 -> 表1
        └─ 连续变量：按Step1.5决定的格式 -> 表1

Step 3  各变量描述性统计
        ├─ 各维度得分 -> 表2
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
        └─ 报告 B、SE、beta、t、p、R²

Step 9  中介效应（如有假设需要）
        ├─ 逐步回归（控制其他X维度为协变量） -> 表8
        ├─ Bootstrap中介检验 -> 间接效应a*b + 置信区间 -> 表9
        └─ 置信区间不含0 -> 中介显著

Step 10 Word 报告输出（必须一次性全量生成，参见全盘重算铁律）
        ├─ 所有表格用三线表
        ├─ 每张表后紧跟文字解读
        └─ 图表嵌入（如有）
```

## 代码库对应

| 步骤 | code_library 文件 | 核心函数 |
|------|-------------------|---------|
| Step 1 | `data_clean.py` | `reverse_score()` `calc_dimension_scores()` |
| Step 1.5 | `pretest.py` | `normality_decision()` |
| Step 2-3 | `descriptive.py` | `demographic_table()` `descriptive_stats()` |
| Step 4 | `survey.py` | `cronbachs_alpha()` |
| Step 5 | `survey.py` | `kmo_bartlett()` `efa()` `calc_ave()` `calc_cr()` |
| Step 6 | `correlation.py` | `correlation_matrix_stars()` |
| Step 7 | `ttest.py` `anova.py` | `independent_ttest()` `oneway_anova()` |
| Step 8 | `regression.py` | `ols_regression()` `hierarchical_regression()` |
| Step 9 | `mediation.py` | `bootstrap_mediation()` |
| Step 10 | `word_utils.py` | `add_three_line_table()` `add_body_text()` |

## 参考脚本

- `小灵问卷分析120/main.py`
- `护生110/analysis.py`
- `公共卫生70/analysis.py`
