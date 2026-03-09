# 🎨 Plotting Utils

常用科研绘图脚本集合，覆盖 R 和 Python 语言。

## 📋 脚本清单

### R 脚本

| 脚本 | 用途 | 依赖 |
|------|------|------|
| [`polar_bar_chart.R`](scripts/R/polar_bar_chart.R) | 极坐标柱状图（环形柱状图） | circlize, readxl, grid, showtext |

### Python 脚本

_暂无，后续添加_

## 🚀 使用方法

1. 找到需要的脚本模板
2. 复制到你的工作目录
3. 修改数据路径、列名、颜色等参数
4. 运行脚本生成图表

## 📝 脚本说明

### polar_bar_chart.R - 极坐标柱状图

**功能**：使用 R 的 `circlize` 包绘制环形柱状图，适用于多品种/多分组的数据可视化。

**特点**：
- 支持多品种（variety）循环绘图
- 每个扇区（sector）对应一个类别（category）
- 柱形颜色按分组（group）区分
- 支持显著性标注
- PDF 导出，3×2 子图排版
- Times New Roman 字体支持

**输入数据格式**（Excel）：
- `category` 列：类别名称
- `variety` / `variety_id` 列：品种名称
- `group` 列：分组名称（用于颜色区分）
- `value` 列：数值
- `significance` 列：显著性标注（如 `*`, `**`, `ns`）

**依赖安装**：
```r
install.packages(bindindindindindc("circlize", "readxl", "showtext"))
```

## 📂 目录结构

```
plotting-utils/
├── SKILL.md           # Antigravity Skill 配置文档
├── README.md          # 本文件
└── scripts/
    ├── R/
    │   └── polar_bar_chart.R
    └── Python/
```

## 🔄 更新日志

- **2026-03-09**: 初始化仓库，添加极坐标柱状图 R 脚本
