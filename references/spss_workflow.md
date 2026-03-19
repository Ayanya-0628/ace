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

   - **结尾必须**附上自动导出到同目录 Excel 或 Word 的命令：

     ```spss

     OUTPUT EXPORT

       /CONTENTS  EXPORT=ALL  LAYERS=PRINTSETTING  MODELVIEWS=PRINTSETTING

       /XLSX DOCUMENTFILE='C:\\绝对路径\\导出的结果表.xlsx'

       OPERATION=CREATEFILE.

     ```

2. **交付语法进行验证**：将这段 `.sps` 脚本内容发送给客户或项目负责人（即现在的你），让他们手动在电脑上双击打开本机的 SPSS 界面。

3. **人工"一键点击"**：在 SPSS 中新建或打开语法文件，贴入代码，点击“运行” -> “全部”，即可完美生成无任何误差的原版结果报表。

---

---