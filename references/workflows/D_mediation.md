# 工作流 D：中介/调节效应分析（★★★★）

**适用场景**：X→M→Y 中介、X*W→Y 调节、被调节的中介

## 标准步骤

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
        ├─ Bootstrap检验（默认方法）
        │   ├─ 重抽样 5000 次
        │   ├─ 计算间接效应 a×b 的置信区间
        │   └─ CI 不含 0 → 间接效应显著
        ├─ 中介类型判断：
        │   ├─ 间接效应显著 + c'显著 → 部分中介
        │   ├─ 间接效应显著 + c'不显著 + c显著 → 完全中介
        │   ├─ 间接效应显著 + c'不显著 + c不显著 → 仅间接中介
        │   └─ CI 含 0 → 中介不成立
        └─ Sobel检验仅作补充说明

Step 5  调节效应检验（如有）
        ├─ 交互项回归：X + W + X*W → Y
        ├─ X*W 系数显著 → 调节效应存在
        └─ 简单斜率分析（W=M±1SD）

Step 6  调节效应图（高/低调节变量下 X→Y 的斜率）

Step 7  Word 输出：逐步回归表 + Bootstrap中介结果表 + 调节效应图
```

## 代码库对应

| 步骤 | 文件 | 函数 |
|------|------|------|
| Step 4 | `mediation.py` | `bootstrap_mediation()` `baron_kenny_mediation()` |
| Step 5 | `mediation.py` | `moderation_test()` |
| Step 7 | `word_utils.py` | `add_three_line_table()` |

## 参考脚本

- `线性回归60/analysis.py`
- `人口学120/analysis_hierarchical_regression.py`
