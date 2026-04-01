# 工作流 B：实证回归分析（★★★★）

**适用场景**：经管类实证论文、面板数据回归、截面数据回归

## 标准步骤

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

## 代码库对应

| 步骤 | code_library 文件 | 核心函数 |
|------|-------------------|---------|
| Step 1 | `data_clean.py` | `check_encoding()` |
| Step 2 | `descriptive.py` | `descriptive_stats()` |
| Step 3 | `correlation.py` | `correlation_matrix_stars()` |
| Step 4 | `pretest.py` | `check_vif()` |
| Step 5 | `regression.py` | `ols_regression()` |
| Step 6-8 | `regression.py` | `ols_regression()` 分组调用 |
| Step 9 | `word_utils.py` | `add_three_line_table()` |

## 参考脚本

- `甜不辣100/analysis.py`
- `数字普惠120/empirical_analysis.py`
