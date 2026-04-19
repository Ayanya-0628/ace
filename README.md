# 🃏 Ace — 数据分析王牌 Skill

> Antigravity / Gemini CLI / Codex 数据分析 Skill，一站式覆盖统计分析、问卷分析、论文格式、学术绘图。

## 新增能力

- 轻量三省六部多 Agent 编排
- 数据分析双产物默认优先尝试多 Agent
- 适用于脚本 + 报告、表格 + 报告、分析 + 核查并行交付
- 内置 `_ace_templates` 模板引擎，可直接复用报告模板、格式预设与标准文字块

## 安装

```bash
# 方式一：Antigravity / Gemini CLI
git clone https://github.com/Ayanya-0628/ace.git ~/.antigravity/skills/ace

# 方式二：Codex
git clone https://github.com/Ayanya-0628/ace.git ~/.codex/skills/ace

# 方式三：手动复制整个技能目录（推荐在不能使用 git 时）
cp -r ace ~/.antigravity/skills/ace
# 或
cp -r ace ~/.codex/skills/ace

# 注意：不要只复制 SKILL.md。
# 当前技能依赖 scripts/、references/、code_library/、_ace_templates/ 等配套目录。
```

## 功能模块

| 模块 | 内容 |
|------|------|
| 📊 统计分析 | ANOVA、回归分析、前后测、LSD多重比较+字母标记 |
| 📋 问卷分析 | Cronbach's α 信度、交叉分析、卡方检验、SERVQUAL |
| 🧾 SPSS 原生输出 | `.sps/.sav/.spv` 交付链、OMS 导出模板、SPSS 27 兼容排障 |
| 📝 论文格式 | 三线表 Word 输出、宋体/黑体/TNR 字体规范、python-docx 代码模板 |
| 📈 学术绘图 | Okabe-Ito 色盲友好配色、200dpi 规范、中文字体配置 |
| 🤖 多 Agent | 轻量三省六部编排、审查/验证 sidecar、双产物默认并行 |
| 🧩 模板引擎 | `_ace_templates` 报告模板、格式预设、标准分析文字块 |

## 常用入口

- SPSS 原生输出工作流：`references/spss_workflow.md`
- SPV 导出模板：`scripts/spss_spv_export_template.py`
- 兼容性验证过的 SPV 生成器：`scripts/spss_spv_generator.py`

## 触发关键词

说出以下关键词自动触发：

`数据分析` `方差分析` `ANOVA` `回归分析` `问卷分析` `信度检验` `交叉分析` `三线表` `论文格式` `学术绘图` `matplotlib` `SPSS` `Likert` `SERVQUAL`

## 依赖

```
pandas, numpy, scipy, statsmodels, openpyxl,
python-docx, matplotlib, savReaderWriter (可选)
```

## License

MIT
