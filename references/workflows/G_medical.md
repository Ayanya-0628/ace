# 工作流 G：医学多表综合分析（★★★）

**适用场景**：中医证型分析、体质分布、多维度交叉、大型医学数据

## 标准步骤

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
        └─ 参见交付规范
```

## 代码库对应

| 步骤 | 文件 | 函数 |
|------|------|------|
| Step 2 | `descriptive.py` | `demographic_table()` `chi_square_test()` |
| Step 5 | `regression.py` | `logistic_regression()` |
| Step 8 | `word_utils.py` | `add_three_line_table()` |

## 参考脚本

- `医学400/_step2_analysis_full.py`
- `实证全套100/analysis_full.py`
