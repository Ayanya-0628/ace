# -*- coding: utf-8 -*-
"""
ACE 问卷分析流水线
===================
用法:
    python questionnaire_pipeline.py data.xlsx --dims 维度1:Q1,Q2,Q3 维度2:Q4,Q5 --reverse Q3,Q5
    python questionnaire_pipeline.py data.xlsx --dims auto --kmo --efa 3

功能（按顺序执行）:
    1. 数据清洗（缺失值、异常值、反向计分）
    2. 描述性统计（频率、均值±标准差）
    3. 信度检验（Cronbach's α，总量表+各维度）
    4. KMO + Bartlett 球形检验
    5. 探索性因子分析（EFA，可选）
    6. 输出终端报告 + Excel 结果
"""

import argparse
import sys
import numpy as np
import pandas as pd


# ── 颜色输出 ──
def _c(t, code): return f"\033[{code}m{t}\033[0m"
def green(t):  return _c(t, 32)
def red(t):    return _c(t, 31)
def yellow(t): return _c(t, 33)
def bold(t):   return _c(t, 1)


def cronbachs_alpha(df):
    """计算 Cronbach's α 系数"""
    df = df.dropna()
    if df.shape[1] < 2 or df.shape[0] < 3:
        return np.nan
    k = df.shape[1]
    item_vars = df.var(axis=0, ddof=1)
    total_var = df.sum(axis=1).var(ddof=1)
    if total_var == 0:
        return np.nan
    alpha = (k / (k - 1)) * (1 - item_vars.sum() / total_var)
    return alpha


def alpha_quality(alpha):
    """α 系数质量判断"""
    if np.isnan(alpha):
        return red("N/A")
    elif alpha >= 0.9:
        return green(f"{alpha:.3f} 优秀")
    elif alpha >= 0.8:
        return green(f"{alpha:.3f} 良好")
    elif alpha >= 0.7:
        return yellow(f"{alpha:.3f} 可接受")
    elif alpha >= 0.6:
        return yellow(f"{alpha:.3f} 勉强")
    else:
        return red(f"{alpha:.3f} 不可接受")


def citc_analysis(df):
    """校正项目-总分相关 (CITC)"""
    results = []
    total = df.sum(axis=1)
    for col in df.columns:
        rest = total - df[col]
        corr = df[col].corr(rest)
        # 删除该项后的 α
        remaining = df.drop(columns=[col])
        alpha_if_del = cronbachs_alpha(remaining)
        results.append({
            'item': col,
            'CITC': round(corr, 3) if not np.isnan(corr) else np.nan,
            'alpha_if_deleted': round(alpha_if_del, 3) if not np.isnan(alpha_if_del) else np.nan,
        })
    return pd.DataFrame(results)


def kmo_bartlett(df):
    """KMO 检验 + Bartlett 球形检验"""
    try:
        from factor_analyzer.factor_analyzer import calculate_kmo, calculate_bartlett_sphericity
    except ImportError:
        print(red("❌ 请安装 factor_analyzer: pip install factor_analyzer"))
        return None, None, None

    df_clean = df.dropna()
    kmo_all, kmo_model = calculate_kmo(df_clean)
    chi2, p = calculate_bartlett_sphericity(df_clean)
    return kmo_model, chi2, p


def efa(df, n_factors, rotation='varimax'):
    """探索性因子分析"""
    try:
        from factor_analyzer import FactorAnalyzer
    except ImportError:
        print(red("❌ 请安装 factor_analyzer: pip install factor_analyzer"))
        return None, None

    df_clean = df.dropna()
    fa = FactorAnalyzer(n_factors=n_factors, rotation=rotation)
    fa.fit(df_clean)

    loadings = pd.DataFrame(
        fa.loadings_, index=df_clean.columns,
        columns=[f'因子{i+1}' for i in range(n_factors)]
    )
    variance = fa.get_factor_variance()
    var_df = pd.DataFrame({
        '因子': [f'因子{i+1}' for i in range(n_factors)],
        '特征值': variance[0],
        '方差解释率(%)': variance[1] * 100,
        '累计方差解释率(%)': variance[2] * 100,
    })
    return loadings, var_df


def run_pipeline(df, dimensions, reverse_items=None,
                 do_kmo=False, n_efa_factors=None):
    """
    执行问卷分析流水线

    Args:
        df: DataFrame，问卷数据
        dimensions: dict, {'维度名': ['Q1','Q2',...]}
        reverse_items: list，需要反向计分的列名
        do_kmo: bool，是否进行 KMO + Bartlett 检验
        n_efa_factors: int or None，EFA 因子数
    """
    all_items = []
    for items in dimensions.values():
        all_items.extend(items)

    # ── 0. 数据清洗 ──
    print(bold("\n" + "=" * 60))
    print(bold("  ACE 问卷分析报告"))
    print("=" * 60)
    print(f"\n📂 样本量: {len(df)}, 问卷题项: {len(all_items)}")

    # 检查缺失
    missing = df[all_items].isnull().sum()
    if missing.sum() > 0:
        print(yellow(f"⚠  发现缺失值:"))
        for col in missing[missing > 0].index:
            print(f"    {col}: {missing[col]} 个缺失 ({missing[col]/len(df)*100:.1f}%)")

    # 反向计分
    if reverse_items:
        max_val = df[all_items].max().max()
        min_val = df[all_items].min().min()
        for col in reverse_items:
            if col in df.columns:
                df[col] = (max_val + min_val) - df[col]
        print(f"🔄 反向计分: {reverse_items} (极值 {min_val}-{max_val})")

    # ── 1. 描述性统计 ──
    print(bold("\n📊 1. 描述性统计"))
    print("-" * 50)
    desc = df[all_items].describe().T[['count', 'mean', 'std', 'min', 'max']]
    desc.columns = ['N', '均值', '标准差', '最小值', '最大值']
    print(desc.round(3).to_string())

    # ── 2. 信度检验 ──
    print(bold("\n📊 2. 信度检验 (Cronbach's α)"))
    print("-" * 50)

    # 总量表
    total_alpha = cronbachs_alpha(df[all_items])
    print(f"  {'总量表':20s}  k={len(all_items):3d}  α = {alpha_quality(total_alpha)}")

    # 各维度
    reliability_results = []
    for dim_name, items in dimensions.items():
        if len(items) < 2:
            a = np.nan
        else:
            a = cronbachs_alpha(df[items])
        print(f"  {dim_name:20s}  k={len(items):3d}  α = {alpha_quality(a)}")
        reliability_results.append({
            '维度': dim_name, '题项数': len(items), 'α': round(a, 3)
        })

    # CITC
    print(bold("\n  📋 CITC分析 (校正项目-总分相关)"))
    citc_df = citc_analysis(df[all_items])
    low_citc = citc_df[citc_df['CITC'] < 0.3]
    if not low_citc.empty:
        print(yellow(f"  ⚠ CITC<0.3 的题项 (建议删除):"))
        for _, r in low_citc.iterrows():
            print(f"    {r['item']}: CITC={r['CITC']:.3f}, 删后α={r['alpha_if_deleted']:.3f}")
    else:
        print(green("  ✔ 所有题项 CITC≥0.3"))

    # ── 3. KMO + Bartlett ──
    if do_kmo:
        print(bold("\n📊 3. KMO + Bartlett 球形检验"))
        print("-" * 50)
        kmo_val, chi2, p = kmo_bartlett(df[all_items])
        if kmo_val is not None:
            kmo_status = green("✔ 适合") if kmo_val > 0.6 else red("✘ 不适合")
            bart_status = green("✔ 显著") if p < 0.05 else red("✘ 不显著")
            print(f"  KMO = {kmo_val:.3f}  {kmo_status}")
            print(f"  Bartlett χ² = {chi2:.1f}, p = {p:.4f}  {bart_status}")

    # ── 4. EFA ──
    if n_efa_factors:
        print(bold(f"\n📊 4. 探索性因子分析 (EFA, {n_efa_factors}因子, varimax)"))
        print("-" * 50)
        loadings, var_df = efa(df[all_items], n_efa_factors)
        if loadings is not None:
            print("  因子载荷矩阵:")
            print(loadings.round(3).to_string())
            print(f"\n  方差解释:")
            print(var_df.round(3).to_string(index=False))

    # ── 综合建议 ──
    print(bold("\n" + "=" * 60))
    print(bold("  📋 综合建议"))
    print("=" * 60)
    issues = []
    if total_alpha < 0.7:
        issues.append("总量表 α<0.7, 信度不足")
    if not low_citc.empty:
        issues.append(f"{len(low_citc)} 个题项 CITC<0.3, 建议删除后重新计算")
    if do_kmo and kmo_val is not None and kmo_val < 0.6:
        issues.append("KMO<0.6, 不适合做因子分析")

    if not issues:
        print(green("  ✔ 问卷质量良好，可进行后续分析"))
    else:
        for issue in issues:
            print(yellow(f"  ⚠ {issue}"))
    print()

    return {
        'descriptive': desc,
        'reliability': pd.DataFrame(reliability_results),
        'citc': citc_df,
    }


def parse_dimensions(dim_strs):
    """解析 维度名:Q1,Q2,Q3 格式"""
    dims = {}
    for s in dim_strs:
        if ':' in s:
            name, cols_str = s.split(':', 1)
            cols = [c.strip() for c in cols_str.split(',')]
            dims[name] = cols
        else:
            dims[s] = [s]
    return dims


def main():
    parser = argparse.ArgumentParser(description="ACE 问卷分析流水线")
    parser.add_argument("file", help="Excel/CSV 数据文件")
    parser.add_argument("--sheet", default=0, help="Sheet名或索引")
    parser.add_argument("--dims", nargs="+", required=True,
                        help="维度定义, 格式: 维度名:Q1,Q2,Q3")
    parser.add_argument("--reverse", default=None,
                        help="反向计分题项, 逗号分隔")
    parser.add_argument("--kmo", action="store_true", help="执行 KMO+Bartlett 检验")
    parser.add_argument("--efa", type=int, default=None, help="EFA 因子数")
    parser.add_argument("--output", default=None, help="导出 Excel 结果文件")
    args = parser.parse_args()

    # 读取
    if args.file.endswith('.csv'):
        df = pd.read_csv(args.file)
    else:
        sheet = int(args.sheet) if str(args.sheet).isdigit() else args.sheet
        df = pd.read_excel(args.file, sheet_name=sheet)

    dims = parse_dimensions(args.dims)
    reverse = args.reverse.split(',') if args.reverse else None

    results = run_pipeline(df, dims, reverse, args.kmo, args.efa)

    # 导出
    if args.output:
        with pd.ExcelWriter(args.output, engine='openpyxl') as writer:
            results['descriptive'].to_excel(writer, sheet_name='描述性统计')
            results['reliability'].to_excel(writer, sheet_name='信度', index=False)
            results['citc'].to_excel(writer, sheet_name='CITC', index=False)
        print(f"📁 结果已导出: {args.output}")


if __name__ == "__main__":
    main()
