# 工作流 E：DID 双重差分（★★）

**适用场景**：政策效应评估、准自然实验

## 标准步骤

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

Step 6  DID 系数图

Step 7  Word 输出
```

## 参考脚本

- `实证分析绘图60/plot_charts.py`
