# 🃏 Ace — 数据分析王牌 Skill

> AI 编程助手数据分析 Skill，一站式覆盖统计分析、问卷分析、机器学习、论文格式、学术绘图。

## 安装

本仓库提供多个分支，适配不同 AI 编程助手平台：

| 平台 | 分支 | 安装命令 |
|------|------|---------|
| **Antigravity** | `antigravity` | `git clone -b antigravity https://github.com/Ayanya-0628/ace.git ~/.antigravity/skills/ace` |
| **Codex CLI** | `codex` | `git clone -b codex https://github.com/Ayanya-0628/ace.git ~/.codex/skills/ace` |
| **通用** | `main` | `git clone https://github.com/Ayanya-0628/ace.git` |

> **Windows 用户**：将 `~` 替换为 `$HOME` 或 `C:\Users\你的用户名`。

## 分支差异

| | `main` | `antigravity` | `codex` |
|---|--------|---------------|---------|
| SKILL.md | 733 行基础版 | 795 行（+scripts 索引） | 1416 行（+ML 模块） |
| scripts/ | ❌ | ✅ 5 个（前置检验/ANOVA/问卷/三线表/绘图） | ✅ 6 个（描述统计/ANOVA/回归/DID/问卷/ML） |
| agents/ | ❌ | ❌ | ✅ openai.yaml |
| 设计思路 | 纯 SKILL.md | 代码模板 + 可执行脚本 | 方法论指南 + 脚本 + agent 调度 |

## 功能模块

| 模块 | 内容 |
|------|------|
| 📊 统计分析 | ANOVA、t检验、回归分析、DID、中介/调节效应、LSD多重比较 |
| 📋 问卷分析 | Cronbach's α、CITC、KMO、EFA、交叉分析、SERVQUAL |
| 🤖 机器学习 | 随机森林、XGBoost、SVM、交叉验证、SHAP（codex 分支） |
| 📝 论文格式 | 三线表 Word 输出、宋体/黑体/TNR 字体规范 |
| 📈 学术绘图 | Okabe-Ito 配色、200dpi、中文字体、DID系数图、ROC曲线 |

## 触发关键词

`数据分析` `方差分析` `ANOVA` `回归分析` `问卷分析` `信度检验` `交叉分析` `三线表` `论文格式` `学术绘图` `matplotlib` `SPSS` `Likert` `SERVQUAL` `随机森林` `机器学习` `建模` `调参`

## 依赖

```
核心：pandas, numpy, scipy, statsmodels, openpyxl, python-docx, matplotlib
可选：factor_analyzer, pingouin, semopy, linearmodels, scikit-learn, xgboost
```

## License

MIT
