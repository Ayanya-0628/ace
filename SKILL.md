---
name: ace
description: >
  数据分析王牌 Skill。用于统计分析、方差分析、ANOVA、回归分析、问卷分析、
  SERVQUAL、Likert量表、信度检验、卡方检验、描述性统计、交叉分析、
  数据清洗、SPSS格式、三线表、Word报告、论文格式修改、
  图表绘制、matplotlib、学术绘图。
  触发词：分析数据、做方差分析、问卷分析、清洗数据、格式修改、画图、出报告
---

# Ace — 数据分析王牌

> 涵盖统计分析、问卷分析、论文格式、学术绘图四大模块，一站式处理数据分析接单和学习任务。

---

## 一、何时触发本 Skill

- 用户提到：方差分析、ANOVA、回归、前后测、组间比较
- 用户提到：问卷、调研、Likert、SERVQUAL、信度、交叉分析
- 用户提到：论文格式、三线表、页眉页码、宋体、字体修改
- 用户提到：画图、绑图、matplotlib、配色、DID系数图
- 用户提供：Excel/SPSS 数据文件要求分析

---

## 二、统计分析模块

### 2.1 双因素方差分析（ANOVA）

**标准工作流：**
1. 读取 Excel/SPSS 数据 → `pd.read_excel()` / `savReaderWriter`
2. 分配受试者 ID（按组别×时间点展开）
3. 双因素 ANOVA：`statsmodels.formula.api.ols` + `sm.stats.anova_lm(model, typ=2)`
4. LSD 多重比较 → 紧凑字母显示（CLD）
5. 输出 Word 三线表 + 结果分析段落

**核心函数模板：**
```python
from statsmodels.formula.api import ols
import statsmodels.api as sm

model = ols(f'{value_col} ~ C(group) * C(time)', data=df).fit()
anova_table = sm.stats.anova_lm(model, typ=2)
# 提取：组别F/P、时间F/P、交互F/P
```

**字母标记规则：**
- **小写字母** = 同一组别内不同时间点间的 LSD 多重比较（P<0.05）
- **大写字母** = 不同因素水平间的 LSD 多重比较（P<0.05）

**参考脚本：** `已完成已结款/心率相关分析50/anova_spss.py`

### 2.2 回归分析

**工作流：**
1. 变量筛选（相关性矩阵 → VIF 共线性检查）
2. OLS 回归 / 有序 Logit / Bootstrap 中介效应
3. 稳健性检验（替换变量、子样本）
4. 输出回归系数表 + 显著性标记

### 2.3 前后测分析

**工作流：**
1. 配对样本 t 检验 / Wilcoxon 符号秩检验
2. 组间差异：独立样本 t 检验 / Mann-Whitney U
3. 效应量计算（Cohen's d）
4. 重复测量方差分析（如有多个时间点）

---

## 三、问卷分析模块

### 3.1 标准问卷分析流程

1. **数据清洗**：缺失值检测、异常值剔除、反向计分
2. **描述性统计**：频率、百分比、均值±标准差
3. **信度检验**：Cronbach's α（总量表 + 各维度）
4. **效度检验**：KMO + Bartlett 球形检验 → 因子分析
5. **交叉分析**：卡方检验 + 列联表
6. **差异分析**：独立样本 t / 单因素 ANOVA

### 3.2 关键代码模板

```python
import pandas as pd
from scipy import stats

# Cronbach's α
def cronbachs_alpha(df):
    k = df.shape[1]
    item_vars = df.var(axis=0, ddof=1)
    total_var = df.sum(axis=1).var(ddof=1)
    return (k / (k - 1)) * (1 - item_vars.sum() / total_var)

# 卡方检验
contingency = pd.crosstab(df['性别'], df['购买意愿'])
chi2, p, dof, expected = stats.chi2_contingency(contingency)
```

**参考脚本：** `已完成已结款/市场调研报告80/analysis.py`、`已完成已结款/数据清洗加过检验60/analysis.py`

---

## 四、论文格式模块

### 4.1 Word 文档字体规范

| 元素 | 中文字体 | 英文/数字字体 | 字号 |
|------|---------|-------------|------|
| 正文 | 宋体 | Times New Roman | 小四（10.5pt） |
| 标题 | 黑体 | Times New Roman | — |
| 表格 | 宋体 | Times New Roman | 小五（9pt） |
| 注释 | 宋体 | Times New Roman | 8pt |
| 图题 | 宋体 | Times New Roman | 8pt |

- **首行缩进**：2字符（约0.74cm）
- **行距**：1.5倍行距
- **字体颜色**：默认黑色

### 4.2 三线表格式

```
顶粗线 ══════════════════════════
 组别 │ 时间 │ 指标1 │ 指标2
栏目细线 ─────────────────────────
 对照组   T1    均值±标准差 a
          T2    均值±标准差 b
 实验组   T1    均值±标准差 a
          T2    均值±标准差 b
虚线分隔 ┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
 组别       对照组  均值 A
            实验组  均值 B
 时间       T1     均值 A
            T2     均值 B
虚线分隔 ┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
 差异分析   组别(G)  F值**
            时间(T)  F值*
            G×T      F值ns
底粗线 ══════════════════════════
注：小写字母=同组内不同时间 LSD 比较(P<0.05)
    大写字母=不同组别/时间 LSD 比较(P<0.05)
    ** P<0.01, * P<0.05, ns 不显著
```

### 4.3 python-docx 三线表关键代码

```python
from docx.oxml.ns import nsdecls, qn
from docx.oxml import parse_xml

# 清除所有边框
def clear_table_borders(table):
    tblPr = table._tbl.tblPr or table._tbl._add_tblPr()
    borders = parse_xml(
        '<w:tblBorders %s>'
        '<w:top w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        '<w:left w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        '<w:bottom w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        '<w:right w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        '<w:insideH w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        '<w:insideV w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        '</w:tblBorders>' % nsdecls('w'))
    for existing in tblPr.findall(qn('w:tblBorders')):
        tblPr.remove(existing)
    tblPr.append(borders)

# 设置行边框（顶粗线 sz=12，栏目细线 sz=6）
def set_row_border(row, position, sz=12):
    for cell in row.cells:
        tc = cell._tc
        tcPr = tc.tcPr or tc._add_tcPr()
        borders = tcPr.find(qn('w:tcBorders'))
        if borders is None:
            borders = parse_xml('<w:tcBorders %s/>' % nsdecls('w'))
            tcPr.append(borders)
        border_el = parse_xml(
            f'<w:{position} {nsdecls("w")} w:val="single" '
            f'w:sz="{sz}" w:space="0" w:color="000000"/>')
        existing = borders.find(qn(f'w:{position}'))
        if existing is not None:
            borders.remove(existing)
        borders.append(border_el)

# 中文字体设置
def set_cell_font(cell, text, font_cn='宋体', font_en='Times New Roman', size=9):
    cell.text = ''
    p = cell.paragraphs[0]
    run = p.add_run(str(text))
    run.font.name = font_en
    run.font.size = Pt(size)
    rPr = run._element.find(qn('w:rPr')) or parse_xml('<w:rPr %s/>' % nsdecls('w'))
    run._element.insert(0, rPr)
    rFonts = rPr.find(qn('w:rFonts')) or parse_xml('<w:rFonts %s/>' % nsdecls('w'))
    rPr.insert(0, rFonts)
    rFonts.set(qn('w:eastAsia'), font_cn)
```

### 4.4 表注格式

- 中文宋体、英文 Times New Roman、五号
- 两端对齐、首行缩进2字符
- 段前/段后 0 行、单倍行距

---

## 五、学术绘图模块

### 5.1 图形规范

| 参数 | 规范 |
|------|------|
| 分辨率 | ≥200 dpi |
| 宽度 | 5.5 英寸（适应 A4 页面）|
| 中文字体 | SimHei 或 Microsoft YaHei |
| 坐标轴标签 | 中文 + 英文单位 |
| 图题 | 图下方，宋体 8pt |
| 显著差异配色 | P<0.05 红色系，不显著灰色系 |

### 5.2 Matplotlib 中文配置

```python
import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
mpl.rcParams['axes.unicode_minus'] = False
mpl.rcParams['figure.dpi'] = 200
mpl.rcParams['savefig.dpi'] = 200
```

### 5.3 学术配色方案

```python
# Okabe-Ito 色盲友好配色
OKABE_ITO = ['#E69F00', '#56B4E9', '#009E73', '#F0E442',
             '#0072B2', '#D55E00', '#CC79A7', '#000000']

# 红灰显著性配色
SIG_COLORS = {'significant': '#C44E52', 'not_significant': '#8C8C8C'}
```

### 5.4 常用图表模板

- **分组柱状图 + 误差棒**：组间对比
- **折线图 + 标准误**：时间趋势
- **DID 系数图**：双重差分估计
- **堆叠柱状图**：百分比构成
- **热力图**：相关性矩阵

---

## 六、结果分析写作风格

### 要求

- **一整段连贯文字**，不按指标分列
- 首行缩进 2 字符，客观陈述
- 去 AI 味：删"值得注意的是""综合来看"，统一用"降低"不用"下降"

### 段落结构模板

1. "由表X可知" + 宏观概述哪些指标受显著影响
2. 用**百分比**描述组间差异（不逐个列均值±标准差）
3. 过渡词：第一指标直接跟概述，中间用"此外"，最后用"就XX而言"
4. 交互效应：描述差异最大/最小时间点
5. 结尾"这表明..."因果总结

### 示例

> 　　由表1可知，HR、MAP、BIS均受到组别和时间的显著影响。与对照组相比，瑞马组的HR降低了8.3%。此外，两组MAP在阻滞后均出现明显下降，对照组降低了12.1%，瑞马组降低了15.7%。就BIS而言，两组均呈先降后升趋势，但瑞马组在手术开始时的降幅更大。组别与时间的交互效应显著，两组HR在入室后差异最小，在30min差异最大。这表明瑞马唑仑对患者血流动力学指标具有更显著的调控作用。

---

## 七、通用工作规范

### 7.1 PowerShell + Python 编码

```powershell
$env:PYTHONUTF8="1"; & "python.exe" "script.py" 2>&1
```

### 7.2 依赖库

```
pandas, numpy, scipy, statsmodels, openpyxl,
python-docx, matplotlib, savReaderWriter (可选)
```

### 7.3 交付物检查清单

- [ ] Excel 分析附表（原始数据 + 统计结果）
- [ ] Word 报告（三线表 + 结果分析文字）
- [ ] 图表（PNG 200dpi，嵌入 Word）
- [ ] 脚本代码（可复现）
