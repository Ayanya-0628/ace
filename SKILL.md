

---

## 二十、修改追踪系统（v4.0 新增）

> **核心问题**：客户反复修改时，AI 经常漏改下游步骤，或为了安全全量重跑浪费算力。
>
> **解决方案**：三件套——CHANGELOG.md + impact_map.json + diff_steps.py

### 20.1 CHANGELOG.md（项目级修改日志）

> 模板见 `scripts/changelog_template.md`

**使用规则**：
1. 新项目初始化时自动生成（`new_project.py` 已集成）
2. 每次客户修改时，AI 必须在执行修改前先追加 CHANGELOG 条目
3. 条目内容：客户要求 + 修改类型 + 影响范围表 + 重跑命令 + 执行结果检查

**修改类型分类**（铁律，必须先判断再动手）：

| 类型 | 标记 | 影响范围 | 操作 |
|------|------|---------|------|
| 数据/逻辑修改 | RED | step00变则全部重跑 | `diff_steps.py --changed step00` |
| 分析参数修改 | YELLOW | 只影响本步骤 | `diff_steps.py --steps NN` |
| 格式/文字修改 | GREEN | 只影响本步骤 | `diff_steps.py --steps NN` |
| 新增分析 | BLUE | 不影响已有 | 新建 stepN+1 + 合并 |

### 20.2 impact_map.json（步骤依赖图）

> 代码见 `code_library/impact_analyzer.py`

**结构示例**：
```json
{
  "version": "1.0",
  "data_source": "交付成果/cleaned_data.xlsx",
  "steps": {
    "step00": {
      "script": "step00_clean.py",
      "type": "clean",
      "downstream": ["step01", "step02", "step03"]
    },
    "step03": {
      "script": "step03_descriptive.py",
      "type": "analysis",
      "depends_on": ["step00"],
      "variables_used": ["维度1", "维度2"],
      "downstream": []
    }
  }
}
```

**维护规则**：
- 新项目初始化时自动生成骨架
- AI 在完成每个 step 脚本后更新 `variables_used` 字段
- 新增/删除步骤时同步更新 `downstream` 关系

### 20.3 diff_steps.py（智能重跑工具）

> 代码见 `scripts/diff_steps.py`

```bash
# 只重跑指定步骤（最常用）
python diff_steps.py --steps 04 06

# 自动分析影响范围并重跑
python diff_steps.py --changed step00

# 只重跑过期步骤（数据变了但没重跑的）
python diff_steps.py --stale

# 全部重跑（安全兜底）
python diff_steps.py --all

# 查看项目步骤状态
python diff_steps.py --list
```

**自动执行流程**：
1. 备份将被重跑步骤的旧输出（带时间戳）
2. 按依赖顺序执行受影响的步骤
3. 保存运行元数据（data hash + 时间戳）
4. 自动运行 merge_all.py 合并
5. 追加 CHANGELOG.md

### 20.4 修改型任务完整工作流（升级版 S16.10）

> 替代旧的 S16.10 工作流 I，增加了结构化追踪步骤

```
Step 1  读取客户反馈
        |- 逐条列出修改清单
        |- 记录到 Obsidian 需求文件（铁律J）
        |- [NEW] 读取 impact_map.json 理解依赖关系

Step 2  判断修改类型（[NEW] 必须明确分类）
        |- RED 数据/逻辑 -> 影响全部下游
        |- YELLOW 分析参数 -> 只影响本步骤
        |- GREEN 格式文字 -> 只影响本步骤
        |- BLUE 新增分析 -> 不影响已有

Step 3  [NEW] 追加 CHANGELOG.md 条目
        |- 写入客户要求 + 修改类型 + 影响范围表
        |- 列出重跑命令

Step 4  修改分析脚本
        |- 定位需要修改的 stepN.py
        |- 修改代码

Step 5  [NEW] 用 diff_steps.py 智能重跑
        |- python diff_steps.py --steps NN
        |- 自动备份旧输出 + 重跑 + 合并
        |- 自动保存运行元数据

Step 6  验证
        |- 新旧版本对比
        |- 数据一致性检查
        |- 更新 CHANGELOG 执行结果检查项

Step 7  交付
        |- 新报告带日期后缀
        |- 更新 progress.md
        |- 记录到 Obsidian
```

### 20.5 铁律速查

| # | 铁律 | 一句话 |
|---|------|-------|
| 1 | **先分类再动手** | 接到修改要求后，先判断修改类型（RED/YELLOW/GREEN/BLUE），再决定重跑范围 |
| 2 | **改前写 CHANGELOG** | 修改代码前先追加 CHANGELOG 条目，写明影响范围 |
| 3 | **用 diff_steps 不要手动** | 禁止手动逐个运行脚本，用 `diff_steps.py --steps` 自动备份+重跑+合并 |
| 4 | **不确定就全跑** | 分不清影响范围时，`diff_steps.py --all` 最安全 |
| 5 | **最小输出原则** | 修复/修改时，仅重新生成客户需求涉及的内容，不要全量重跑所有步骤。除非客户明确要求或修改类型为 RED（数据/逻辑变更） |



### 20.6 版本管理与文件夹结构

> 代码见 `scripts/version_manager.py`

**项目目录结构（v4.0）**：
```
项目名/
+-- 原始数据/              <-- 客户原始数据（只读，绝不修改）
+-- 需求整理/              <-- 客户需求文档、截图、聊天记录
+-- 交付成果/              <-- 当前工作区（step脚本输出到这里）
+-- v1/                    <-- 第一版快照（初版交付时创建）
+-- v2/                    <-- 第二版快照（客户修改后创建）
+-- v3/                    <-- ...
+-- step00_clean.py
+-- step01_xxx.py
+-- merge_all.py
+-- CHANGELOG.md
+-- impact_map.json
```

**版本快照命令**：
```bash
# 初版完成 -> 创建 v1/
python version_manager.py snapshot --tag "初版交付"

# 客户修改后重跑 -> 创建 v2/
python version_manager.py snapshot --tag "修改：去掉年龄变量"

# 列出所有版本
python version_manager.py list

# 对比两个版本差异
python version_manager.py diff v1 v2

# 从旧版本恢复（回退）
python version_manager.py restore v1
```

**工作流（版本管理融入修改流程）**：
1. 初版完成 -> `python version_manager.py snapshot --tag "初版交付"` -> v1/
2. 客户提修改 -> 写 CHANGELOG -> 改脚本 -> `diff_steps.py` 重跑
3. 修改完成 -> `python version_manager.py snapshot --tag "修改摘要"` -> v2/
4. 交付给客户的是最新 vN/ 文件夹里的内容
5. 交付成果/ 始终是"当前工作区"，step脚本无需修改

**铁律**：
- 每次交付前必须 snapshot，确保有完整存档
- 版本号自动递增，不需要手动管理
- v1/v2/... 文件夹只读，不要直接修改里面的文件
