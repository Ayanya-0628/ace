# -*- coding: utf-8 -*-
# ace 代码库: plot_bindent.py
# 从 SKILL.md 提取的可复用代码模板
# 使用时复制对应函数/代码段，替换变量名即可

# ══════ 全局绘图初始化（每个脚本开头必加） ══════

import matplotlib

matplotlib.use('Agg')

import matplotlib.pyplot as plt

from matplotlib import rcParams

from matplotlib.font_manager import FontProperties

import numpy as np

# ══════ 字体对象（精确控制，按元素指定） ══════

FONT_SONG = FontProperties(fname=r'C:\Windows\Fonts\simsun.ttc')   # 宋体 → 中文正文、轴标签

FONT_HEI  = FontProperties(fname=r'C:\Windows\Fonts\simhei.ttf')   # 黑体 → 子图标题

FONT_TNR  = FontProperties(family='Times New Roman')                # TNR  → 英文/数字/字母标记

# ══════ 仅设serif回退 + 负号，不设全局字体 ══════

rcParams['font.serif'] = ['Times New Roman', 'SimSun']

rcParams['axes.unicode_minus'] = False

# ── 分辨率 ──

rcParams['figure.dpi'] = 300

rcParams['savefig.dpi'] = 300

# ── 图形尺寸（A4适配） ──

rcParams['figure.figsize'] = (5.5, 4.0)  # 英寸

# ── 字体大小（全局默认值，可被 fontproperties 覆盖） ──

rcParams['font.size'] = 9

rcParams['axes.titlesize'] = 10

rcParams['axes.labelsize'] = 9

rcParams['xtick.labelsize'] = 8

rcParams['ytick.labelsize'] = 8

rcParams['legend.fontsize'] = 8

# ── 边框/刻度 ──

rcParams['axes.spines.top'] = False

rcParams['axes.spines.right'] = False

rcParams['xtick.direction'] = 'out'

rcParams['ytick.direction'] = 'out'

# ── 输出 ──

rcParams['savefig.bbox'] = 'tight'

rcParams['savefig.pad_inches'] = 0.1


# ══════ 未知章节 ══════

# 子图标题 → 黑体

ax.set_title('返青期', fontproperties=FONT_HEI, fontsize=11, fontweight='bold')

# 中英混排轴标签 → 拆成两个 ax.text，分别用宋体和TNR

ax.text(-0.13, 0.50, '(cm)', transform=ax.transAxes,

        fontproperties=FONT_TNR, fontsize=10, ha='center', va='bottom', rotation=90)

ax.text(-0.13, 0.49, '土层深度', transform=ax.transAxes,

        fontproperties=FONT_SONG, fontsize=10, ha='center', va='top', rotation=90)

# 刻度数字 → TNR

for label in ax.get_xticklabels():

    label.set_fontproperties(FONT_TNR)

    label.set_fontsize(9)

# 图例文字 → TNR（处理名），图例标题 → 宋体

leg = ax.legend(title='处理', title_fontproperties=FONT_SONG.copy())

for text in leg.get_texts():

    text.set_fontproperties(FONT_TNR)

# 显著性字母标记 → TNR

ax.text(x, y, 'ab', fontproperties=FONT_TNR, fontsize=9)

# 保存（学术投稿推荐 300 DPI）

plt.savefig('output.png', dpi=300, bbox_inches='tight', facecolor='white')


# ══════ 配色方案 ══════

# ── Okabe-Ito 色盲友好（学术首选） ──

OKABE_ITO = ['#E69F00', '#56B4E9', '#009E73', '#F0E442',

             '#0072B2', '#D55E00', '#CC79A7', '#000000']

# ── 红灰显著性 ──

SIG_COLORS = {

    'p<0.01': '#C44E52',     # 深红

    'p<0.05': '#E8866A',     # 浅红

    'ns':     '#8C8C8C',     # 灰色

}

# ── 分组对比（2-4组常用） ──

GROUP_COLORS = ['#4C72B0', '#DD8452', '#55A868', '#C44E52']

# ── 渐变色（热力图） ──

HEATMAP_CMAP = 'RdBu_r'     # 红蓝色阶

CORR_CMAP = 'coolwarm'       # 相关矩阵


# ══════ 图表模板 ══════
def grouped_bar(data, groups, categories, ylabel, title='', colors=None):
    """
    data: dict {group: [values]}
    categories: x轴类别标签
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
    for lbl in ax.get_yticklabels():
        lbl.set_fontproperties(FONT_TNR)
    leg = ax.legend(frameon=False)
    for t in leg.get_texts():
        t.set_fontproperties(FONT_TNR)
    if title:
        ax.set_title(title, fontproperties=FONT_HEI)
    plt.tight_layout()
    return fig, ax

# ══════ 未知章节 ══════
def line_with_sem(data, time_labels, ylabel, groups=None, colors=None):
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
    for lbl in ax.get_xticklabels() + ax.get_yticklabels():
        lbl.set_fontproperties(FONT_TNR)
    leg = ax.legend(frameon=False)
    for t in leg.get_texts():
        t.set_fontproperties(FONT_TNR)
    plt.tight_layout()
    return fig, ax

# ══════ 未知章节 ══════
def did_coefficient_plot(periods, coefs, ci_lower, ci_upper, event_time=0):
    fig, ax = plt.subplots()
    ax.errorbar(periods, coefs, yerr=[np.array(coefs)-np.array(ci_lower),
                np.array(ci_upper)-np.array(coefs)],
                fmt='o', color='#0072B2', capsize=4, markersize=6)
    ax.axhline(y=0, color='gray', linestyle='--', linewidth=0.8)
    ax.axvline(x=event_time, color='red', linestyle='--', linewidth=0.8, alpha=0.5)
    ax.set_xlabel('时间（相对于政策实施）', fontproperties=FONT_SONG)
    ax.set_ylabel('DID 估计系数', fontproperties=FONT_SONG)
    for lbl in ax.get_xticklabels() + ax.get_yticklabels():
        lbl.set_fontproperties(FONT_TNR)
    plt.tight_layout()
    return fig, ax

# ══════ 未知章节 ══════
def plot_roc(fpr, tpr, roc_auc, optimal_point=None):
    fig, ax = plt.subplots()
    ax.plot(fpr, tpr, color='#C44E52', lw=2,
            label=f'ROC (AUC = {roc_auc:.3f})')
    ax.plot([0, 1], [0, 1], 'k--', lw=0.8)
    if optimal_point:
        ax.scatter(*optimal_point, marker='*', s=100, color='#E69F00',
                   zorder=5, label='最佳截断点')
    # 中英混排轴标签：拆成两个 text
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
    for lbl in ax.get_xticklabels() + ax.get_yticklabels():
        lbl.set_fontproperties(FONT_TNR)
    leg = ax.legend(loc='lower right', frameon=False)
    for t in leg.get_texts():
        t.set_fontproperties(FONT_TNR)
    plt.tight_layout()
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

# ══════ 图片导出 ══════
# 标准导出（嵌入Word / 投稿用，统一 300 DPI）
fig.savefig('figure1.png', dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')

# 高清版（印刷用）
fig.savefig('figure1_hires.tiff', dpi=300, bbox_inches='tight')

# 矢量图（编辑用）

fig.savefig('figure1.svg', bbox_inches='tight')

fig.savefig('figure1.pdf', bbox_inches='tight')


