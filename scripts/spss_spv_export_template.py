# -*- coding: utf-8 -*-
"""
SPSS SPV 通用导出模板

用途:
    当项目内已经有 .sav 数据文件和一组待执行的 SPSS syntax blocks 时，
    用本模板通过 SPSS 自带 Python 接口批量导出 .spv。

默认策略:
    1. 优先 OMS -> SPV（当前机器兼容性最稳）
    2. OMS 失败时，再回退到 SpssClient + OUTPUT SAVE

使用方式:
    "C:\\Program Files\\IBM\\SPSS\\Statistics\\27\\statisticspython3.bat" spss_spv_export_template.py

    或在项目脚本中 import 本文件的 run_spv_export。
"""

from __future__ import annotations

import json
import os
from pathlib import Path


def _norm(path_str: str) -> str:
    return os.path.abspath(path_str).replace("\\", "/")


def run_with_oms(sav_path: str, syntax_blocks: list[str], spv_output_path: str, sav_output_path: str | None = None) -> bool:
    import spss

    spss.Submit(f"GET FILE='{_norm(sav_path)}'.")
    spss.Submit(
        f"""OMS /SELECT ALL
  /DESTINATION FORMAT=SPV OUTFILE='{_norm(spv_output_path)}'
  /TAG='spv_all'."""
    )
    for block in syntax_blocks:
        spss.Submit(block)
    spss.Submit("OMSEND TAG='spv_all'.")
    if sav_output_path:
        spss.Submit(f"SAVE OUTFILE='{_norm(sav_output_path)}'.")
    print(f"[OMS] SPV 已保存: {_norm(spv_output_path)}")
    if sav_output_path:
        print(f"[OMS] SAV 已保存: {_norm(sav_output_path)}")
    return True


def run_with_spssclient(sav_path: str, syntax_blocks: list[str], spv_output_path: str, sav_output_path: str | None = None) -> bool:
    import SpssClient

    SpssClient.StartClient()
    try:
        SpssClient.RunSyntax(f"GET FILE='{_norm(sav_path)}'.")
        for block in syntax_blocks:
            SpssClient.RunSyntax(block)
        SpssClient.RunSyntax(f"OUTPUT SAVE OUTFILE='{_norm(spv_output_path)}'.")
        if sav_output_path:
            SpssClient.RunSyntax(f"SAVE OUTFILE='{_norm(sav_output_path)}'.")
        print(f"[SpssClient] SPV 已保存: {_norm(spv_output_path)}")
        if sav_output_path:
            print(f"[SpssClient] SAV 已保存: {_norm(sav_output_path)}")
        return True
    finally:
        try:
            SpssClient.StopClient()
        except Exception:
            pass


def run_spv_export(sav_path: str, syntax_blocks: list[str], spv_output_path: str, sav_output_path: str | None = None) -> bool:
    os.makedirs(os.path.dirname(_norm(spv_output_path)), exist_ok=True)

    try:
        return run_with_oms(sav_path, syntax_blocks, spv_output_path, sav_output_path)
    except Exception as exc:
        print(f"[OMS] 失败: {exc}")
        print("[OMS] 回退到 SpssClient 方案...")

    try:
        return run_with_spssclient(sav_path, syntax_blocks, spv_output_path, sav_output_path)
    except Exception as exc:
        print(f"[SpssClient] 也失败了: {exc}")
        return False


def load_json_config(config_path: str) -> dict:
    return json.loads(Path(config_path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    # 按需改成你自己的项目路径
    example = {
        "sav_path": r"C:\path\to\data.sav",
        "spv_output_path": r"C:\path\to\SPSS输出.spv",
        "sav_output_path": None,
        "syntax_blocks": [
            "TITLE '人口学资料频数分布'.\nFREQUENCIES VARIABLES=gender age.",
            "TITLE '描述性统计'.\nDESCRIPTIVES VARIABLES=score_total.",
            "TITLE '多元回归'.\nREGRESSION /DEPENDENT score_total /METHOD=ENTER x1 x2 x3.",
        ],
    }
    print(json.dumps(example, ensure_ascii=False, indent=2))
    print("将上面的结构保存为 json 后，可在项目脚本中读取并传给 run_spv_export。")
