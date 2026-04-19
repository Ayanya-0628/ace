# -*- coding: utf-8 -*-
# ace 代码库: ml_pipeline.py
# 从 SKILL.md 提取的可复用代码模板
# 使用时复制对应函数/代码段，替换变量名即可

# ══════ 数据预处理 Pipeline ══════

from sklearn.model_selection import train_test_split

from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder

from sklearn.impute import SimpleImputer

from sklearn.pipeline import Pipeline

from sklearn.compose import ColumnTransformer

import pandas as pd

import numpy as np

# ── 数据集划分 ──

X_train, X_test, y_train, y_test = train_test_split(

    X, y, test_size=0.2, random_state=42, stratify=y  # 分类任务加 stratify

)

# ── 数值+分类混合 Pipeline ──

num_cols = X.select_dtypes(include='number').columns.tolist()

cat_cols = X.select_dtypes(include='object').columns.tolist()

preprocessor = ColumnTransformer([

    ('num', Pipeline([

        ('imputer', SimpleImputer(strategy='median')),

        ('scaler', StandardScaler())

    ]), num_cols),

    ('cat', Pipeline([

        ('imputer', SimpleImputer(strategy='most_frequent')),

        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))

    ]), cat_cols)

])


# ══════ 随机森林分类 ══════

from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (classification_report, confusion_matrix,

                             roc_auc_score, accuracy_score)

# ── 基础模型 ──

rf_clf = Pipeline([

    ('prep', preprocessor),

    ('clf', RandomForestClassifier(

        n_estimators=200,

        max_depth=None,         # 先不限制，调参时再约束

        min_samples_split=5,

        min_samples_leaf=2,

        max_features='sqrt',

        class_weight='balanced', # 类别不平衡时使用

        random_state=42,

        n_jobs=-1

    ))

])

rf_clf.fit(X_train, y_train)

y_pred = rf_clf.predict(X_test)

y_proba = rf_clf.predict_proba(X_test)

# ── 评估 ──

print(classification_report(y_test, y_pred, digits=4))

print(f'Accuracy: {accuracy_score(y_test, y_pred):.4f}')

# 多分类 AUC

auc = roc_auc_score(y_test, y_proba, multi_class='ovr', average='weighted')

print(f'AUC (weighted OVR): {auc:.4f}')


# ══════ 随机森林回归 ══════

from sklearn.ensemble import RandomForestRegressor

from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

rf_reg = Pipeline([

    ('prep', preprocessor),

    ('reg', RandomForestRegressor(

        n_estimators=200,

        max_depth=None,

        min_samples_split=5,

        min_samples_leaf=2,

        max_features='sqrt',

        random_state=42,

        n_jobs=-1

    ))

])

rf_reg.fit(X_train, y_train)

y_pred = rf_reg.predict(X_test)

print(f'R²:   {r2_score(y_test, y_pred):.4f}')

print(f'RMSE: {np.sqrt(mean_squared_error(y_test, y_pred)):.4f}')

print(f'MAE:  {mean_absolute_error(y_test, y_pred):.4f}')


# ══════ 超参调优 ══════

from sklearn.model_selection import GridSearchCV

param_grid = {

    'clf__n_estimators': [100, 200, 500],

    'clf__max_depth': [5, 10, 20, None],

    'clf__min_samples_split': [2, 5, 10],

    'clf__min_samples_leaf': [1, 2, 4],

    'clf__max_features': ['sqrt', 'log2'],

}

grid = GridSearchCV(

    rf_clf, param_grid,

    cv=5, scoring='accuracy',  # 或 'roc_auc_ovr_weighted'

    n_jobs=-1, verbose=1, refit=True

)

grid.fit(X_train, y_train)

print(f'最优参数: {grid.best_params_}')

print(f'最优CV分数: {grid.best_score_:.4f}')

best_model = grid.best_estimator_


# ══════ 未知章节 ══════

from sklearn.model_selection import RandomizedSearchCV

from scipy.stats import randint, uniform

param_dist = {

    'clf__n_estimators': randint(100, 1000),

    'clf__max_depth': [5, 10, 15, 20, 30, None],

    'clf__min_samples_split': randint(2, 20),

    'clf__min_samples_leaf': randint(1, 10),

    'clf__max_features': ['sqrt', 'log2', 0.3, 0.5],

}

random_search = RandomizedSearchCV(

    rf_clf, param_dist,

    n_iter=100, cv=5, scoring='accuracy',

    random_state=42, n_jobs=-1, verbose=1

)

random_search.fit(X_train, y_train)

print(f'最优参数: {random_search.best_params_}')


# ══════ 未知章节 ══════

import optuna

from sklearn.model_selection import cross_val_score

def objective(trial):

    params = {

        'n_estimators': trial.suggest_int('n_estimators', 100, 1000),

        'max_depth': trial.suggest_int('max_depth', 3, 30),

        'min_samples_split': trial.suggest_int('min_samples_split', 2, 20),

        'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 10),

        'max_features': trial.suggest_categorical('max_features', ['sqrt', 'log2']),

    }

    clf = Pipeline([

        ('prep', preprocessor),

        ('clf', RandomForestClassifier(**params, random_state=42, n_jobs=-1))

    ])

    score = cross_val_score(clf, X_train, y_train, cv=5, scoring='accuracy').mean()

    return score

study = optuna.create_study(direction='maximize')

study.optimize(objective, n_trials=100, show_progress_bar=True)

print(f'最优参数: {study.best_params}')

print(f'最优CV分数: {study.best_value:.4f}')

# Optuna 可视化

from optuna.visualization.matplotlib import (

    plot_optimization_history, plot_param_importances

)

plot_optimization_history(study)

plot_param_importances(study)

plt.tight_layout()

plt.savefig('optuna_history.png', dpi=200, bbox_inches='tight')


# ══════ 交叉验证 ══════

from sklearn.model_selection import cross_validate, StratifiedKFold

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

scoring = {

    'accuracy': 'accuracy',

    'precision_weighted': 'precision_weighted',

    'recall_weighted': 'recall_weighted',

    'f1_weighted': 'f1_weighted',

    'roc_auc_ovr_weighted': 'roc_auc_ovr_weighted',

}

cv_results = cross_validate(best_model, X_train, y_train,

                            cv=cv, scoring=scoring, return_train_score=True)

for metric, scores in cv_results.items():

    if metric.startswith('test_'):

        name = metric.replace('test_', '')

        print(f'{name}: {scores.mean():.4f} ± {scores.std():.4f}')


# ══════ 特征重要性 ══════

# 从 Pipeline 中提取模型

rf_model = best_model.named_steps['clf']

importances = rf_model.feature_importances_

# 获取特征名（Pipeline 处理后）

feature_names = best_model.named_steps['prep'].get_feature_names_out()

feat_imp = pd.DataFrame({

    'feature': feature_names,

    'importance': importances

}).sort_values('importance', ascending=False)

print(feat_imp.head(15))


# ══════ 特征重要性 ══════

from sklearn.inspection import permutation_importance

perm_imp = permutation_importance(

    best_model, X_test, y_test,

    n_repeats=10, random_state=42, n_jobs=-1

)

perm_df = pd.DataFrame({

    'feature': feature_names if hasattr(best_model, 'named_steps') else X.columns,

    'importance_mean': perm_imp.importances_mean,

    'importance_std': perm_imp.importances_std

}).sort_values('importance_mean', ascending=False)


# ══════ 未知章节 ══════

import shap

# 对 Pipeline，先 transform 再用 TreeExplainer

X_test_transformed = best_model.named_steps['prep'].transform(X_test)

rf_model = best_model.named_steps['clf']

explainer = shap.TreeExplainer(rf_model)

shap_values = explainer.shap_values(X_test_transformed)

# Summary plot（全局特征重要性）

fig, ax = plt.subplots(figsize=(5.5, 6))

shap.summary_plot(shap_values, X_test_transformed,

                  feature_names=feature_names, show=False)

plt.tight_layout()

plt.savefig('shap_summary.png', dpi=200, bbox_inches='tight')

# Bar plot（平均绝对 SHAP 值）

shap.summary_plot(shap_values, X_test_transformed,

                  feature_names=feature_names, plot_type='bar', show=False)


# ══════ ML 可视化模板 ══════

def plot_feature_importance(feat_df, top_n=15, title='特征重要性'):

    """feat_df: DataFrame with 'feature' and 'importance' columns"""

    top = feat_df.head(top_n).sort_values('importance')

    fig, ax = plt.subplots(figsize=(5.5, 0.35 * top_n))

    colors = ['#C44E52' if v >= top['importance'].quantile(0.75)

              else '#4C72B0' for v in top['importance']]

    ax.barh(top['feature'], top['importance'], color=colors, edgecolor='white')

    ax.set_xlabel('重要性')

    ax.set_title(title)

    for spine in ['top', 'right']:

        ax.spines[spine].set_visible(False)

    plt.tight_layout()

    return fig, ax


# ══════ 未知章节 ══════

from sklearn.metrics import ConfusionMatrixDisplay

def plot_confusion(y_true, y_pred, labels=None, title='混淆矩阵'):

    fig, ax = plt.subplots(figsize=(5, 4.5))

    ConfusionMatrixDisplay.from_predictions(

        y_true, y_pred, display_labels=labels,

        cmap='Blues', ax=ax, colorbar=False,

        text_kw={'fontsize': 10}

    )

    ax.set_title(title)

    ax.set_xlabel('预测类别')

    ax.set_ylabel('真实类别')

    plt.tight_layout()

    return fig, ax


# ══════ 未知章节 ══════

from sklearn.model_selection import learning_curve

def plot_learning_curve(estimator, X, y, title='学习曲线', cv=5):

    train_sizes, train_scores, val_scores = learning_curve(

        estimator, X, y, cv=cv,

        train_sizes=np.linspace(0.1, 1.0, 10),

        scoring='accuracy', n_jobs=-1

    )

    train_mean = train_scores.mean(axis=1)

    train_std = train_scores.std(axis=1)

    val_mean = val_scores.mean(axis=1)

    val_std = val_scores.std(axis=1)

    fig, ax = plt.subplots()

    ax.fill_between(train_sizes, train_mean - train_std,

                    train_mean + train_std, alpha=0.15, color='#4C72B0')

    ax.fill_between(train_sizes, val_mean - val_std,

                    val_mean + val_std, alpha=0.15, color='#C44E52')

    ax.plot(train_sizes, train_mean, 'o-', color='#4C72B0',

            label='训练集', markersize=4)

    ax.plot(train_sizes, val_mean, 'o-', color='#C44E52',

            label='验证集', markersize=4)

    ax.set_xlabel('训练样本数')

    ax.set_ylabel('准确率')

    ax.set_title(title)

    ax.legend(frameon=False)

    plt.tight_layout()

    return fig, ax


# ══════ 其他常用模型（快速切换） ══════

from sklearn.svm import SVC

from sklearn.ensemble import GradientBoostingClassifier

# ── XGBoost ──

try:

    from xgboost import XGBClassifier

    xgb_clf = XGBClassifier(

        n_estimators=200, max_depth=6, learning_rate=0.1,

        subsample=0.8, colsample_bytree=0.8,

        eval_metric='mlogloss', random_state=42, n_jobs=-1

    )

except ImportError:

    pass

# ── SVM ──

svm_clf = Pipeline([

    ('prep', preprocessor),

    ('clf', SVC(kernel='rbf', C=1.0, gamma='scale', probability=True))

])

# ── GBDT ──

gbdt_clf = Pipeline([

    ('prep', preprocessor),

    ('clf', GradientBoostingClassifier(

        n_estimators=200, max_depth=5, learning_rate=0.1, random_state=42

    ))

])

# ── 模型对比 ──

from sklearn.model_selection import cross_val_score

models = {'RF': rf_clf, 'SVM': svm_clf, 'GBDT': gbdt_clf}

for name, model in models.items():

    scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')

    print(f'{name}: {scores.mean():.4f} ± {scores.std():.4f}')


