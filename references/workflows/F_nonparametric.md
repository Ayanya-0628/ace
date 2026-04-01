# 工作流 F：非参数检验（★★）

**适用场景**：小样本、有序数据、不满足正态性假设

## 标准步骤

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

## 代码库对应

| 步骤 | 文件 | 函数 |
|------|------|------|
| Step 1 | `pretest.py` | `normality_decision()` |
| Step 2 | `ttest.py` | `mann_whitney_u()` |
| Step 5 | `word_utils.py` | `add_three_line_table()` |

## 参考脚本

- `Wilcoxon80/analysis.py`
- `下颌骨150/_analysis.py`
