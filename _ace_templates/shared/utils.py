# -*- coding: utf-8 -*-
"""
shared/utils.py — ACE 模板引擎公共工具函数
从 5 个 pipeline 中提取的通用逻辑，避免重复代码。

提供：
  - load_config: 加载 YAML 配置
  - cronbach_alpha: 克朗巴赫 α 信度系数
  - load_and_clean: 统一数据加载 + likert 映射 + 缺失值处理
  - compute_dimension_scores: 反向计分 + 维度均值 + 总量表得分
  - p_str / sig_star: P 值格式化工具
"""
import yaml
import numpy as np
import pandas as pd


# ══════════════════════════════════════════════
#  配置加载
# ══════════════════════════════════════════════
def load_config(path):
    """加载 YAML 配置文件"""
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


# ══════════════════════════════════════════════
#  信度系数
# ══════════════════════════════════════════════
def cronbach_alpha(df_items):
    """计算 Cronbach's α 信度系数

    Args:
        df_items: DataFrame, 每列为一个题目

    Returns:
        float: α 系数, 题目数 < 2 时返回 NaN
    """
    k = df_items.shape[1]
    if k < 2:
        return np.nan
    item_vars = df_items.var(axis=0, ddof=1)
    total_var = df_items.sum(axis=1).var(ddof=1)
    if total_var == 0:
        return np.nan
    return (k / (k - 1)) * (1 - item_vars.sum() / total_var)


# ══════════════════════════════════════════════
#  数据加载 + 清洗
# ══════════════════════════════════════════════
def load_and_clean(cfg, project_dir):
    """统一数据加载 + Likert文本映射 + 缺失值删除

    Args:
        cfg: dict, 从 config.yaml 加载的配置
        project_dir: str, 项目根目录

    Returns:
        (df, N_raw, N, all_item_cols, demo_cols):
          df: 清洗后的 DataFrame
          N_raw: 原始行数
          N: 有效行数
          all_item_cols: 所有量表题目列名
          demo_cols: 人口学变量列名
    """
    import os
    data_path = os.path.join(project_dir, cfg['data_file'])
    sheet = cfg.get('sheet_name', 0)
    df = pd.read_excel(data_path, sheet_name=sheet)
    N_raw = len(df)

    # 收集所有题目列
    all_item_cols = []
    for scale in cfg.get('scales', []):
        all_item_cols.extend(scale['items'])

    # Likert 文本 → 数值映射
    likert_map = cfg.get('likert_map', None)
    if likert_map:
        for col in all_item_cols:
            if col in df.columns and df[col].dtype == object:
                df[col] = df[col].map(likert_map)

    # 人口学列
    demo_cols = [d['col'] for d in cfg.get('demographics', [])]

    # 删除关键列缺失值
    key_cols = [c for c in all_item_cols + demo_cols if c in df.columns]
    if key_cols:
        df = df.dropna(subset=key_cols)
    N = len(df)

    return df, N_raw, N, all_item_cols, demo_cols


# ══════════════════════════════════════════════
#  维度得分计算
# ══════════════════════════════════════════════
def compute_dimension_scores(df, cfg):
    """反向计分 + 计算维度均值 + 总量表得分

    Args:
        df: DataFrame（会被原地修改）
        cfg: dict, 包含 scales 和 likert_scale

    Returns:
        (dim_cols_map, scale_dims, all_dim_names, scale_names):
          dim_cols_map: {维度/量表名: [题目列]}
          scale_dims: {量表名: [子维度名]}
          all_dim_names: 所有维度+量表名的有序列表
          scale_names: 仅量表总分名称列表
    """
    dim_cols_map = {}   # {维度名: [题目列]}
    scale_dims = {}     # {量表名: [子维度名]}

    for scale in cfg.get('scales', []):
        sname = scale['name']
        if scale.get('dimensions'):
            dims = []
            for dim in scale['dimensions']:
                dname = dim['name']
                items = dim['items']
                # 反向计分
                if dim.get('reverse'):
                    likert_n = cfg.get('likert_scale', 5)
                    for col in items:
                        if col in df.columns:
                            df[col] = likert_n + 1 - df[col]
                df[dname] = df[items].mean(axis=1)
                dim_cols_map[dname] = items
                dims.append(dname)
            # 总量表得分
            df[sname] = df[scale['items']].mean(axis=1)
            dim_cols_map[sname] = scale['items']
            scale_dims[sname] = dims
        else:
            df[sname] = df[scale['items']].mean(axis=1)
            dim_cols_map[sname] = scale['items']
            scale_dims[sname] = []

    all_dim_names = list(dim_cols_map.keys())
    scale_names = [s['name'] for s in cfg.get('scales', [])]

    return dim_cols_map, scale_dims, all_dim_names, scale_names


# ══════════════════════════════════════════════
#  P 值格式化工具
# ══════════════════════════════════════════════
def p_str(p):
    """P 值格式化: <0.001 → '<0.001', 否则 '=0.xxx'"""
    return '<0.001' if p < 0.001 else f'={p:.3f}'


def sig_star(p):
    """显著性星号"""
    if p <= 0.001: return '***'
    if p < 0.01:  return '**'
    if p < 0.05:  return '*'
    return ''


def sig_text(p, pos, neg):
    """根据 P 值选择正面/负面文本"""
    return pos if p < 0.05 else neg


def direction(value):
    """正/负方向"""
    return '正' if value > 0 else '负'


def corr_strength(r):
    """相关强度描述"""
    ar = abs(r)
    if ar > 0.7: return '强'
    if ar > 0.5: return '较强'
    if ar > 0.3: return '中等'
    return '弱'


# ══════════════════════════════════════════════
#  Config 校验
# ══════════════════════════════════════════════
def validate_config(cfg, required_fields=None):
    """校验 config 必填字段

    Args:
        cfg: dict
        required_fields: list of (field_path, description)
            field_path 支持点分隔, 如 'output.format_preset'

    Returns:
        list of error messages (空列表表示通过)
    """
    if required_fields is None:
        required_fields = [
            ('project_type', '项目类型'),
            ('project_name', '项目名称'),
            ('data_file', '数据文件路径'),
        ]

    errors = []
    for field_path, desc in required_fields:
        parts = field_path.split('.')
        val = cfg
        for part in parts:
            if isinstance(val, dict):
                val = val.get(part)
            else:
                val = None
                break
        if val is None or val == '':
            errors.append(f'缺少必填字段: {field_path} ({desc})')

    return errors
