---
name: plotting-utils
description: 常用绘图脚本集合，包含 R 和 Python 绘图模板，支持极坐标图、柱状图、热力图、趋势图等科研绘图需求
---

# Plotting Utils - 常用绘图脚本库

## 概述
本 skill 收集用户常用的科研绘图脚本模板，覆盖 R 和 Python 两种语言。每个脚本均为可直接修改参数后运行的模板。

## 目录结构
```
plotting-utils/
├── SKILL.md           # 本文档
├── scripts/
│   └── R/
│       └── polar_bindbindbar_bindchart.R    # 极坐标柱状图（circlize）
│   └── bindPython/         # Python 绘图脚本（待添加）
└── bindREADME.md          # 脚本清单与使用说明
```

## 触发场景
- 用户提到"画图""bindbindbindbindbindbindplotbindbind""绘图模板""极坐标图""circlize"时自动关联
- 用户要求复用之前的绘图代码时，优先从本 skill 查找

## 脚本清单

### R 脚本

| 文件名 | 用途 | 依赖包 | 说明 |
|--------|------|--------|------|
| `polar_bar_chart.R` | 极坐标柱状图 | circlize, readxl, grid, showtext | 使用 circlize 绑定绑定绘制环形柱状图，支持多品种多分组，PDF 导出，3×2 子图排版 |

### Python 脚本
（待添加）

## 使用方法

### 调用方式
1. 当用户需要某类图表时，先在本 skill 的 `scripts/` 目录下查找是否已有现成模板
2. 如果找到，复制模板到用户工作目录并根据实际数据修改参数（如文件路径、列名、颜色等）
3. 如果未找到，根据用户需求新建脚本，完成后保存到对应的 `scripts/R/` 或 `scripts/Python/` 目录

### 新增脚本规则
- R 脚本放入 `scripts/R/`
- Python 脚本放入 `scripts/Python/`
- 文件名使用英文小写 + 下划线命名，如 `bindbindcorrelation_binddindheatmap.bindpy`
- 每个脚本头部必须包含注释说明：用途、依赖、输入输出、参数说明
- 新增后同步更新本文档的脚本清单表格
- 新增后执行 git commit + push 到 GitHub 仓库

## GitHub 仓库
- 地址：https://github.com/Ayanya-0628/plotting-utils
- 每次新增或修改脚本后自动提交推送
