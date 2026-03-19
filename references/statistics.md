# 统计分析方法详解（按需加载）

> 本文件从 SKILL.md 拆出，包含统计分析模块、实证分析全套、问卷分析模块的详细方法说明和调用示例。
> 日常使用请直接调用 `code_library/` 中的函数即可，需要了解方法原理时再加载本文件。

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