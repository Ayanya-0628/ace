# -*- coding: utf-8 -*-
"""
用途：生成 SPSS PROCESS 宏分析语法文件的标准模板
位置：ace/code_library/generate_spss_syntax_template.py
日期：2026-03-25

══════════════════════════════════════════════════════════════
  SPSS 语法文件 (.sps) 生成铁律（实测验证版）
══════════════════════════════════════════════════════════════

1. 【编码铁律】
   - 普通 SPSS 语法：用 encoding='gbk' 写入（中文版 SPSS 默认 GBK）
   - 涉及 PROCESS 宏（需要内嵌 process.sps）：用 encoding='utf-8-sig'
     （因为 process.sps 本身是 UTF-8 BOM，必须统一编码）
   - 绝对禁止用 write_to_file 等默认 UTF-8 无 BOM 的工具直接写 .sps

2. 【PROCESS 宏加载铁律】
   - INCLUDE/INSERT 加载 process.sps 会**静默失败**（原因不明）
   - 唯一可靠方案：将 process.sps 全文内嵌到语法文件开头
   - process.sps 末尾的 `process activate=1.` 是必需的激活调用，不能删

3. 【变量名铁律】
   - PROCESS 使用 MATRIX 引擎，变量名必须 <= 8 字符
   - 超长变量名需在 SAV 文件中预先缩短

4. 【路径铁律】
   - SAV 文件路径必须使用绝对路径（SPSS 工作目录不可控）
   - SPSS 路径用单反斜杠即可，不需要双反斜杠

5. 【PROCESS 参数格式】
   - v3/v4/v5 均支持 vars= 参数（可省略）
   - 参数用 / 分隔：PROCESS y=Y/x=X/m=M1 M2/model=6/boot=5000.
   - 多个中介变量用空格分隔写在 /m= 后面
"""

import os
import pyreadstat


def ensure_short_varnames(sav_path, rename_map=None, max_len=8):
    """
    检查并缩短 SAV 文件中超过 max_len 字符的变量名。
    
    Parameters
    ----------
    sav_path : str
        SAV 文件路径
    rename_map : dict, optional
        手动指定的重命名映射 {旧名: 新名}
    max_len : int
        最大变量名长度（PROCESS MATRIX 要求 <= 8）
    
    Returns
    -------
    dict : 实际使用的重命名映射
    """
    df, meta = pyreadstat.read_sav(sav_path)
    
    long_vars = [c for c in df.columns if len(c) > max_len]
    if not long_vars and not rename_map:
        print("[OK] 所有变量名均 <= 8 字符")
        return {}
    
    if rename_map is None:
        # 自动缩短：取前 max_len 个字符，冲突时加数字后缀
        rename_map = {}
        used = set(c for c in df.columns if len(c) <= max_len)
        for c in long_vars:
            short = c[:max_len]
            while short in used:
                short = short[:max_len-1] + str(len(used) % 10)
            rename_map[c] = short
            used.add(short)
    
    df = df.rename(columns=rename_map)
    
    # 更新标签
    old_labels = dict(zip(meta.column_names, meta.column_labels))
    new_labels = {}
    for c in df.columns:
        old_name = next((k for k, v in rename_map.items() if v == c), c)
        if old_name in old_labels:
            new_labels[c] = old_labels[old_name]
    
    pyreadstat.write_sav(df, sav_path, column_labels=new_labels)
    
    print(f"[OK] 变量名已缩短并保存: {sav_path}")
    for old, new in rename_map.items():
        print(f"  {old} -> {new}")
    
    return rename_map


def generate_process_sps(sav_abs_path, sps_out_path, process_call,
                         process_sps_path=None):
    """
    生成包含内嵌 PROCESS 宏定义的 SPSS 语法文件。
    
    Parameters
    ----------
    sav_abs_path : str
        SAV 数据文件的绝对路径
    sps_out_path : str
        输出的 .sps 文件路径
    process_call : str
        PROCESS 宏调用语句，如：
        "PROCESS y=SDS_Std/x=GSRStot/m=GUTstot PSQItot/model=6/boot=5000."
    process_sps_path : str, optional
        process.sps 文件路径，默认自动查找
    
    Notes
    -----
    - 使用 UTF-8 BOM 编码（与 process.sps 一致）
    - 内嵌 process.sps 全文，不使用 INSERT/INCLUDE
    """
    # 自动查找 process.sps
    if process_sps_path is None:
        candidates = [
            r"C:\Program Files\IBM\SPSS\Statistics\27\PROCESS v5.0  for SPSS\process.sps",
            r"C:\Program Files\IBM\SPSS\Statistics\28\PROCESS v5.0  for SPSS\process.sps",
            r"C:\Program Files\IBM\SPSS\Statistics\27\process.sps",
        ]
        for p in candidates:
            if os.path.exists(p):
                process_sps_path = p
                break
        if process_sps_path is None:
            raise FileNotFoundError("找不到 process.sps，请手动指定路径")
    
    # 读取 process.sps 全文
    with open(process_sps_path, 'r', encoding='utf-8-sig') as f:
        process_code = f.read()
    
    # 自动生成 SPV 输出路径（与 .sps 同目录同名）
    spv_out_path = os.path.splitext(sps_out_path)[0] + '.spv'
    
    # 拼接分析语法
    analysis_syntax = f"""

GET FILE='{sav_abs_path}'.
DATASET NAME DataSet1 WINDOW=FRONT.

{process_call}

* ---- Auto export SPV ----.
OUTPUT SAVE OUTFILE='{spv_out_path}'.
"""
    
    full_syntax = process_code + analysis_syntax
    
    os.makedirs(os.path.dirname(sps_out_path) or '.', exist_ok=True)
    with open(sps_out_path, 'w', encoding='utf-8-sig') as f:
        f.write(full_syntax)
    
    print(f"[OK] 已生成 PROCESS 语法文件: {sps_out_path}")
    print(f"[OK] SPV 将自动导出到: {spv_out_path}")
    print(f"[OK] 编码: UTF-8 BOM | 大小: {os.path.getsize(sps_out_path)//1024} KB")


def generate_plain_sps(sav_abs_path, sps_out_path, syntax_content):
    """
    生成普通 SPSS 语法文件（不含 PROCESS 宏）。
    使用 GBK 编码，适用于描述统计、t检验、方差分析、回归等。
    """
    full = f"GET FILE='{sav_abs_path}'.\nDATASET NAME DataSet1 WINDOW=FRONT.\n\n{syntax_content}"
    
    os.makedirs(os.path.dirname(sps_out_path) or '.', exist_ok=True)
    with open(sps_out_path, 'w', encoding='gbk') as f:
        f.write(full)
    
    print(f"[OK] GBK 编码写入: {sps_out_path}")


# ══════════════════════════════════════════════════════════════
# 使用示例
# ══════════════════════════════════════════════════════════════
if __name__ == '__main__':
    # 示例: Model 6 链式中介
    sav = r'C:\path\to\data.sav'
    sps = r'C:\path\to\output.sps'
    
    # 1. 缩短变量名
    # ensure_short_varnames(sav, {'GSRS_Total': 'GSRStot', 'PSQI_Total': 'PSQItot'})
    
    # 2. 生成 PROCESS 语法
    # generate_process_sps(
    #     sav_abs_path=sav,
    #     sps_out_path=sps,
    #     process_call="PROCESS y=SDS_Std/x=GSRStot/m=GUTstot PSQItot/model=6/total=1/stand=1/boot=5000/conf=95/seed=12345."
    # )
    print("示例代码 - 请取消注释后使用")
