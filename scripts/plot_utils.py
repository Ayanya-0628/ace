# -*- coding: utf-8 -*-
"""
ACE 学术绘图工具集
===================
提供即用型绘图函数，统一配置中文字体、分辨率、配色。

用法（作为模块导入）:
    from plot_utils import init_style, grouped_bar, correlation_heatmap
    init_style()
    fig, ax = grouped_bar(...)
    fig.savefig('fig1.png')
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl


# ============================================================
# 配色方案
# ============================================================

# Okabe-Ito 色盲友好（学术首选）
OKABE_ITO = ['#E69F00', '#56B4E9', '#009E73', '#F0E442',
             '#0072B2', '#D55E00', '#CC79A7', '#000000']

# 显著性配色
SIG_COLORS = {
    'p<0.01': '#C44E52',
    'p<0.05': '#E8866A',
    'ns':     '#8C8C8C',
}

# 分组对比（2-4 组常用）
GROUP_COLORS = ['#4C72B0', '#DD8452', '#55A868', '#C44E52']

# 热力图色阶
HEATMAP_CMAP = 'RdBu_r'
CORR_CMAP = 'coolwarm'


# ============================================================
# 全局初始化
# ============================================================

def init_style():
    """学术绘图全局初始化（每个脚本开头调用一次）"""
    mpl.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun']
    mpl.rcParams['axes.unicode_minus'] = False
    mpl.rcParams['figure.dpi'] = 200
    mpl.rcParams['savefig.dpi'] = 200
    mpl.rcParams['figure.figsize'] = (5.5, 4.0)
    mpl.rcParams['font.size'] = 9
    mpl.rcParams['axes.titlesize'] = 10
    mpl.rcParams['axes.labelsize'] = 9
    mpl.rcParams['xtick.labelsize'] = 8
    mpl.rcParams['ytick.labelsize'] = 8
    mpl.rcParams['legend.fontsize'] = 8
    mpl.rcParams['axes.spines.top'] = False
    mpl.rcParams['axes.spines.right'] = False
    mpl.rcParams['xtick.direction'] = 'out'
    mpl.rcParams['ytick.direction'] = 'out'
    mpl.rcParams['savefig.bbox'] = 'tight'
    mpl.rcParams['savefig.pad_inches'] = 0.1


# ============================================================
# 图表函数
# ============================================================

def grouped_bar(data, categories, ylabel, title='', colors=None, figsize=None):
    """
    分组柱状图 + 误差棒

    Args:
        data: dict {组名: [各类别的数组列表]}
              例: {'实验组': [[v1,v2],[v3,v4]], '对照组': [[v5,v6],[v7,v8]]}
        categories: x轴类别标签
        ylabel: y轴标签
    Returns:
        fig, ax
    """
    if colors is None:
        colors = GROUP_COLORS
    groups = list(data.keys())
    x = np.arange(len(categories))
    width = 0.8 / len(groups)
    fig, ax = plt.subplots(figsize=figsize)

    for i, (group, vals) in enumerate(data.items()):
        means = [np.mean(v) for v in vals]
        sems = [np.std(v, ddof=1) / np.sqrt(len(v)) if len(v) > 1 else 0
                for v in vals]
        ax.bar(x + i * width - width * (len(groups) - 1) / 2, means,
               width, yerr=sems, label=group, color=colors[i % len(colors)],
               capsize=3, edgecolor='white', linewidth=0.5)

    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_ylabel(ylabel)
    ax.legend(frameon=False)
    if title:
        ax.set_title(title)
    plt.tight_layout()
    return fig, ax


def line_with_sem(data, time_labels, ylabel, title='', colors=None, figsize=None):
    """
    折线图 + 标准误

    Args:
        data: dict {组名: [各时间点的数组列表]}
        time_labels: x轴时间标签
    """
    if colors is None:
        colors = GROUP_COLORS
    fig, ax = plt.subplots(figsize=figsize)
    x = np.arange(len(time_labels))

    for i, (group, vals) in enumerate(data.items()):
        means = [np.mean(v) for v in vals]
        sems = [np.std(v, ddof=1) / np.sqrt(len(v)) if len(v) > 1 else 0
                for v in vals]
        ax.errorbar(x, means, yerr=sems, label=group,
                    color=colors[i % len(colors)], marker='o', markersize=5,
                    capsize=3, linewidth=1.5)

    ax.set_xticks(x)
    ax.set_xticklabels(time_labels, rotation=30, ha='right')
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.legend(frameon=False)
    plt.tight_layout()
    return fig, ax


def correlation_heatmap(df, cols=None, method='pearson', figsize=(5.5, 5)):
    """
    相关矩阵热力图（下三角）

    Args:
        df: DataFrame
        cols: list of str, 要计算相关的列（默认全部数值列）
        method: 'pearson' or 'spearman'
    """
    if cols is None:
        cols = df.select_dtypes(include='number').columns.tolist()

    corr = df[cols].corr(method=method)
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)

    fig, ax = plt.subplots(figsize=figsize)
    im = ax.imshow(np.where(mask, np.nan, corr), cmap=CORR_CMAP,
                   vmin=-1, vmax=1, aspect='equal')
    ax.set_xticks(range(len(cols)))
    ax.set_yticks(range(len(cols)))
    ax.set_xticklabels(cols, rotation=45, ha='right', fontsize=7)
    ax.set_yticklabels(cols, fontsize=7)

    for i in range(len(cols)):
        for j in range(len(cols)):
            if not mask[i, j]:
                ax.text(j, i, f'{corr.iloc[i, j]:.2f}', ha='center',
                        va='center', fontsize=7, color='black')

    plt.colorbar(im, ax=ax, shrink=0.8)
    plt.tight_layout()
    return fig, ax


def did_coefficient_plot(periods, coefs, ci_lower, ci_upper, event_time=0):
    """
    DID 动态效应系数图

    Args:
        periods: list, 相对时间期
        coefs: list, DID系数
        ci_lower, ci_upper: list, 置信区间上下界
        event_time: 政策实施时间点
    """
    fig, ax = plt.subplots()
    ax.errorbar(periods, coefs,
                yerr=[np.array(coefs) - np.array(ci_lower),
                      np.array(ci_upper) - np.array(coefs)],
                fmt='o', color='#0072B2', capsize=4, markersize=6)
    ax.axhline(y=0, color='gray', linestyle='--', linewidth=0.8)
    ax.axvline(x=event_time, color='red', linestyle='--', linewidth=0.8, alpha=0.5)
    ax.set_xlabel('时间（相对于政策实施）')
    ax.set_ylabel('DID 估计系数')
    plt.tight_layout()
    return fig, ax


def roc_plot(fpr, tpr, roc_auc, optimal_point=None):
    """
    ROC 曲线

    Args:
        fpr, tpr: 从 sklearn.metrics.roc_curve 获得
        roc_auc: AUC 值
        optimal_point: (fpr, tpr) 最佳截断点坐标
    """
    fig, ax = plt.subplots()
    ax.plot(fpr, tpr, color='#C44E52', lw=2,
            label=f'ROC (AUC = {roc_auc:.3f})')
    ax.plot([0, 1], [0, 1], 'k--', lw=0.8)
    if optimal_point:
        ax.scatter(*optimal_point, marker='*', s=100, color='#E69F00',
                   zorder=5, label='最佳截断点')
    ax.set_xlabel('1 - 特异度 (FPR)')
    ax.set_ylabel('灵敏度 (TPR)')
    ax.legend(loc='lower right', frameon=False)
    plt.tight_layout()
    return fig, ax


def add_significance(ax, x1, x2, y, p_value, height_ratio=0.02):
    """在柱状图上添加显著性标注线和星号"""
    if p_value < 0.001:
        text = '***'
    elif p_value < 0.01:
        text = '**'
    elif p_value < 0.05:
        text = '*'
    else:
        text = 'ns'
    y_range = ax.get_ylim()[1] - ax.get_ylim()[0]
    y_max = y + height_ratio * y_range
    ax.plot([x1, x1, x2, x2], [y, y_max, y_max, y], 'k-', lw=0.8)
    ax.text((x1 + x2) / 2, y_max, text, ha='center', va='bottom', fontsize=8)


def save_figure(fig, path, dpi=200, fmt='png'):
    """标准导出（白色背景，紧凑布局）"""
    fig.savefig(path, dpi=dpi, bbox_inches='tight',
                facecolor='white', edgecolor='none', format=fmt)
    print(f"📁 图表已保存: {path}")


# ── CLI 演示 ──
if __name__ == "__main__":
    init_style()
    print("学术绘图工具集已加载。")
    print("可用函数: init_style, grouped_bar, line_with_sem,")
    print("  correlation_heatmap, did_coefficient_plot, roc_plot,")
    print("  add_significance, save_figure")
    print("配色: OKABE_ITO, GROUP_COLORS, SIG_COLORS")
