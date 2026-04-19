# ══════════════════════════════════════════════════════════════════════
# NIR光谱分类工具函数模板
# 用途：近红外光谱数据的KS划分、预处理、模型训练与评估
# 适用场景：农产品品种鉴别、质量检测等基于NIR光谱的分类任务
# 日期：2026-03-30
# ══════════════════════════════════════════════════════════════════════

import numpy as np
from scipy.signal import savgol_filter
from scipy.spatial.distance import cdist
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix


# ══════ Kennard-Stone 数据划分 ══════
def kennard_stone(X, n_train):
    """
    Kennard-Stone算法划分训练集和测试集。
    在欧氏距离空间中选择分布最均匀的样本作为训练集。

    Parameters
    ----------
    X : ndarray, shape (n_samples, n_features)
        光谱矩阵
    n_train : int
        训练集样本数（如 int(n * 0.7) 表示 7:3 划分）

    Returns
    -------
    train_idx, test_idx : ndarray
        训练集和测试集的样本索引
    """
    n = X.shape[0]
    D = cdist(X, X, 'euclidean')
    sel = list(np.unravel_index(np.argmax(D), D.shape))
    rem = list(set(range(n)) - set(sel))
    while len(sel) < n_train:
        md = np.min(D[np.ix_(rem, sel)], axis=1)
        nxt = rem[np.argmax(md)]
        sel.append(nxt)
        rem.remove(nxt)
    return np.array(sel), np.array(rem)


# ══════ 光谱预处理方法 ══════
def snv_transform(X):
    """标准正态变量变换 (SNV)：消除光散射影响"""
    return np.array([(x - x.mean()) / x.std(ddof=1) for x in X])

def sg_derivative(X, window=15, polyorder=2, deriv=1):
    """Savitzky-Golay 求导/平滑
    deriv=0 → 平滑, deriv=1 → 一阶导, deriv=2 → 二阶导
    """
    return savgol_filter(X, window_length=window, polyorder=polyorder,
                         deriv=deriv, axis=1)

def get_all_preprocessed(X_raw, sg_window=15, sg_poly=2):
    """生成所有预处理版本"""
    return {
        'Raw': X_raw,
        'SNV': snv_transform(X_raw),
        '1st_Derivative': sg_derivative(X_raw, sg_window, sg_poly, deriv=1),
        '2nd_Derivative': sg_derivative(X_raw, sg_window, sg_poly, deriv=2),
        'SG_Smooth': sg_derivative(X_raw, sg_window, sg_poly, deriv=0),
    }


# ══════ 分类评估指标 ══════
def calc_classification_metrics(y_true, y_pred):
    """
    计算二分类指标：TP, TN, FP, FN, Accuracy, Sensitivity, Specificity

    Returns
    -------
    dict : 包含所有指标的字典
    """
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    return {
        'TP': tp, 'TN': tn, 'FP': fp, 'FN': fn,
        'Accuracy':    round((tp + tn) / (tp + tn + fp + fn), 4),
        'Sensitivity': round(tp / (tp + fn), 4) if (tp + fn) > 0 else 0,
        'Specificity': round(tn / (tn + fp), 4) if (tn + fp) > 0 else 0,
    }


# ══════ 可复用模型封装 ══════

def train_plsda(X_train, y_train, X_test, n_components=10):
    """
    PLS-DA 分类器（训练+预测）

    Parameters
    ----------
    X_train, y_train : 训练集特征和标签
    X_test : 测试集特征
    n_components : PLS主成分数（可通过RMSECV肘部图确定最优值）

    Returns
    -------
    y_pred : 预测标签
    model  : 训练好的模型（可用于后续可视化、得分图等）
    """
    from sklearn.cross_decomposition import PLSRegression
    n_comp = min(n_components, X_train.shape[0] - 1, X_train.shape[1])
    pls = PLSRegression(n_components=n_comp)
    pls.fit(X_train, y_train)
    y_pred = (pls.predict(X_test).ravel() > 0.5).astype(int)
    return y_pred, pls


def train_svm(X_train, y_train, X_test, C=10, gamma='scale', kernel='rbf'):
    """
    SVM 分类器（自动标准化 + 训练+预测）

    Parameters
    ----------
    C : 正则化参数（可通过网格搜索确定）
    gamma : RBF核系数
    kernel : 核函数类型 ('rbf', 'linear', 'poly')

    Returns
    -------
    y_pred : 预测标签
    model  : SVC 模型
    scaler : StandardScaler（测试时需用同一个scaler）
    """
    from sklearn.svm import SVC
    scaler = StandardScaler()
    X_tr_sc = scaler.fit_transform(X_train)
    X_te_sc = scaler.transform(X_test)
    svm = SVC(kernel=kernel, C=C, gamma=gamma, probability=True, random_state=42)
    svm.fit(X_tr_sc, y_train)
    y_pred = svm.predict(X_te_sc)
    return y_pred, svm, scaler


def train_rf(X_train, y_train, X_test, n_estimators=200):
    """
    随机森林分类器

    Parameters
    ----------
    n_estimators : 树的数量（可通过OOB误差肘部图确定）

    Returns
    -------
    y_pred : 预测标签
    model  : RandomForestClassifier 模型（可用 .feature_importances_ 获取特征重要性）
    """
    from sklearn.ensemble import RandomForestClassifier
    rf = RandomForestClassifier(n_estimators=n_estimators, oob_score=True,
                                 random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    y_pred = rf.predict(X_test)
    return y_pred, rf


def build_cnn_1d(input_length, num_classes=2):
    """
    构建 1D-CNN 模型（PyTorch），用于光谱分类

    结构: Conv1d(1→32,k11) → Conv1d(32→64,k7) → Conv1d(64→128,k5)
          → AdaptiveAvgPool → FC(1024→256→64→num_classes)

    Parameters
    ----------
    input_length : 输入光谱长度（波长点数）
    num_classes  : 类别数

    Returns
    -------
    model : nn.Module
    """
    import torch.nn as nn
    class NIR_CNN(nn.Module):
        def __init__(self):
            super().__init__()
            self.features = nn.Sequential(
                nn.Conv1d(1, 32, kernel_size=11, padding=5),
                nn.BatchNorm1d(32), nn.ReLU(inplace=True),
                nn.MaxPool1d(4),
                nn.Conv1d(32, 64, kernel_size=7, padding=3),
                nn.BatchNorm1d(64), nn.ReLU(inplace=True),
                nn.MaxPool1d(4),
                nn.Conv1d(64, 128, kernel_size=5, padding=2),
                nn.BatchNorm1d(128), nn.ReLU(inplace=True),
                nn.AdaptiveAvgPool1d(8),
            )
            self.classifier = nn.Sequential(
                nn.Flatten(),
                nn.Linear(128 * 8, 256), nn.ReLU(inplace=True), nn.Dropout(0.5),
                nn.Linear(256, 64), nn.ReLU(inplace=True), nn.Dropout(0.3),
                nn.Linear(64, num_classes),
            )
        def forward(self, x):
            return self.classifier(self.features(x))
    return NIR_CNN()


def train_cnn(X_train, y_train, X_test, epochs=200, lr=0.001, batch_size=16):
    """
    训练 1D-CNN 并返回预测结果

    Parameters
    ----------
    X_train, y_train : 训练集（numpy数组）
    X_test           : 测试集特征
    epochs           : 训练轮数
    lr               : 学习率
    batch_size       : 批大小

    Returns
    -------
    y_pred : 预测标签
    model  : 训练好的 CNN 模型

    Raises
    ------
    ImportError : 如果 PyTorch 未安装
    """
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import TensorDataset, DataLoader

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # 标准化
    scaler = StandardScaler()
    X_tr = scaler.fit_transform(X_train)
    X_te = scaler.transform(X_test)

    # 转Tensor (N, 1, L)
    X_tr_t = torch.FloatTensor(X_tr).unsqueeze(1).to(device)
    y_tr_t = torch.LongTensor(y_train).to(device)
    X_te_t = torch.FloatTensor(X_te).unsqueeze(1).to(device)

    loader = DataLoader(TensorDataset(X_tr_t, y_tr_t), batch_size=batch_size, shuffle=True)

    model = build_cnn_1d(X_train.shape[1]).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    model.train()
    for epoch in range(epochs):
        for bx, by in loader:
            optimizer.zero_grad()
            loss = criterion(model(bx), by)
            loss.backward()
            optimizer.step()
        scheduler.step()

    model.eval()
    with torch.no_grad():
        y_pred = torch.max(model(X_te_t), 1)[1].cpu().numpy()
    return y_pred, model


# ══════ 批量运行所有模型×预处理组合 ══════

def batch_run_models(X_raw, y, train_idx, test_idx,
                     sg_window=15, sg_poly=2,
                     models=('PLS-DA', 'SVM', 'RF'),
                     include_cnn=False):
    """
    一键运行所有预处理×模型组合，返回结果DataFrame

    Parameters
    ----------
    X_raw     : 原始光谱矩阵
    y         : 标签数组
    train_idx : KS划分的训练集索引
    test_idx  : KS划分的测试集索引
    models    : 要运行的传统模型列表
    include_cnn : 是否包含CNN（需要PyTorch）

    Returns
    -------
    pd.DataFrame : 包含 Preprocessing, Model, TP, TN, FP, FN, Accuracy, Sensitivity, Specificity
    """
    import pandas as pd
    all_data = get_all_preprocessed(X_raw, sg_window, sg_poly)
    y_train, y_test = y[train_idx], y[test_idx]
    results = []

    model_funcs = {
        'PLS-DA': lambda Xtr, ytr, Xte: train_plsda(Xtr, ytr, Xte)[0],
        'SVM':    lambda Xtr, ytr, Xte: train_svm(Xtr, ytr, Xte)[0],
        'RF':     lambda Xtr, ytr, Xte: train_rf(Xtr, ytr, Xte)[0],
    }
    if include_cnn:
        model_funcs['CNN'] = lambda Xtr, ytr, Xte: train_cnn(Xtr, ytr, Xte)[0]

    for prep_name, X_full in all_data.items():
        X_tr, X_te = X_full[train_idx], X_full[test_idx]
        for m_name in list(models) + (['CNN'] if include_cnn else []):
            if m_name not in model_funcs:
                continue
            y_pred = model_funcs[m_name](X_tr, y_train, X_te)
            row = {'Preprocessing': prep_name, 'Model': m_name}
            row.update(calc_classification_metrics(y_test, y_pred))
            results.append(row)
            print(f"  {prep_name} + {m_name}: Acc={row['Accuracy']}")

    return pd.DataFrame(results)


# ══════ 使用示例 ══════
if __name__ == '__main__':
    import pandas as pd
    from sklearn.preprocessing import LabelEncoder

    # 1. 读取数据（替换为你的文件路径）
    df = pd.read_excel('your_nir_data.xlsx', sheet_name='Sheet1')
    X_raw = df.iloc[:, 1:].values.astype(np.float64)
    y = LabelEncoder().fit_transform(df.iloc[:, 0].values)

    # 2. KS划分 (7:3)
    train_idx, test_idx = kennard_stone(X_raw, int(len(y) * 0.7))

    # ── 方式A：一键跑所有组合（5种预处理 × 3/4 种模型） ──
    results_df = batch_run_models(X_raw, y, train_idx, test_idx, include_cnn=False)
    print(results_df.to_string(index=False))
    results_df.to_excel('results.xlsx', index=False)

    # ── 方式B：单独调用某个模型 ──
    X_tr, X_te = X_raw[train_idx], X_raw[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]

    # PLS-DA（可获取模型做后续可视化）
    y_pred, pls_model = train_plsda(X_tr, y_train, X_te, n_components=10)
    print(calc_classification_metrics(y_test, y_pred))

    # SVM（返回scaler用于后续预测）
    y_pred, svm_model, svm_scaler = train_svm(X_tr, y_train, X_te, C=10, gamma='scale')
    print(calc_classification_metrics(y_test, y_pred))

    # RF（可用 rf_model.feature_importances_ 做特征分析）
    y_pred, rf_model = train_rf(X_tr, y_train, X_te, n_estimators=200)
    print(calc_classification_metrics(y_test, y_pred))

    # CNN（需要 pip install torch）
    # y_pred, cnn_model = train_cnn(X_tr, y_train, X_te, epochs=200)
    # print(calc_classification_metrics(y_test, y_pred))
