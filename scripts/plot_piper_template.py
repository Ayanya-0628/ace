# -*- coding: utf-8 -*-
"""
ACE 绘图模板：标准的几何 Piper 三线图 (Geometric Piper Diagram)
基于纯平行的散点逆推映射机制，彻底解决等分菱形与下三角偏位、阴离子标反的问题。

用法：
将包含 mg/L 离子的 DataFrame 传入该脚本的函数，由 mg_to_meq 完成换算及百分比投图。
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.font_manager import FontProperties

def plot_piper(df, out_path="Piper三线图.png"):
    """
    几何标准 Piper 三线图投影算法 (完美居中对应)
    输入 df 必须包含 'Ca', 'Mg', 'Na', 'K', 'Cl', 'SO4', 'HCO3' (单位: meq/L 或是 %meq，若是 mg/L 需先进行换算)
    在此模板中假设 df 已经是 meq 表！
    """
    meq = df.copy()
    
    # 若需转换 mg/L -> meq/L 请自行编写 mg_to_meq，并在此之前调用
    if 'K' not in meq.columns:
        meq['K'] = 0
    
    # 阳离子总和
    cat_sum = meq['Ca'] + meq['Mg'] + meq['Na'] + meq['K']
    # 阴离子总和
    an_sum  = meq['Cl'] + meq['SO4'] + meq['HCO3']
    
    # 获取每一项的占比 (0-1)
    ca_f  = (meq['Ca'] / cat_sum).fillna(0)
    mg_f  = (meq['Mg'] / cat_sum).fillna(0)
    nak_f = ((meq['Na'] + meq['K']) / cat_sum).fillna(0)
    
    cl_f   = (meq['Cl'] / an_sum).fillna(0)
    so4_f  = (meq['SO4'] / an_sum).fillna(0)
    hco3_f = (meq['HCO3'] / an_sum).fillna(0)
    
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_aspect('equal')
    ax.axis('off')
    
    h = np.sqrt(3)/2
    gap = 0.2  # 左右三角形间距
    
    # 左侧阳离子三角形顶点：Ca(0,0), Mg(0.5, h), NaK(1,0)
    cat_verts = np.array([[0,0], [1,0], [0.5,h], [0,0]])
    ax.plot(cat_verts[:,0], cat_verts[:,1], 'k-', lw=1.2)
    
    # 右侧阴离子三角形顶点：HCO3(1+gap,0), Cl(2+gap,0), SO4(1.5+gap,h)
    an_verts = np.array([[1+gap,0], [2+gap,0], [1.5+gap,h], [1+gap,0]])
    ax.plot(an_verts[:,0], an_verts[:,1], 'k-', lw=1.2)
    
    # 顶部菱形顶点
    dia_verts = np.array([
        [1 + gap/2, h*gap],                          # Bottom
        [1.5 + gap/2, h*(gap+1)],                    # Right
        [1 + gap/2, h*(gap+2)],                      # Top
        [0.5 + gap/2, h*(gap+1)],                    # Left
        [1 + gap/2, h*gap]                           # Close
    ])
    ax.plot(dia_verts[:,0], dia_verts[:,1], 'k-', lw=1.2)
    
    # ── 画网格网 ──
    ticks = [0.2, 0.4, 0.6, 0.8]
    tick_labels = ['20', '40', '60', '80']
    
    for idx, f in enumerate(ticks):
        # 阳离子网格
        ax.plot([0.5*(1-f), 1-f], [h*(1-f), 0], 'k-', lw=0.3, alpha=0.3)
        ax.text(0.5*(1-f)-0.02, h*(1-f), tick_labels[idx], fontsize=7, ha='right')
        ax.plot([0.5*f, 1-f+0.5*f], [h*f, h*f], 'k-', lw=0.3, alpha=0.3)
        ax.text(1-f+0.5*f+0.02, h*f, tick_labels[idx], fontsize=7, ha='left')
        ax.plot([f, f+0.5*(1-f)], [0, h*(1-f)], 'k-', lw=0.3, alpha=0.3)
        ax.text(f, -0.03, tick_labels[idx], fontsize=7, ha='center', va='top')
        
        # 阴离子网格
        ax.plot([1+gap+0.5*(1-f), 1+gap+1-f], [h*(1-f), 0], 'k-', lw=0.3, alpha=0.3)
        ax.text(1+gap+1-f, -0.03, tick_labels[idx], fontsize=7, ha='center', va='top')
        ax.plot([1+gap+0.5*f, 1+gap+(1-f)+0.5*f], [h*f, h*f], 'k-', lw=0.3, alpha=0.3)
        ax.text(1+gap+0.5*f-0.02, h*f, tick_labels[idx], fontsize=7, ha='right')
        ax.plot([1+gap+f, 1+gap+f+0.5*(1-f)], [0, h*(1-f)], 'k-', lw=0.3, alpha=0.3)
        ax.text(1+gap+f+0.5*(1-f)+0.02, h*(1-f), tick_labels[idx], fontsize=7, ha='left')

        # 菱形网格
        ax.plot([1+gap/2-f/2, 1+gap/2-f/2+0.5], [h*(gap+f), h*(gap+f+1)], 'k-', lw=0.3, alpha=0.3)
        ax.text(1+gap/2-f/2-0.02, h*(gap+f), tick_labels[idx], fontsize=7, ha='right')
        ax.plot([1+gap/2+f/2, 1+gap/2+f/2-0.5], [h*(gap+f), h*(gap+f+1)], 'k-', lw=0.3, alpha=0.3)
        ax.text(1+gap/2+f/2+0.02, h*(gap+f), tick_labels[idx], fontsize=7, ha='left')

    # ── 数据散点投影绘制 ──
    cat_px = nak_f + 0.5 * mg_f
    cat_py = h * mg_f
    ax.scatter(cat_px, cat_py, c='black', s=25, ec='none', zorder=5)
    
    an_px = 1 + gap + cl_f + 0.5 * so4_f
    an_py = h * so4_f
    ax.scatter(an_px, an_py, c='black', s=25, ec='none', zorder=5)
    
    # 菱形散点映射
    dia_x_factor = ca_f + mg_f
    dia_y_factor = so4_f + cl_f
    dia_px = 1 + gap/2 + (dia_y_factor - dia_x_factor) / 2
    dia_py = h * (gap + dia_x_factor + dia_y_factor)
    ax.scatter(dia_px, dia_py, c='black', s=25, ec='none', zorder=5)
    
    # 顶点标签补充
    ax.text(0-0.05, -0.05, 'Ca²⁺', fontsize=10, ha='right')
    ax.text(1+0.05, -0.05, 'Na⁺+K⁺', fontsize=10, ha='left')
    ax.text(0.5, h+0.05, 'Mg²⁺', fontsize=10, ha='center')
    
    ax.text(1+gap-0.05, -0.05, 'HCO₃⁻+CO₃²⁻', fontsize=10, ha='right')
    ax.text(2+gap+0.05, -0.05, 'Cl⁻', fontsize=10, ha='left')
    ax.text(1.5+gap, h+0.05, 'SO₄²⁻', fontsize=10, ha='center')
    
    ax.text(0.5+gap/2 - 0.05, h*(gap+1), 'Ca²⁺+Mg²⁺', fontsize=10, ha='right')
    ax.text(1.5+gap/2 + 0.05, h*(gap+1), 'SO₄²⁻+Cl⁻', fontsize=10, ha='left')

    ax.set_xlim(-0.2, 2.2 + gap)
    ax.set_ylim(-0.15, h*(gap+2) + 0.15)
    
    fig.savefig(out_path, dpi=200, facecolor='white', bbox_inches='tight')
    plt.close()

if __name__ == '__main__':
    print("Piper 三线图通用几何作图库可以导入。")
