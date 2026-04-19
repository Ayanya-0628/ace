# SPSS 原生输出专项工作流（按需加载）

> 本文件从 SKILL.md 拆出。仅在客户要求 SPSS 格式输出时加载。

---

## 十一、SPSS 原生输出专项工作流 (针对挑剔客户)

### 11.1 环境限制与结论

由于该机器上的 SPSS 27 底层 Java 组件 Bug，**无法使用 `stats.exe -production silent` 或任何无头模式 (Headless / Silent) 自动静默导出表单**（运行时会抛出 `NullPointerException` 或卡死）。因此，**禁止尝试在后台悄悄调 SPSS**。

### 11.2 标准化替代方案（脑力代码化，体力手动化）

当客户明确要求提交 SPSS 原始分析过程和结果表时，必须遵循以下“代码生成+手动执行”工作流：

1. **Python 生成语法**：读取客户数据后，使用 Python 按照要求生成完整的 SPSS Syntax 语法脚本（`.sps`）。

   - 代码中需包含 `GET DATA` 来读取客户的数据文件。

   - 包含各种分析命令（如 `FREQUENCIES`, `DESCRIPTIVES`, `GLM` 等）。

   - **编码与保存铁律**：
     - `.sps` 统一使用 `utf-8-sig`（带 BOM 的 UTF-8）写出。
     - 统一使用 Windows `CRLF` 换行。
     - 禁止使用无 BOM 的 `utf-8`；本机 `SPSS 27` 打开这类文件时，中文变量名、中文路径和中文注释容易乱码。

   - **打开方式铁律**：
     - Python 重生成 `.sps` 后，若 `SPSS` 里已经打开过旧标签页，必须先关闭旧标签页，再从磁盘重新打开。
     - `SPSS` 已打开标签页不会自动刷新磁盘内容，继续运行旧标签页会误以为“代码没改”。

   - **语法写法铁律**：
     - 单条重分类优先使用单行 `IF (...) 变量 = 值.`，少用 `DO IF ... END IF`。
     - 本机 `SPSS 27` 在中文变量名与字符串函数并用时，`DO IF ... END IF` 更容易触发 `4070 / END IF` 一类控制结构报错。

   - **回归前核查铁律**：
     - 回归自变量必须按当前 `.sav` 的真实变量名生成，不得沿用旧版脚本里的历史命名。
     - 进入回归前应先排除零方差哑变量和 `.sav` 中不存在的变量；否则容易出现“前面分析正常，回归块无结果”。

   - **导出区铁律**：
     - 导出区只保留真正执行的 `OUTPUT EXPORT` 和 `OUTPUT SAVE`。
     - 禁止在导出区堆放大段说明文字或标题节点，避免这些文本一并进入 `Viewer` 干扰阅读。

   - **结尾必须**附上自动导出到同目录 Excel 或 Word 的命令：

     ```spss

     OUTPUT EXPORT

       /CONTENTS  EXPORT=ALL  LAYERS=PRINTSETTING  MODELVIEWS=PRINTSETTING

       /XLSX DOCUMENTFILE='C:\\绝对路径\\导出的结果表.xlsx'

       OPERATION=CREATEFILE.

     ```

2. **交付语法进行验证**：将这段 `.sps` 脚本内容发送给客户或项目负责人（即现在的你），让他们手动在电脑上双击打开本机的 SPSS 界面。

3. **人工"一键点击"**：在 SPSS 中新建或打开语法文件，贴入代码，点击“运行” -> “全部”，即可完美生成无任何误差的原版结果报表。

### 11.3 本机已验证的排障经验

- 若 `Viewer` 中出现整段语法回显而没有统计表，先区分是“语法回显”还是“结果未生成”；语法回显本身不等于分析失败。
- 若回归块前面的描述统计、差异分析都能出表，而回归块不出表，优先检查：
  - 当前 `.sps` 是否是磁盘上的最新版本
  - 回归 `/METHOD=ENTER` 中的变量名是否与 `.sav` 字段一一对应
  - 是否存在零方差分组变量
- 若只是 `TITLE` 超过 60 个字符触发 `2003` 警告，可缩短标题；该警告不影响统计结果。

### 11.4 代码模板位置

- 通用 SPV 导出模板：`scripts/spss_spv_export_template.py`
  - 适用：项目内已有 `.sav` 和一组待执行的 `syntax_blocks`，需要通过 SPSS Python 接口批量导出 `.spv`
  - 默认策略：优先 `OMS -> SPV`，仅在需要兼容旧 GUI 风格输出时再尝试 `SpssClient + OUTPUT SAVE`
- 已落地的生成器示例：`scripts/spss_spv_generator.py`
  - 适用：Logistic/ROC 等成套分析直接拼装并导出

### 11.5 当前默认建议

- `客户只要 .sps + 自己手动运行`：优先生成带 `OUTPUT SAVE` 的标准 `.sps`
- `客户明确要直接给 .spv`：优先使用 `scripts/spss_spv_export_template.py` 或 `scripts/spss_spv_generator.py`，并默认走 `OMS` 路线
- `同一项目同时要 .sav + .sps + .spv`：先生成 `.sav` 与 `.sps`，再用模板脚本读取 `.sav` 和 `syntax_blocks` 产出 `.spv`

---

---
