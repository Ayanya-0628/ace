# -*- coding: utf-8 -*-
"""
用途：问卷分析全套 SPSS .sps 语法文件生成模板
位置：ace/code_library/spss_questionnaire_sps.py
日期：2026-03-26

══════════════════════════════════════════════════════════════
  问卷分析 .sps 生成铁律
══════════════════════════════════════════════════════════════

【路径铁律 — 最重要！】
  - 禁止用 os.path.abspath() 推断 SAV 路径
    （原因：abspath 依赖脚本执行时的 cwd，换目录执行就会解析错误）
  - 必须以 __file__ 为锚点构造路径，保证无论从哪里运行都正确
  - 模板: SAV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '交付成果', 'xxx.sav')

【编码铁律】
  - 统一使用 encoding='utf-8-sig'（带 BOM 的 UTF-8）
  - 🔴 禁止使用 encoding='utf-8'（SPSS 27 在无 BOM 时按 GBK 读取，中文必乱码）
  - 🔴 禁止使用 encoding='gbk'（变量名含英文特殊字符时可能出错，且不通用）

【语法结构铁律】
  - 第一行: GET FILE='绝对路径.sav'.
  - 第二行: DATASET NAME ds1 WINDOW=FRONT.
  - 中间: 各分析模块（RELIABILITY / FACTOR / DESCRIPTIVES / CORRELATIONS / T-TEST / ONEWAY / REGRESSION）
  - 最后: OUTPUT SAVE OUTFILE='绝对路径.spv'.

用法：
    from spss_questionnaire_sps import generate_questionnaire_sps

    config = QuestionnaireConfig(
        project_id='157',
        project_name='家长式领导',
        sav_path=os.path.join(BASE_DIR, '交付成果', '157_数据_家长式领导.sav'),
        spv_path=os.path.join(BASE_DIR, '交付成果', '157_SPV_家长式领导.spv'),
        sps_path=os.path.join(BASE_DIR, '交付成果', '157_SPS_家长式领导.sps'),
        # 量表定义
        scales=[
            ScaleBlock('家长式领导', {
                '德行领导': ['德行1', '德行2', '德行3', '德行4', '德行5'],
                '仁慈领导': ['仁慈1', '仁慈2', '仁慈3', '仁慈4', '仁慈5'],
                '威权领导': ['威权1', '威权2', '威权3', '威权4', '威权5'],
            }, n_factors=3),
            ScaleBlock('工作幸福感', {
                '工作幸福感': ['幸福1', '幸福2', '幸福3', '幸福4', '幸福5', '幸福6'],
            }, n_factors=1),
        ],
        # 维度均分变量名（用于差异/回归分析）
        dim_vars=['德行领导', '仁慈领导', '威权领导', '工作幸福感', '心理授权'],
        # 人口学变量
        demo_groups={
            '性别': {'type': 'ttest', 'codes': (1, 2)},
            '受教育程度': {'type': 'anova'},
            '年龄': {'type': 'anova'},
            '工作年限': {'type': 'anova'},
            '企业类型': {'type': 'anova'},
            '职位层级': {'type': 'anova'},
        },
        # 回归分析
        regressions=[
            {'title': '家长式领导 → 工作幸福感', 'dv': '工作幸福感', 'ivs': ['德行领导', '仁慈领导', '威权领导']},
            {'title': '家长式领导 → 心理授权', 'dv': '心理授权', 'ivs': ['德行领导', '仁慈领导', '威权领导']},
        ],
    )
    generate_questionnaire_sps(config)
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class ScaleBlock:
    """一个量表/量表组的定义"""
    name: str                          # 量表名称（如"家长式领导"）
    dimensions: Dict[str, List[str]]   # {维度名: [题项变量名列表]}
    n_factors: int = 1                 # 因子分析提取的因子数


@dataclass
class RegressionSpec:
    """回归分析规范"""
    title: str
    dv: str              # 因变量
    ivs: List[str]       # 自变量列表


@dataclass
class QuestionnaireConfig:
    """问卷分析SPS配置"""
    project_id: str
    project_name: str
    sav_path: str         # SAV 文件绝对路径
    spv_path: str         # SPV 输出绝对路径
    sps_path: str         # SPS 输出绝对路径
    scales: List[ScaleBlock] = field(default_factory=list)
    dim_vars: List[str] = field(default_factory=list)        # 差异/回归用的维度均分变量
    demo_groups: Dict[str, dict] = field(default_factory=dict)  # 人口学分组变量
    regressions: List[dict] = field(default_factory=list)    # 回归分析列表
    corr_vars: Optional[List[str]] = None                    # 相关分析变量（默认=dim_vars）
    encoding: str = 'utf-8-sig'                              # 输出编码（必须带BOM）


def _to_spss_path(path: str) -> str:
    """将路径转为 SPSS 格式（正斜杠）。
    🔴 铁律：必须使用已确定的绝对路径，禁止 os.path.abspath()
    """
    return os.path.normpath(path).replace('\\', '/')


def generate_questionnaire_sps(cfg: QuestionnaireConfig) -> str:
    """
    根据配置生成问卷分析全套 SPSS .sps 语法。

    包含模块：
    1. 信度分析（RELIABILITY）
    2. 效度分析（FACTOR）
    3. 描述性统计（DESCRIPTIVES）
    4. 相关分析（CORRELATIONS）
    5. 差异分析（T-TEST / ONEWAY）
    6. 回归分析（REGRESSION）
    7. 输出保存（OUTPUT SAVE）

    Returns: 生成的 .sps 文件路径
    """
    sav = _to_spss_path(cfg.sav_path)
    spv = _to_spss_path(cfg.spv_path)

    sections = []
    sec_num = 0

    # ── 文件头 ──
    sections.append(f"""* ═══════════════════════════════════════════════════════════.
* {cfg.project_name} — SPSS 分析语法.
* 项目编号：{cfg.project_id}.
* 自动生成，可一键运行.
* ═══════════════════════════════════════════════════════════.

GET FILE='{sav}'.
DATASET NAME ds1 WINDOW=FRONT.""")

    # ── 1. 信度分析 ──
    sec_num += 1
    reliability_lines = [f"\n* ══════ {sec_num}. 信度分析 ══════."]
    sub = 0
    for scale in cfg.scales:
        # 量表总体信度
        all_items = []
        for dim_items in scale.dimensions.values():
            all_items.extend(dim_items)
        if len(scale.dimensions) > 1:
            sub += 1
            reliability_lines.append(f"""
TITLE '{sec_num}.{sub} {scale.name}量表总体信度'.
RELIABILITY
  /VARIABLES={' '.join(all_items)}
  /SCALE('{scale.name}') ALL
  /MODEL=ALPHA.""")
        # 各维度信度
        for dim_name, items in scale.dimensions.items():
            sub += 1
            reliability_lines.append(f"""
TITLE '{sec_num}.{sub} {dim_name}维度信度'.
RELIABILITY
  /VARIABLES={' '.join(items)}
  /SCALE('{dim_name}') ALL
  /MODEL=ALPHA.""")
    sections.append('\n'.join(reliability_lines))

    # ── 2. 效度分析 ──
    sec_num += 1
    validity_lines = [f"\n* ══════ {sec_num}. 效度分析（KMO + 因子分析）══════."]
    sub = 0
    for scale in cfg.scales:
        all_items = []
        for dim_items in scale.dimensions.values():
            all_items.extend(dim_items)
        sub += 1
        validity_lines.append(f"""
TITLE '{sec_num}.{sub} {scale.name}量表因子分析'.
FACTOR
  /VARIABLES {' '.join(all_items)}
  /MISSING LISTWISE
  /PRINT KMO EXTRACTION ROTATION
  /CRITERIA FACTORS({scale.n_factors}) ITERATE(25)
  /EXTRACTION PC
  /ROTATION VARIMAX.""")
    sections.append('\n'.join(validity_lines))

    # ── 3. 描述性统计 ──
    if cfg.dim_vars:
        sec_num += 1
        dim_str = ' '.join(cfg.dim_vars)
        sections.append(f"""
* ══════ {sec_num}. 描述性统计 ══════.

TITLE '{sec_num}.1 各维度描述性统计'.
DESCRIPTIVES VARIABLES={dim_str}
  /STATISTICS=MEAN STDDEV MIN MAX.""")

    # ── 4. 相关分析 ──
    corr_vars = cfg.corr_vars or cfg.dim_vars
    if corr_vars:
        sec_num += 1
        corr_str = ' '.join(corr_vars)
        sections.append(f"""
* ══════ {sec_num}. 相关分析 ══════.

TITLE '{sec_num}.1 Pearson相关分析'.
CORRELATIONS
  /VARIABLES={corr_str}
  /PRINT=TWOTAIL NOSIG
  /MISSING=PAIRWISE.""")

    # ── 5. 差异分析 ──
    if cfg.demo_groups and cfg.dim_vars:
        sec_num += 1
        diff_lines = [f"\n* ══════ {sec_num}. 差异分析 ══════."]
        sub = 0
        dep_str = ' '.join(cfg.dim_vars)
        for var_name, spec in cfg.demo_groups.items():
            sub += 1
            if spec.get('type') == 'ttest':
                codes = spec.get('codes', (1, 2))
                diff_lines.append(f"""
TITLE '{sec_num}.{sub} {var_name}差异（t检验）'.
T-TEST GROUPS={var_name}({codes[0]} {codes[1]})
  /MISSING=ANALYSIS
  /VARIABLES={dep_str}
  /CRITERIA=CI(.95).""")
            else:  # anova
                diff_lines.append(f"""
TITLE '{sec_num}.{sub} {var_name}差异（ANOVA）'.
ONEWAY {dep_str} BY {var_name}
  /STATISTICS DESCRIPTIVES
  /MISSING ANALYSIS
  /POSTHOC=LSD ALPHA(0.05).""")
        sections.append('\n'.join(diff_lines))

    # ── 6. 回归分析 ──
    if cfg.regressions:
        sec_num += 1
        reg_lines = [f"\n* ══════ {sec_num}. 回归分析 ══════."]
        sub = 0
        for reg in cfg.regressions:
            sub += 1
            title = reg.get('title', f'{" ".join(reg["ivs"])} → {reg["dv"]}')
            reg_lines.append(f"""
TITLE '{sec_num}.{sub} {title}'.
REGRESSION
  /MISSING LISTWISE
  /STATISTICS COEFF OUTS R ANOVA COLLIN
  /DEPENDENT {reg['dv']}
  /METHOD=ENTER {' '.join(reg['ivs'])}
  /RESIDUALS DURBIN.""")
        sections.append('\n'.join(reg_lines))

    # ── 7. 保存输出 ──
    sections.append(f"""
* ══════ 输出保存 ══════.

OUTPUT SAVE OUTFILE='{spv}'.

* ═══════════════════════════════════════════════════════════.
* END OF SYNTAX.
* ═══════════════════════════════════════════════════════════.""")

    # 拼接并写入
    sps_content = '\n'.join(sections)

    os.makedirs(os.path.dirname(cfg.sps_path) or '.', exist_ok=True)
    with open(cfg.sps_path, 'w', encoding=cfg.encoding) as f:
        f.write(sps_content)

    print(f'✅ 已生成: {cfg.sps_path}')
    print(f'   编码: {cfg.encoding} | 大小: {os.path.getsize(cfg.sps_path)} bytes')
    return cfg.sps_path


# ══════════════════════════════════════════════════════════════
# 便捷函数：从 __file__ 安全构建路径
# ══════════════════════════════════════════════════════════════

def safe_paths(script_file: str, project_id: str, project_name: str,
               subdir: str = '交付成果') -> Tuple[str, str, str]:
    """
    以脚本文件所在目录为锚点，安全构建 SAV/SPV/SPS 路径。
    🔴 铁律：禁止用 os.getcwd() 或裸 os.path.abspath()

    Parameters
    ----------
    script_file : str
        调用方传入 __file__
    project_id : str
        项目编号（如 '157'）
    project_name : str
        项目名关键词（如 '家长式领导'）
    subdir : str
        子目录名（默认 '交付成果'）

    Returns
    -------
    (sav_path, spv_path, sps_path) : Tuple[str, str, str]

    Usage
    -----
    SAV, SPV, SPS = safe_paths(__file__, '157', '家长式领导')
    """
    base = os.path.dirname(os.path.abspath(script_file))
    out = os.path.join(base, subdir)
    sav = os.path.join(out, f'{project_id}_数据_{project_name}.sav')
    spv = os.path.join(out, f'{project_id}_SPV_{project_name}.spv')
    sps = os.path.join(out, f'{project_id}_SPS_{project_name}.sps')
    return sav, spv, sps


# ══════════════════════════════════════════════════════════════
# 使用示例
# ══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    # 以本文件所在目录为锚点（这是唯一推荐的路径构建方式）
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    SAV, SPV, SPS = safe_paths(__file__, '157', '家长式领导')

    config = QuestionnaireConfig(
        project_id='157',
        project_name='家长式领导',
        sav_path=SAV,
        spv_path=SPV,
        sps_path=SPS,
        scales=[
            ScaleBlock('家长式领导', {
                '德行领导': [f'德行{i}' for i in range(1, 6)],
                '仁慈领导': [f'仁慈{i}' for i in range(1, 6)],
                '威权领导': [f'威权{i}' for i in range(1, 6)],
            }, n_factors=3),
            ScaleBlock('工作幸福感', {
                '工作幸福感': [f'幸福{i}' for i in range(1, 7)],
            }, n_factors=1),
            ScaleBlock('心理授权', {
                '工作意义': [f'意义{i}' for i in range(1, 4)],
                '自主性': [f'自主{i}' for i in range(1, 4)],
                '自我效能': [f'效能{i}' for i in range(1, 4)],
                '影响力': [f'影响{i}' for i in range(1, 4)],
            }, n_factors=4),
        ],
        dim_vars=['德行领导', '仁慈领导', '威权领导', '工作幸福感', '心理授权'],
        demo_groups={
            '性别': {'type': 'ttest', 'codes': (1, 2)},
            '受教育程度': {'type': 'anova'},
            '年龄': {'type': 'anova'},
        },
        regressions=[
            {'title': '家长式领导 → 工作幸福感', 'dv': '工作幸福感', 'ivs': ['德行领导', '仁慈领导', '威权领导']},
        ],
    )
    generate_questionnaire_sps(config)
