# -*- coding: utf-8 -*-
"""
ace 代码库: plot_bindent.py
用途：学术绘图初始化 + 字体常量 + 配色 + 图表模板
日期：2026-04-04 (v3.0 清理裸代码，新增地理可视化)

使用方式:
    from plot_bindent import FONT_SONG, FONT_HEI, FONT_TNR
    from plot_bindent import grouped_bar, line_with_sem, horizontal_bar
    from plot_bindent import district_choropleth  # 地理可视化
"""

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.font_manager import FontProperties
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import os

# ══════ 字体对象（精确控制，按元素指定） ══════

FONT_SONG = FontProperties(fname=r'C:\Windows\Fonts\simsun.ttc')   # 宋体 → 中文正文、轴标签
FONT_HEI  = FontProperties(fname=r'C:\Windows\Fonts\simhei.ttf')   # 黑体 → 子图标题
FONT_TNR  = FontProperties(family='Times New Roman')                # TNR  → 英文/数字/字母标记

# ══════ rcParams 基础设置 ══════

rcParams['font.serif'] = ['Times New Roman', 'SimSun']
rcParams['axes.unicode_minus'] = False
rcParams['figure.dpi'] = 300
rcParams['savefig.dpi'] = 300
rcParams['figure.figsize'] = (5.5, 4.0)  # A4适配
rcParams['font.size'] = 9
rcParams['axes.titlesize'] = 10
rcParams['axes.labelsize'] = 9
rcParams['xtick.labelsize'] = 8
rcParams['ytick.labelsize'] = 8
rcParams['legend.fontsize'] = 8
rcParams['axes.spines.top'] = False
rcParams['axes.spines.right'] = False
rcParams['xtick.direction'] = 'out'
rcParams['ytick.direction'] = 'out'
rcParams['savefig.pad_inches'] = 0.1


# ══════ 配色方案 ══════

# Okabe-Ito 色盲友好（学术首选）
OKABE_ITO = ['#E69F00', '#56B4E9', '#009E73', '#F0E442',
             '#0072B2', '#D55E00', '#CC79A7', '#000000']

# 红灰显著性
SIG_COLORS = {
    'p<0.01': '#C44E52',
    'p<0.05': '#E8866A',
    'ns':     '#8C8C8C',
}

# 分组对比（2-4组常用）
GROUP_COLORS = ['#4C72B0', '#DD8452', '#55A868', '#C44E52']

# 渐变色
HEATMAP_CMAP = 'RdBu_r'
CORR_CMAP = 'coolwarm'

# 蓝色渐变（地图/热力图用）
BLUE_GRADIENT = ['#f7fbff', '#deebf7', '#c6dbef', '#9ecae1',
                 '#6baed6', '#4292c6', '#2171b5', '#084594']


# ══════ 字体设置辅助（工具函数） ══════

def set_ax_fonts(ax, title_font=None, label_font=None, tick_font=None):
    """统一设置坐标轴字体
    
    Args:
        ax: matplotlib Axes
        title_font: 标题字体 (默认黑体)
        label_font: 轴标签字体 (默认宋体)
        tick_font: 刻度字体 (默认TNR)
    """
    if title_font is None:
        title_font = FONT_HEI
    if label_font is None:
        label_font = FONT_SONG
    if tick_font is None:
        tick_font = FONT_TNR
    
    if ax.get_title():
        ax.title.set_fontproperties(title_font)
    if ax.get_xlabel():
        ax.xaxis.label.set_fontproperties(label_font)
    if ax.get_ylabel():
        ax.yaxis.label.set_fontproperties(label_font)
    for lbl in ax.get_xticklabels() + ax.get_yticklabels():
        lbl.set_fontproperties(tick_font)


def set_legend_font(ax, text_font=None, title_font=None):
    """设置图例字体"""
    if text_font is None:
        text_font = FONT_TNR
    if title_font is None:
        title_font = FONT_SONG
    leg = ax.get_legend()
    if leg:
        if leg.get_title():
            leg.get_title().set_fontproperties(title_font)
        for t in leg.get_texts():
            t.set_fontproperties(text_font)


# ══════ 图表模板 ══════

def grouped_bar(data, groups, categories, ylabel, title='', colors=None):
    """分组柱状图（带误差线）
    
    Args:
        data: dict {group: [values_per_category]}
        groups: 分组名列表
        categories: x轴类别标签
        ylabel: y轴标签
    """
    if colors is None:
        colors = GROUP_COLORS
    x = np.arange(len(categories))
    width = 0.8 / len(groups)
    fig, ax = plt.subplots()
    for i, (group, vals) in enumerate(data.items()):
        means = [np.mean(v) for v in vals]
        sems = [np.std(v, ddof=1)/np.sqrt(len(v)) for v in vals]
        ax.bar(x + i*width - width*(len(groups)-1)/2, means,
               width, yerr=sems, label=group, color=colors[i],
               capsize=3, edgecolor='white', linewidth=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontproperties=FONT_TNR)
    ax.set_ylabel(ylabel, fontproperties=FONT_SONG)
    set_ax_fonts(ax)
    leg = ax.legend(frameon=False)
    set_legend_font(ax)
    if title:
        ax.set_title(title, fontproperties=FONT_HEI)
    fig.subplots_adjust(bottom=0.15)
    return fig, ax


def line_with_sem(data, time_labels, ylabel, title='', colors=None):
    """折线图（带SEM误差带）
    
    Args:
        data: dict {group: [values_per_time]}
        time_labels: x轴时间标签
        ylabel: y轴标签
    """
    if colors is None:
        colors = GROUP_COLORS
    fig, ax = plt.subplots()
    x = np.arange(len(time_labels))
    for i, (group, vals) in enumerate(data.items()):
        means = [np.mean(v) for v in vals]
        sems = [np.std(v, ddof=1)/np.sqrt(len(v)) for v in vals]
        ax.errorbar(x, means, yerr=sems, label=group,
                    color=colors[i], marker='o', markersize=5,
                    capsize=3, linewidth=1.5)
    ax.set_xticks(x)
    ax.set_xticklabels(time_labels, rotation=30, ha='right', fontproperties=FONT_TNR)
    ax.set_ylabel(ylabel, fontproperties=FONT_SONG)
    set_ax_fonts(ax)
    leg = ax.legend(frameon=False)
    set_legend_font(ax)
    if title:
        ax.set_title(title, fontproperties=FONT_HEI)
    fig.subplots_adjust(bottom=0.20)
    return fig, ax


def horizontal_bar(labels, values, title='', xlabel='人数（n）', colors=None):
    """横向柱形图（频数分布常用）
    
    Args:
        labels: 类别名列表（从大到小排好序）
        values: 对应值列表
        title: 图标题
        xlabel: x轴标签
    """
    fig, ax = plt.subplots(figsize=(7, max(3, len(labels) * 0.5)), dpi=200)
    
    max_val = max(values) if values else 1
    if colors is None:
        colors = [plt.cm.Blues(0.3 + 0.6 * (v / max_val)) for v in values]
    
    bars = ax.barh(range(len(labels)), values, color=colors,
                   edgecolor='#999999', linewidth=0.5, height=0.65)
    
    for i, val in enumerate(values):
        ax.text(val + max_val * 0.01, i, str(val),
                fontproperties=FONT_TNR, fontsize=8, va='center', color='#333333')
    
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontproperties=FONT_SONG, fontsize=9)
    ax.set_xlabel(xlabel, fontproperties=FONT_SONG, fontsize=10)
    if title:
        ax.set_title(title, fontproperties=FONT_HEI, fontsize=12, pad=12)
    
    for label in ax.get_xticklabels():
        label.set_fontproperties(FONT_TNR)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_xlim(0, max_val * 1.15)
    fig.subplots_adjust(left=0.20)
    return fig, ax


def did_coefficient_plot(periods, coefs, ci_lower, ci_upper, event_time=0,
                         xlabel='时间（相对于政策实施）', ylabel='DID 估计系数'):
    """DID系数图（平行趋势检验）"""
    fig, ax = plt.subplots()
    ax.errorbar(periods, coefs,
                yerr=[np.array(coefs)-np.array(ci_lower),
                      np.array(ci_upper)-np.array(coefs)],
                fmt='o', color='#0072B2', capsize=4, markersize=6)
    ax.axhline(y=0, color='gray', linestyle='--', linewidth=0.8)
    ax.axvline(x=event_time, color='red', linestyle='--', linewidth=0.8, alpha=0.5)
    ax.set_xlabel(xlabel, fontproperties=FONT_SONG)
    ax.set_ylabel(ylabel, fontproperties=FONT_SONG)
    set_ax_fonts(ax)
    fig.subplots_adjust(bottom=0.15)
    return fig, ax


def plot_roc(fpr, tpr, roc_auc, optimal_point=None):
    """ROC曲线（中英混排轴标签）"""
    fig, ax = plt.subplots()
    ax.plot(fpr, tpr, color='#C44E52', lw=2,
            label=f'ROC (AUC = {roc_auc:.3f})')
    ax.plot([0, 1], [0, 1], 'k--', lw=0.8)
    if optimal_point:
        ax.scatter(*optimal_point, marker='*', s=100, color='#E69F00',
                   zorder=5, label='最佳截断点')
    # 中英混排轴标签
    ax.set_xlabel('')
    ax.text(0.5, -0.08, '1 - 特异度 ', transform=ax.transAxes,
            ha='right', va='top', fontproperties=FONT_SONG, fontsize=9)
    ax.text(0.5, -0.08, '(FPR)', transform=ax.transAxes,
            ha='left', va='top', fontproperties=FONT_TNR, fontsize=9)
    ax.set_ylabel('')
    ax.text(-0.10, 0.5, '(TPR)', transform=ax.transAxes,
            ha='center', va='bottom', rotation=90, fontproperties=FONT_TNR, fontsize=9)
    ax.text(-0.10, 0.49, '灵敏度 ', transform=ax.transAxes,
            ha='center', va='top', rotation=90, fontproperties=FONT_SONG, fontsize=9)
    set_ax_fonts(ax)
    leg = ax.legend(loc='lower right', frameon=False)
    set_legend_font(ax)
    fig.subplots_adjust(bottom=0.15, left=0.15)
    return fig, ax


# ══════ 显著性标注 ══════

def add_significance(ax, x1, x2, y, p_value, height=0.02):
    """在柱状图上添加显著性标注线和星号"""
    if p_value < 0.001:
        text = '***'
    elif p_value < 0.01:
        text = '**'
    elif p_value < 0.05:
        text = '*'
    else:
        text = 'ns'
    y_max = y + height * (ax.get_ylim()[1] - ax.get_ylim()[0])
    ax.plot([x1, x1, x2, x2], [y, y_max, y_max, y], 'k-', lw=0.8)
    ax.text((x1+x2)/2, y_max, text, ha='center', va='bottom',
            fontsize=8, fontproperties=FONT_TNR)


# ══════ 地理可视化 ══════

def district_choropleth(geojson_path, data_dict, title='',
                        cbar_label='人数', colors=None, figsize=(8, 7)):
    """行政区热力地图（需 geopandas）
    
    Args:
        geojson_path: GeoJSON文件路径
        data_dict: {区名: 数值} 映射
        title: 图标题
        cbar_label: 色条标签
        colors: 自定义颜色列表（默认蓝色渐变）
    
    Returns:
        fig, ax
    
    示例:
        data = {'越秀区': 87, '天河区': 25, '海珠区': 43}
        fig, ax = district_choropleth('guangzhou.json', data, '分布图')
    """
    import geopandas as gpd
    
    gdf = gpd.read_file(geojson_path)
    gdf['count'] = gdf['name'].map(data_dict).fillna(0).astype(int)
    gdf['centroid'] = gdf.geometry.centroid
    
    if colors is None:
        colors = BLUE_GRADIENT
    cmap = LinearSegmentedColormap.from_list('custom', colors, N=256)
    vmax = max(data_dict.values()) if data_dict else 1
    
    fig, ax = plt.subplots(figsize=figsize, dpi=200)
    gdf.plot(column='count', cmap=cmap, linewidth=0.8,
             edgecolor='#666666', ax=ax, legend=False, vmin=0, vmax=vmax)
    
    # 标注区名 + 数值
    for _, row in gdf.iterrows():
        cx, cy = row['centroid'].x, row['centroid'].y
        count = row['count']
        text_color = 'white' if count > vmax * 0.6 else '#333333'
        ax.text(cx, cy + 0.02, row['name'],
                fontproperties=FONT_HEI, fontsize=7, color=text_color,
                ha='center', va='bottom', weight='bold')
        ax.text(cx, cy - 0.02, str(count),
                fontproperties=FONT_TNR, fontsize=8, color=text_color,
                ha='center', va='top', weight='bold')
    
    # 色条
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(0, vmax))
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, shrink=0.6, aspect=20, pad=0.02)
    cbar.set_label(cbar_label, fontproperties=FONT_SONG)
    for label in cbar.ax.get_yticklabels():
        label.set_fontproperties(FONT_TNR)
    
    if title:
        ax.set_title(title, fontproperties=FontProperties(
            fname=r'C:\Windows\Fonts\simhei.ttf', size=13), pad=15)
    ax.axis('off')
    fig.subplots_adjust(right=0.85)
    return fig, ax


# ══════ 保存辅助 ══════

def save_fig(fig, path, dpi=200):
    """标准保存图片（白底、指定DPI）"""
    fig.savefig(path, dpi=dpi, facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f"✅ 图片已保存: {path}")
