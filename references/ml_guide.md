# 机器学习建模指南（按需加载）

> 本文件从 SKILL.md 拆出，包含机器学习建模模块（随机森林、XGBoost、调参、SHAP 等）。
> 仅在涉及机器学习任务时加载。

---

## 九、机器学习建模模块

> 📦 代码见 `code_library/ml_pipeline.py`

### 9.1 环境与依赖

- 依赖库：`scikit-learn`, `shap`, `optuna`, `xgboost`, `matplotlib`
- 流程：数据预处理 → 特征工程 → 模型训练 → 调参 → 评估 → 特征重要性分析


### 9.2 随机森林分类

> 📦 代码见 `code_library/ml_pipeline.py`


### 9.3 随机森林回归

> 📦 代码见 `code_library/ml_pipeline.py`


### 9.4 超参调优

#### GridSearchCV（小参数空间，穷举）

> 📦 代码见 `code_library/ml_pipeline.py`


#### RandomizedSearchCV（大参数空间，随机采样）

> 📦 代码见 `code_library/ml_pipeline.py`


#### Optuna 贝叶斯调参（推荐，效率最高）

> 📦 代码见 `code_library/ml_pipeline.py`


### 9.5 交叉验证

> 📦 代码见 `code_library/ml_pipeline.py`


### 9.6 特征重要性

#### sklearn 内置

> 📦 代码见 `code_library/ml_pipeline.py`


#### Permutation Importance（更稳健）

> 📦 代码见 `code_library/ml_pipeline.py`


#### SHAP 解释（推荐，可解释性最强）

> 📦 代码见 `code_library/ml_pipeline.py`


### 9.7 ML 可视化模板

#### 特征重要性柱状图

> 📦 代码见 `code_library/ml_pipeline.py`


#### 混淆矩阵热力图

> 📦 代码见 `code_library/ml_pipeline.py`


#### 学习曲线

> 📦 代码见 `code_library/ml_pipeline.py`


#### 多分类 ROC 曲线

> 📦 代码见 `code_library/survey.py`


### 9.8 其他常用模型（快速切换）

> 📦 代码见 `code_library/ml_pipeline.py`


### 9.9 ML 交付物检查清单

- [ ] 数据预处理说明（缺失值、编码、标准化方式）

- [ ] 模型选择理由 + 基线模型性能

- [ ] 超参调优过程（搜索空间 + 最优参数）

- [ ] 交叉验证结果（Acc / Precision / Recall / F1 / AUC）

- [ ] 混淆矩阵 + 分类报告

- [ ] 特征重要性排序（Top 15）

- [ ] SHAP 解释图（如客户需要可解释性）

- [ ] 学习曲线（判断过拟合/欠拟合）

---