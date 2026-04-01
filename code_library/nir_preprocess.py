# ══════════════════════════════════════════════════════════════════════
# NIR 光谱预处理与KS数据集划分工具模块
# 用途：近红外/中红外光谱数据的预处理（SNV、MSC、SG平滑/求导、Detrend）
#       以及 Kennard-Stone 算法数据集划分（分类/回归通用）
# 适用场景：品种鉴别（分类）、理化值预测（回归）等光谱建模任务
# 日期：2026-03-30
# ══════════════════════════════════════════════════════════════════════

import numpy as np
import pandas as pd
from scipy.signal import savgol_filter, detrend
from scipy.spatial.distance import cdist
import os


# ══════ 1. Kennard-Stone 数据集划分（分类/回归通用） ══════

def kennard_stone(X, n_train):
    """
    Kennard-Stone 算法选择训练集样本。
    基于欧氏距离的 maximin 准则，确保训练集在特征空间中均匀分布。
    **不依赖目标变量**，分类(0/1)和回归(连续值)均可直接使用。

    Parameters
    ----------
    X : ndarray, shape (n_samples, n_features)
        光谱特征矩阵（仅光谱列，不含ID和目标列）
    n_train : int
        训练集样本数（如 round(n * 0.7) 表示 7:3 划分）

    Returns
    -------
    train_idx : list[int]
        训练集样本索引（已排序）
    test_idx : list[int]
        预测集样本索引（已排序）

    Example
    -------
    >>> X = df.iloc[:, 1:-1].values  # 提取光谱列
    >>> train_idx, test_idx = kennard_stone(X, round(len(X) * 0.7))
    >>> df_train = df.iloc[train_idx]
    >>> df_test = df.iloc[test_idx]
    """
    n_samples = X.shape[0]
    dist_matrix = cdist(X, X, metric='euclidean')

    # 选距离最大的两个样本作为初始点
    i, j = np.unravel_index(np.argmax(dist_matrix), dist_matrix.shape)
    selected = [i, j]
    remaining = list(set(range(n_samples)) - set(selected))

    # 迭代：每次选与已选集合最小距离最大的样本
    for _ in range(n_train - 2):
        min_dists = np.min(dist_matrix[np.ix_(remaining, selected)], axis=1)
        next_idx = remaining[np.argmax(min_dists)]
        selected.append(next_idx)
        remaining.remove(next_idx)

    return sorted(selected), sorted(remaining)


def ks_split_dataframe(df, train_ratio=0.7, id_col=0, target_col=-1):
    """
    对 DataFrame 执行 KS 划分，自动识别光谱列。

    Parameters
    ----------
    df : pd.DataFrame
        完整数据（第一列=ID, 中间=光谱, 最后一列=目标变量）
    train_ratio : float
        训练集比例（默认0.7）
    id_col : int
        ID列位置索引（默认0=第一列）
    target_col : int
        目标列位置索引（默认-1=最后一列）

    Returns
    -------
    df_train, df_test : pd.DataFrame
        划分后的训练集和预测集（保留全部列，reset_index）
    """
    # 提取光谱矩阵
    cols = list(df.columns)
    if target_col == -1:
        target_col = len(cols) - 1
    spectral_idx = [i for i in range(len(cols)) if i != id_col and i != target_col]
    X = df.iloc[:, spectral_idx].values

    n_train = round(len(X) * train_ratio)
    train_idx, test_idx = kennard_stone(X, n_train)

    df_train = df.iloc[train_idx].reset_index(drop=True)
    df_test = df.iloc[test_idx].reset_index(drop=True)

    print(f"KS划分完成: 训练集 {len(train_idx)} 样本, 预测集 {len(test_idx)} 样本")
    return df_train, df_test


# ══════ 2. 光谱预处理方法 ══════

def calc_snv(spectra):
    """
    SNV (Standard Normal Variate) 标准正态变量变换。
    按行标准化，消除颗粒度/表面散射影响。

    Parameters
    ----------
    spectra : ndarray, shape (n_samples, n_features)

    Returns
    -------
    snv_spectra : ndarray
    """
    mean = np.mean(spectra, axis=1, keepdims=True)
    std = np.std(spectra, axis=1, keepdims=True)
    std[std == 0] = 1e-8
    return (spectra - mean) / std


def calc_msc(spectra, reference=None):
    """
    MSC (Multiplicative Scatter Correction) 多元散射校正。

    Parameters
    ----------
    spectra : ndarray, shape (n_samples, n_features)
    reference : ndarray or None
        参考光谱。训练集设 None（自动计算均值），
        预测集需传入训练集返回的 reference。

    Returns
    -------
    msc_spectra : ndarray
    reference : ndarray
        本次使用的参考光谱（保存后传给预测集使用）

    Example
    -------
    >>> train_processed, ref = calc_msc(X_train)        # 训练集
    >>> test_processed, _   = calc_msc(X_test, ref)     # 预测集用同一ref
    """
    msc_spectra = np.zeros_like(spectra)
    if reference is None:
        reference = np.mean(spectra, axis=0)

    for i in range(spectra.shape[0]):
        fit = np.polyfit(reference, spectra[i, :], 1, full=True)
        slope, intercept = fit[0][0], fit[0][1]
        msc_spectra[i, :] = (spectra[i, :] - intercept) / slope

    return msc_spectra, reference


def calc_sg(spectra, window_length=11, polyorder=2, deriv=0):
    """
    Savitzky-Golay 平滑/求导。

    Parameters
    ----------
    spectra : ndarray
    window_length : int
        窗口长度（必须为奇数，自动修正）
    polyorder : int
        多项式阶数
    deriv : int
        0=仅平滑(SG), 1=一阶导(FD), 2=二阶导(SD)

    Returns
    -------
    sg_spectra : ndarray
    """
    if window_length % 2 == 0:
        window_length += 1
    return savgol_filter(spectra, window_length=window_length,
                         polyorder=polyorder, deriv=deriv, axis=1)


def calc_detrend(spectra):
    """
    去趋势 (Detrending)，消除基线漂移。
    使用线性去趋势。

    Parameters
    ----------
    spectra : ndarray

    Returns
    -------
    detrended : ndarray
    """
    return detrend(spectra, axis=1)


# ══════ 3. 批量预处理并保存 ══════

PREPROCESS_METHODS = {
    'snv':       {'func': lambda s, **kw: (calc_snv(s), None),
                  'label': 'SNV标准正态变量变换'},
    'msc':       {'func': lambda s, **kw: calc_msc(s, kw.get('reference')),
                  'label': 'MSC多元散射校正'},
    'sg_smooth': {'func': lambda s, **kw: (calc_sg(s, kw.get('window_length', 11),
                  kw.get('polyorder', 2), 0), None), 'label': 'SG平滑'},
    'sg_1st_der': {'func': lambda s, **kw: (calc_sg(s, kw.get('window_length', 11),
                   kw.get('polyorder', 2), 1), None), 'label': 'SG一阶导数(FD)'},
    'sg_2nd_der': {'func': lambda s, **kw: (calc_sg(s, kw.get('window_length', 11),
                   kw.get('polyorder', 2), 2), None), 'label': 'SG二阶导数(SD)'},
    'detrend':    {'func': lambda s, **kw: (calc_detrend(s), None),
                   'label': '去趋势(Detrend)'},
}


def process_and_save(input_file, output_file, method, **kwargs):
    """
    读取Excel → 分离(ID|光谱|目标) → 预处理光谱 → 按原格式保存。
    **分类和回归数据通用**，不依赖目标列类型。

    Parameters
    ----------
    input_file : str  输入Excel路径
    output_file : str 输出Excel路径
    method : str      预处理方法名（见 PREPROCESS_METHODS）
    **kwargs : dict   额外参数（如MSC的reference, SG的window_length等）

    Returns
    -------
    ref_return : ndarray or None
        MSC方法返回参考光谱，其他返回 None
    """
    print(f"  处理: {os.path.basename(input_file)} | 方法: {method}")
    df = pd.read_excel(input_file)

    col_names = df.columns
    id_col = df.iloc[:, 0]
    target_col = df.iloc[:, -1]
    spectra = df.iloc[:, 1:-1].values

    if method not in PREPROCESS_METHODS:
        raise ValueError(f"不支持: {method}。可选: {list(PREPROCESS_METHODS.keys())}")

    processed, ref_return = PREPROCESS_METHODS[method]['func'](spectra, **kwargs)

    df_out = pd.DataFrame(processed, columns=df.columns[1:-1])
    df_out.insert(0, col_names[0], id_col)
    df_out[col_names[-1]] = target_col

    df_out.to_excel(output_file, index=False)
    print(f"  → 已保存: {output_file}")
    return ref_return


def batch_preprocess(train_file, test_file, out_dir, prefix='',
                     methods=None, sg_window=11, sg_poly=2):
    """
    一键批量预处理训练集和预测集。

    Parameters
    ----------
    train_file : str   训练集Excel路径
    test_file : str    预测集Excel路径
    out_dir : str      输出目录
    prefix : str       文件名前缀（如 'nir_'）
    methods : list     要执行的方法列表，None=全部执行
    sg_window : int    SG窗口长度
    sg_poly : int      SG多项式阶数

    Example
    -------
    >>> batch_preprocess('训练集.xlsx', '预测集.xlsx', './预处理/',
    ...                  prefix='nir_', methods=['snv', 'msc', 'sg_1st_der'])
    """
    os.makedirs(out_dir, exist_ok=True)
    if methods is None:
        methods = list(PREPROCESS_METHODS.keys())

    kw = {'window_length': sg_window, 'polyorder': sg_poly}

    for m in methods:
        label = PREPROCESS_METHODS[m]['label']
        print(f"\n─── {label} ───")

        if m == 'msc':
            ref = process_and_save(train_file,
                                   f"{out_dir}/{prefix}train_{m}.xlsx", m, **kw)
            process_and_save(test_file,
                             f"{out_dir}/{prefix}test_{m}.xlsx", m, reference=ref, **kw)
        else:
            process_and_save(train_file,
                             f"{out_dir}/{prefix}train_{m}.xlsx", m, **kw)
            process_and_save(test_file,
                             f"{out_dir}/{prefix}test_{m}.xlsx", m, **kw)

    print(f"\n✅ 全部预处理完成，文件保存在: {out_dir}")
