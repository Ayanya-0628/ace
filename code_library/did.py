# -*- coding: utf-8 -*-
# ace 代码库: did.py
# 从 SKILL.md 提取的可复用代码模板
# 使用时复制对应函数/代码段，替换变量名即可

# ══════ 工具变量 / 2SLS（内生性处理） ══════

from linearmodels.iv import IV2SLS

# 第一阶段：X = π0 + π1*Z + ε

# 第二阶段：Y = β0 + β1*X_hat + ε

model = IV2SLS(dependent=df['Y'], exog=df[controls],

               endog=df['X'], instruments=df['Z']).fit()

# 检查：第一阶段F>10，Sargan过度识别检验


