# 实战踩坑速查表 + 防御性代码模板（按需加载）

> 本文件从 SKILL.md 拆出，包含踩坑速查表（65+条，10个分类）和防御性代码模板（8个模板）。
> 遇到问题时加载排查，新项目时加载复制防御模板。

---

## 十九、实战踩坑速查表（从 17 个项目中提炼）

> 遇到问题先查此表，避免重复踩坑。

### 19.1 SEM / CFA 踩坑

| 坑 | 原因 | 解决方案 |
|----|------|--------|
| factor_analyzer 报 force_all_finite 错误 | 与新版 sklearn 不兼容 | 用 numpy 手动实现 EFA，或降级 sklearn |
| semopy.inspect() 的 lval/rval 含义反直觉 | lval=观测变量, rval=潜变量 | 查看 semopy 文档，或打印 inspect 表逐列确认 |
| SEM 路径全不显著 | 多个 IV 高度共线性（r>0.8） | 改用逐个 OLS 简单回归替代 SEM 路径分析 |
| CR/AVE 计算出错 | 用了非标准化因子载荷 | 必须用 Est.Std 列（标准化载荷）计算 |

### 19.2 中介 / 调节效应踩坑

| 坑 | 原因 | 解决方案 |
|----|------|--------|
| 中介路径莫名不显著 | 使用了聚类标准误（过于保守） | 换 HC1 稳健标准误，这是合法的建模选择 |
| 中介变量 a/b 路径均不显著 | 选错了中介变量 | 逐一回归筛选数据中所有候选变量 |
| PROCESS 简单斜率图与手动计算不一致 | 协变量处理方式不同 | PROCESS 默认中心化 X/W，预测时协变量取 0 |
| 交互项不显著 | 解释变量未中心化，共线性高 | 对 X 和 W 先中心化（去均值）再构建交互项 |
| 倒U型关系检验 | 不知道怎么做 | X + X^2 回归，X^2系数显著为负则倒U，配合U-test检验 |

### 19.3 问卷分析踩坑

| 坑 | 原因 | 解决方案 |
|----|------|--------|
| 差异分析用了 t 检验但数据不正态 | 跳过了正态性检验 | 强制执行 Step 1.5（S16.1），非正态则全面切非参数 |
| 描述统计用均值+SD但数据偏态严重 | 同上 | 非正态则改用中位数(P25-P75) |
| 相关矩阵 Pearson 结果不合理 | 同上 | 非正态则改用 Spearman |
| 信度 alpha 特别低 | 包含了反向计分题但未反转 | 检查原始问卷标注的反向计分题，先反转再算 alpha |
| 参考论文的维度拆分套到了客户数据上 | 混淆了方法参考和数据结构 | 铁律F：客户问卷设计表才是变量定义的唯一依据 |

### 19.4 绘图 / Matplotlib 踩坑

| 坑 | 原因 | 解决方案 |
|----|------|--------|
| rcParams 设了中文字体但不生效 | rcParams 全局设置不可靠 | 用 FontProperties(fname=) 逐元素指定（S7.7） |
| bbox_inches='tight' 导致手动布局失效 | tight 自动裁剪会补偿位移 | 禁用 tight，用 fig.subplots_adjust() 手动控制 |
| 修改 ax.text() y偏移但标签距离不变 | tight 裁剪补偿 | 用 ax.set_ylim(min - pad*step, ...) 控制留白 |
| 图例中全角括号显示异常 | TNR 字体不含全角字符 | 全角括号放在宋体 TextArea 中 |
| 误差棒不对称（中位数+四分位距） | yerr 需要 2xN 数组 | yerr = [[下误差], [上误差]] 格式 |

### 19.5 数据 / 编码踩坑

| 坑 | 原因 | 解决方案 |
|----|------|--------|
| 性别计数全部为 0 | 数据用 0=女 但代码用 ==2 判断 | 先 `print(df['性别'].value_counts())` 确认编码 |
| 样本量不一致 | 不同章节用了不同的子集 | 在脚本顶部明确定义所有子集变量名，注释标注用途 |
| 分组中位数不对 | 合并了不该合并的组计算中位数 | 明确定义分组基准的计算范围 |
| 覆盖了已交付的文件 | 重跑脚本直接输出到同路径 | 先备份再跑（§13），或输出路径加日期后缀 |
| `.sav` 文件变量名乱码 | SPSS 文件编码与 Python 默认编码不匹配 | 用 `pyreadstat.read_sav()` 替代 `savReaderWriter`，或指定 `encoding='utf-8'` |
| Excel 读取时列名有空格/换行 | 客户 Excel 表头格式不规范 | `df.columns = df.columns.str.strip().str.replace('\n','')` |
| `pd.read_excel()` 读错Sheet | 默认读第一个Sheet但数据在第二个 | 显式指定 `sheet_name='数据'` 或 `sheet_name=1` |
| 日期列读成数字 | Excel 日期序列号未自动转换 | `pd.to_datetime(df['日期'], origin='1899-12-30', unit='D')` |
| `merge` 后行数暴增 | 合并键有重复值导致笛卡尔积 | merge 前检查 `df[key].duplicated().sum()` |
| 缺失值统计为0但实际有缺失 | 缺失值是空字符串""而非 NaN | `df.replace('', np.nan, inplace=True)` 先统一转 NaN |

### 19.6 Word 报告踩坑

| 坑 | 原因 | 解决方案 |
|----|------|--------|
| 表格内段落行距太大 | 表格段落继承了正文1.5倍行距样式 | 表格单元格必须单独设：单倍行距+段前段后0+无缩进（§6.2） |
| 字体看起来对但打印出来部分是等线 | 未设置 eastAsia 字体 | 用 `rFonts.set(qn('w:eastAsia'), '宋体')` 显式设置 |
| 表格编号跳号 | 手动硬编码表号 | 用变量 `table_num` 自增 |
| 打开已有 Word 替换单个表格 | 其他表格还是旧数据（违反§18） | 禁止打开已有 Word 局部替换，全量重新生成 |
| `add_run()` 后中文变为等线体 | 只设了 `run.font.name` 没设 eastAsia | 每个 `add_run()` 后都要设 eastAsia 字体（用 `word_utils.set_cell_font`） |
| 表格列宽不受控 | python-docx 设置列宽被 Word 自动调整覆盖 | 设置 `table.autofit = False` + 每个 cell 单独设 width |
| 插入的图片尺寸不对 | `Inches()` vs `Cm()` 混用 | 统一用 `Inches(5.5)` 适应 A4 页面 |
| 生成的 Word 在 WPS 中显示异常 | WPS 对 python-docx 的 XML 兼容性差 | 用 Office Word 打开确认；三线表边框用 `tcBorders` 而非 `tblBorders` |
| 文字分析漏了某个表 | 先生成所有表格再回头补文字 | 铁律I：表+文字必须同步编写，`add_table()` 后立即跟 `add_body_text()` |

### 19.7 PowerShell / 编码 / 路径踩坑 🔴 高频

| 坑 | 原因 | 解决方案 |
|----|------|--------|
| `UnicodeDecodeError: 'charmap' codec` | Windows 默认 GBK 编码 | **每次** `run_command` 加 `$env:PYTHONUTF8="1";` 前缀 |
| PowerShell 中 `&&` 连接命令失败 | PowerShell 用 `;` 不用 `&&` | 多条命令用 `;` 分隔：`cmd1; cmd2; cmd3` |
| 路径中有空格导致脚本找不到 | 未用引号包裹路径 | 路径用双引号包裹：`python "C:\path with space\script.py"` |
| 路径中有中文导致 `FileNotFoundError` | Python 脚本内用了 `open()` 默认编码 | `open(path, encoding='utf-8')` 显式指定编码 |
| `$` 符号在 PowerShell 中被解释为变量 | PowerShell 变量前缀是 `$` | 用单引号包裹含 `$` 的字符串，或用 `` ` `` 转义 |
| 脚本输出中文乱码（stdout） | PowerShell 终端编码不匹配 | 脚本开头加 `import sys; sys.stdout.reconfigure(encoding='utf-8')` |
| `2>&1` 重定向在 PowerShell 不生效 | 语法不同 | 用 `python script.py 2>&1` 放在最后，整条命令不要套引号 |
| `cd` 命令无效 | Antigravity 的 `run_command` 不支持 `cd` | 用 `Cwd` 参数指定工作目录，不用 `cd` |
| 管道符 `\|` 被解释错误 | 跨 shell 时管道行为不一致 | 尽量在 Python 脚本内完成处理，减少 Shell 管道 |
| 脚本路径用了 `/` 但 Windows 需要 `\` | Unix 风格路径在 Windows 部分场景不兼容 | 用 `r'C:\path\to\file'` 原始字符串，或 `os.path.join()` |

### 19.8 run_command 调用踩坑 🔴 高频

| 坑 | 原因 | 解决方案 |
|----|------|--------|
| 长脚本超时中断 | `WaitMsBeforeAsync` 设太小 | 数据分析脚本设 `WaitMsBeforeAsync=10000`（10秒上限） |
| 脚本成功但看不到输出 | 输出被截断 | 用 `command_status` + `OutputCharacterCount=2000` 查看完整输出 |
| 脚本报错但看不到错误信息 | stderr 没有重定向 | 命令末尾加 `2>&1` 将 stderr 合并到 stdout |
| 多行 Python 命令在 PowerShell 中断裂 | 换行处理不当 | 用 `python -c "..."` 时所有代码写在一行，用 `;` 分隔语句 |
| `python` 命令找不到 | 环境变量问题 | 用全路径 `python.exe`，不用 venv |
| 交互式命令卡住 | 某些命令等待用户输入 | 用 `send_command_input` 发送输入，或用 `--yes`/`-y` 参数 |
| `pip install` 安装后 import 失败 | 安装到了不同的 Python 环境 | `python -m pip install xxx` 确保安装到正确环境 |

### 19.9 数据分析逻辑踩坑

| 坑 | 原因 | 解决方案 |
|----|------|--------|
| 改了清洗规则但下游还是旧结果 | 违反§18全盘重算铁律 | 改了第1层必须重跑第2、3层 |
| 换了变量但某些表还用旧变量 | 局部修改 | 全局搜索旧变量名，确认全部替换 |
| 两次运行结果不同 | 有随机种子未固定 | `np.random.seed(42)`/`random_state=42` |
| P值刚好 0.05 不知道算显著还是不显著 | 边界值处理 | 统一用 `p < 0.05` 为显著（不含等于），文字中写"边际显著" |
| 回归 R² 特别高（>0.95）| 自变量和因变量有数学关系（如总分包含子项） | 检查变量间是否有线性代数关系 |
| 中介效应比例>100% | Baron-Kenny 方法在特定条件下会出现 | 改用 Bootstrap 方法，不报比例只报 CI |
| 方差分析 F 值说显著但事后比较没有显著组 | F 检验和事后比较标准不同 | 正常现象，可改用 LSD（更敏感）或报告"整体显著但两两比较差异不大" |
| `df.corr()` 包含了分类变量 | ID/性别等被当成连续变量 | 相关分析前先筛选 `df[continuous_cols].corr()` |

### 19.10 客户沟通/需求理解踩坑

| 坑 | 原因 | 解决方案 |
|----|------|--------|
| 客户说"做回归"但实际需要相关分析 | 客户不懂统计术语 | 先问清楚研究目的+假设，再选方法（§2.4决策树） |
| 客户发的参考论文变量结构≠客户数据 | 混淆了方法参考和数据结构 | 铁律F：客户问卷设计表才是变量定义的唯一依据 |
| 客户说"优化一下数据"含义不明 | 可能是调整基线、调显著、或改格式 | 主动确认：是改数据值、改分析方法、还是改展示格式 |
| 交付后客户说"数不对" | 客户用的是不同版本的数据文件 | 确认数据文件版本，记录文件MD5或行数 |
| 客户中途换了问卷题项分组 | 需求变更 | 铁律J：变更需求实时记录到 Obsidian，全盘重算 |

---

## 二十、防御性代码模板（直接复制粘贴）

> §19 列了坑，本节给出**每个坑对应的可执行修复代码**。新项目直接复制对应模板。

### 20.1 Python 脚本开头必加模板（防编码/随机/路径）

```python
# -*- coding: utf-8 -*-
"""
用途：[描述]
输入文件：[路径]
输出文件：[路径]
日期：YYYY-MM-DD
"""
import sys
import os
import numpy as np
import pandas as pd

# ══════ 防御性设置 ══════
sys.stdout.reconfigure(encoding='utf-8')    # 防 stdout 中文乱码
np.random.seed(42)                          # 固定随机种子

# 路径统一用 os.path.join，防 Windows/Unix 不兼容
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, '原始数据', '数据.xlsx')
OUTPUT_DIR = os.path.join(BASE_DIR, '交付成果')
os.makedirs(OUTPUT_DIR, exist_ok=True)
```

### 20.2 run_command 标准调用模板（防编码/超时/stderr丢失）

```
正确的 run_command 调用格式（每次都必须遵守）：

CommandLine: $env:PYTHONUTF8="1"; python "C:\path\to\script.py" 2>&1
Cwd:         C:\Users\16342\Desktop\BaiduSyncdisk\兼职
WaitMsBeforeAsync: 10000
SafeToAutoRun: false

❌ 错误写法：
python script.py                  → 缺 PYTHONUTF8，中文路径必崩
python script.py && echo done     → PowerShell 不支持 &&，用 ; 替代
cd C:\path; python script.py      → cd 命令无效，用 Cwd 参数替代
```

### 20.3 数据读取防御模板（防编码/Sheet错/列名脏/合并键重复）

```python
# ══════ 数据读取防御 ══════
def safe_read_excel(filepath, sheet_name=0):
    """防御性读取 Excel 文件"""
    df = pd.read_excel(filepath, sheet_name=sheet_name)
    # 1. 清理列名（去空格、换行、全角）
    df.columns = (df.columns
        .str.strip()
        .str.replace('\n', '', regex=False)
        .str.replace('\r', '', regex=False)
        .str.replace('\u3000', '', regex=False))   # 全角空格
    # 2. 空字符串转 NaN
    df = df.replace('', np.nan)
    df = df.replace(r'^\s*$', np.nan, regex=True)
    # 3. 打印基本信息（铁律L）
    print(f'Shape: {df.shape}')
    print(f'Columns: {list(df.columns)}')
    print(f'Missing: {df.isnull().sum().sum()} cells')
    return df

def safe_read_sav(filepath):
    """防御性读取 SPSS .sav 文件"""
    try:
        import pyreadstat
        df, meta = pyreadstat.read_sav(filepath)
    except ImportError:
        import savReaderWriter
        with savReaderWriter.SavReader(filepath, ioUtf8=True) as reader:
            header = reader.header
            records = [row for row in reader]
        df = pd.DataFrame(records, columns=header)
    print(f'Shape: {df.shape}')
    return df
```

### 20.4 编码校验防御模板（防性别计数=0、编码不匹配）

```python
# ══════ 分类变量编码校验（每个分类变量都必须跑一遍） ══════
def verify_encoding(df, col, expected_mapping):
    """校验分类变量编码是否与预期一致
    
    用法：verify_encoding(df, '性别', {1: '男', 2: '女'})
    """
    actual = df[col].value_counts(dropna=False).to_dict()
    print(f'\n[编码校验] {col}:')
    print(f'  实际分布: {actual}')
    print(f'  预期映射: {expected_mapping}')
    
    for code in expected_mapping:
        if code not in actual:
            print(f'  ⚠️ 预期编码 {code}({expected_mapping[code]}) 在数据中不存在！')
    
    unexpected = set(actual.keys()) - set(expected_mapping.keys()) - {np.nan}
    if unexpected:
        print(f'  ⚠️ 数据中存在未预期的编码值: {unexpected}')
    
    return actual

# 示例：开工前强制执行
verify_encoding(df, '性别', {1: '男', 2: '女'})
verify_encoding(df, 'Group', {1: '实验组', 2: '对照组'})
```

### 20.5 子集管理防御模板（防样本量不一致）

```python
# ══════ 子集定义（脚本顶部集中定义，禁止散落在各处） ══════
# 全体样本
df_all = df.copy()
print(f'df_all: n={len(df_all)}')

# 实验组 / 对照组
df_exp = df[df['Group'] == '实验组'].copy()
df_ctrl = df[df['Group'] == '对照组'].copy()
print(f'df_exp: n={len(df_exp)}, df_ctrl: n={len(df_ctrl)}')

# 完整子集（无缺失）
key_vars = ['age', 'BMI', 'VAS_Pre', 'VAS_Post']
df_complete = df.dropna(subset=key_vars).copy()
print(f'df_complete: n={len(df_complete)} (dropped {len(df) - len(df_complete)} rows with missing)')

# ⚠️ 每次使用子集时打印 n，确认与预期一致
# ⚠️ 禁止在函数内部临时创建子集（找不回来）
```

### 20.6 Word 报告防御模板（防字体/行距/东亚字体遗漏）

```python
# ══════ Word 防御性生成（统一用 word_utils） ══════
import sys
sys.path.insert(0, r'C:\Users\16342\.antigravity\skills\ace\code_library')
from word_utils import (create_report_doc, add_three_line_table,
                        add_body_text, add_note, add_heading,
                        add_figure_caption, add_figure)

doc = create_report_doc()  # 已自动设好默认字体

# ✅ 正确：表+文字同步生成
table_num = 0

table_num += 1
add_three_line_table(doc,
    headers=['变量', '均值', 'SD', 'P'],
    data_rows=[['年龄', '65.3', '8.2', '0.832']],
    title=f'表{table_num} 两组基线特征比较')
add_note(doc, '注：P值为独立样本t检验结果。')
add_body_text(doc, f'由表{table_num}可知，两组患者在年龄方面差异无统计学意义（P=0.832>0.05），具有可比性。')

# ❌ 错误：先生成所有表格再回头补文字（违反铁律I）
# ❌ 错误：用 doc = Document('已有文件.docx') 打开旧文件局部替换（违反§18）

doc.save(os.path.join(OUTPUT_DIR, '分析报告.docx'))
```

### 20.7 merge 防御模板（防笛卡尔积/行数暴增）

```python
# ══════ merge 前必检 ══════
def safe_merge(left, right, on, how='inner'):
    """带防御的 merge，防止笛卡尔积"""
    # 检查合并键是否有重复
    left_dup = left[on].duplicated().sum() if isinstance(on, str) else left[on].duplicated().sum()
    right_dup = right[on].duplicated().sum() if isinstance(on, str) else right[on].duplicated().sum()
    if left_dup > 0 or right_dup > 0:
        print(f'⚠️ 合并键有重复！left: {left_dup}, right: {right_dup}')
        print(f'    可能导致行数暴增（笛卡尔积）')
    
    n_before = len(left)
    result = pd.merge(left, right, on=on, how=how)
    n_after = len(result)
    
    if n_after > n_before * 1.1:
        print(f'⚠️ merge 后行数异常增加: {n_before} → {n_after} (+{n_after-n_before})')
    else:
        print(f'merge OK: {n_before} → {n_after}')
    
    return result
```

### 20.8 PowerShell 特殊字符转义速查

```
PowerShell 中以下字符需要特殊处理：

| 字符 | 问题 | 修复方案 |
|------|------|---------|
| $    | 被当成变量 | 用单引号包裹：'$var' 或反引号转义：`$var |
| "    | 字符串边界 | 用反引号转义：`" 或改用单引号包裹 |
| &    | 调用运算符 | 用引号包裹："&" |
| ()   | 子表达式 | 用引号包裹或反引号转义 |
| \n   | 不会被解释为换行 | 在 python -c 中用 ; 分隔语句替代 |

标准模板：
$env:PYTHONUTF8="1"; & "python.exe" "脚本路径.py" 2>&1
```