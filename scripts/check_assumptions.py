# -*- coding: utf-8 -*-
"""
ACE 前置检验工具
=================
用法:
    python check_assumptions.py data.xlsx --cols HR MAP BIS --group 组别
    python check_assumptions.py data.xlsx --cols score --vif x1 x2 x3

功能:
    1. 正态性检验 (Shapiro-Wilk / K-S)
    2. 方差齐性检验 (Levene)
    3. 多重共线性诊断 (VIF)
    4. 输出彩色终端报告 + CSV 结果表
"""

import argparse
import sys
import numpy as np
import pandas as pd
from scipy import stats


# ── 颜色输出 ──
def _c(text, code):
    return f"\033[{code}m{text}\033[0m"

def green(t):  return _c(t, 32)
def red(t):    return _c(t, 31)
def yellow(t): return _c(t, 33)
def bold(t):   return _c(t, 1)


def check_normality(series, name="", alpha=0.05):
    """正态性检验: n<5000 用 Shapiro-Wilk，否则用 K-S"""
    series = series.dropna()
    n = len(series)
    if n < 3:
        return {"variable": name, "test": "N/A", "statistic": np.nan,
                "p_value": np.nan, "normal": None, "note": f"样本量不足(n={n})"}

    if n < 5000:
        stat, p = stats.shapiro(series)
        test_name = "Shapiro-Wilk"
    else:
        stat, p = stats.kstest(series, 'norm', args=(series.mean(), series.std()))
        test_name = "K-S"

    return {
        "variable": name,
        "test": test_name,
        "n": n,
        "statistic": round(stat, 4),
        "p_value": round(p, 4),
        "normal": p > alpha,
        "conclusion": green("✔ 正态") if p > alpha else red("✘ 非正态"),
    }


def check_levene(df, value_col, group_col, alpha=0.05):
    """Levene 方差齐性检验"""
    groups = df[group_col].unique()
    arrays = [df[df[group_col] == g][value_col].dropna().values for g in groups]
    arrays = [a for a in arrays if len(a) >= 2]

    if len(arrays) < 2:
        return {"variable": value_col, "test": "Levene",
                "statistic": np.nan, "p_value": np.nan,
                "homogeneous": None, "note": "分组不足"}

    stat, p = stats.levene(*arrays)
    return {
        "variable": value_col,
        "test": "Levene",
        "groups": len(arrays),
        "statistic": round(stat, 4),
        "p_value": round(p, 4),
        "homogeneous": p > alpha,
        "conclusion": green("✔ 方差齐") if p > alpha else red("✘ 方差不齐"),
    }


def check_vif(df, cols):
    """多重共线性 VIF 诊断"""
    from statsmodels.stats.outliers_influence import variance_inflation_factor

    X = df[cols].dropna()
    if X.shape[0] < X.shape[1] + 1:
        print(red("⚠  样本量不足，无法计算 VIF"))
        return pd.DataFrame()

    results = []
    for i, col in enumerate(cols):
        vif_val = variance_inflation_factor(X.values, i)
        status = green("✔ OK") if vif_val < 5 else (
            yellow("⚠ 注意") if vif_val < 10 else red("✘ 严重共线性"))
        results.append({
            "variable": col,
            "VIF": round(vif_val, 2),
            "conclusion": status,
        })
    return pd.DataFrame(results)


def run_full_check(df, value_cols, group_col=None, vif_cols=None, alpha=0.05):
    """运行完整前置检验套件"""
    print(bold("\n" + "=" * 60))
    print(bold("  ACE 前置检验报告"))
    print(bold("=" * 60))

    all_results = []

    # ── 1. 正态性 ──
    print(bold("\n📊 1. 正态性检验"))
    print("-" * 50)
    norm_results = []

    if group_col and group_col in df.columns:
        for col in value_cols:
            for grp in df[group_col].unique():
                series = df[df[group_col] == grp][col]
                r = check_normality(series, f"{col}[{grp}]", alpha)
                norm_results.append(r)
                print(f"  {r['variable']:30s}  {r['test']:12s}  "
                      f"W={r['statistic']:.4f}  p={r['p_value']:.4f}  {r['conclusion']}")
    else:
        for col in value_cols:
            r = check_normality(df[col], col, alpha)
            norm_results.append(r)
            print(f"  {r['variable']:30s}  {r['test']:12s}  "
                  f"stat={r['statistic']:.4f}  p={r['p_value']:.4f}  {r['conclusion']}")

    all_normal = all(r['normal'] for r in norm_results if r['normal'] is not None)

    # ── 2. 方差齐性 ──
    if group_col and group_col in df.columns:
        print(bold(f"\n📊 2. 方差齐性检验 (分组变量: {group_col})"))
        print("-" * 50)
        lev_results = []
        for col in value_cols:
            r = check_levene(df, col, group_col, alpha)
            lev_results.append(r)
            print(f"  {r['variable']:30s}  Levene F={r['statistic']:.4f}  "
                  f"p={r['p_value']:.4f}  {r['conclusion']}")

        all_homo = all(r['homogeneous'] for r in lev_results if r['homogeneous'] is not None)
    else:
        print(bold("\n📊 2. 方差齐性检验"))
        print("  ⏭  未指定分组变量，跳过")
        all_homo = True

    # ── 3. VIF ──
    if vif_cols:
        print(bold("\n📊 3. 多重共线性诊断 (VIF)"))
        print("-" * 50)
        vif_df = check_vif(df, vif_cols)
        if not vif_df.empty:
            for _, row in vif_df.iterrows():
                print(f"  {row['variable']:30s}  VIF={row['VIF']:.2f}  {row['conclusion']}")

    # ── 建议 ──
    print(bold("\n" + "=" * 60))
    print(bold("  📋 综合建议"))
    print("=" * 60)
    if all_normal and all_homo:
        print(green("  ✔ 满足参数检验条件，可使用 t检验 / ANOVA / 回归"))
    elif all_normal and not all_homo:
        print(yellow("  ⚠ 正态但方差不齐 → 使用 Welch's t / Welch ANOVA"))
    elif not all_normal:
        print(yellow("  ⚠ 非正态 → 建议使用非参数检验 (Mann-Whitney U / Kruskal-Wallis)"))
        print(yellow("    或对数据做变换 (log / sqrt / Box-Cox)"))
    print()


def main():
    parser = argparse.ArgumentParser(description="ACE 前置检验工具")
    parser.add_argument("file", help="Excel/CSV 数据文件路径")
    parser.add_argument("--sheet", default=0, help="Excel sheet名或索引 (默认0)")
    parser.add_argument("--cols", nargs="+", required=True, help="要检验的数值列名")
    parser.add_argument("--group", default=None, help="分组变量列名 (可选)")
    parser.add_argument("--vif", nargs="*", default=None, help="VIF检验的自变量列 (可选)")
    parser.add_argument("--alpha", type=float, default=0.05, help="显著性水平 (默认0.05)")
    args = parser.parse_args()

    # 读取数据
    if args.file.endswith('.csv'):
        df = pd.read_csv(args.file)
    else:
        sheet = int(args.sheet) if args.sheet.isdigit() else args.sheet
        df = pd.read_excel(args.file, sheet_name=sheet)

    print(f"📂 数据文件: {args.file}")
    print(f"   样本量: {len(df)}, 列数: {len(df.columns)}")

    # 检查列名
    missing = [c for c in args.cols if c not in df.columns]
    if missing:
        print(red(f"❌ 列名不存在: {missing}"))
        print(f"   可用列: {list(df.columns)}")
        sys.exit(1)

    run_full_check(df, args.cols, args.group, args.vif, args.alpha)


if __name__ == "__main__":
    main()
