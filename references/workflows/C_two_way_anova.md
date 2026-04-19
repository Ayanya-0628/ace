# 工作流 C：双因素方差分析（★★★）

**适用场景**：A因素×B因素对多指标的影响，如 组别×时间点 对 HR/MAP/BIS

## 标准步骤

```
Step 1  读取数据 → 长格式（subject_id, 因素A, 因素B, 指标值）
Step 2  描述性统计：各组合(A×B)的均值±标准差
Step 3  正态性 + 方差齐性检验
Step 4  双因素 ANOVA
        ├─ statsmodels ols + anova_lm(typ=2)
        ├─ 报告 F值 + p值（主效应A、主效应B、交互效应A×B）
Step 5  LSD 多重比较
        ├─ 同组内不同时间 → 小写字母
        ├─ 不同组别均值 → 大写字母
        └─ 紧凑字母显示 CLD
Step 6  三线表 Word 输出
Step 7  结果分析段落
```

## 字母标记规则

- **小写字母** = 同组内不同时间 LSD（P<0.05）
- **大写字母** = 不同因素水平 LSD（P<0.05）

## 代码库对应

| 步骤 | 文件 | 函数 |
|------|------|------|
| Step 3 | `pretest.py` | `normality_decision()` `check_homogeneity()` |
| Step 4-5 | `anova.py` | `oneway_anova()` |
| Step 6 | `word_utils.py` | `add_three_line_table()` |

## 参考脚本

- `心率50/anova_spss.py`
- `方差分析160/analysis_pipeline.py`
