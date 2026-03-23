# -*- coding: utf-8 -*-
"""
SPSS SPV 过程文件生成器
通过 SPSS 27 内置 Python 接口（SpssClient）批量执行分析语法并保存 SPV 输出。

使用方式:
    "C:\Program Files\IBM\SPSS\Statistics\27\statisticspython3.bat" spss_spv_generator.py

前置条件:
    - 安装 IBM SPSS Statistics 27+
    - 使用 SPSS 自带的 statisticspython3.bat 执行（非系统 Python）

踩坑记录:
    - OUTPUT NEW / OUTPUT SAVE: 非 GUI 模式不可用（errLevel 3）
    - SET OLANG=CHINESE: 非 GUI 模式不可用；SpssClient 模式下报 833 错误但不影响结果
    - OMS: 非 GUI 模式下导出 SPV 的唯一可靠方式，但输出为英文标题
    - SpssClient: GUI 模式接口，支持 OUTPUT SAVE，输出为中文标题（推荐）
    - stats.exe -production silent: 可运行语法但无法控制输出保存
    - stats.com -f -type -out: SPSS 27 不支持这些参数

推荐方案:
    优先 SpssClient（中文输出） → 回退 OMS（英文输出但稳定）
"""
import os
import sys


def run_spss_analysis(sav_path, syntax_list, spv_output_path, sav_output_path=None):
    """
    执行 SPSS 分析语法并保存 SPV 输出文件。

    Parameters
    ----------
    sav_path : str
        输入的 .sav 数据文件绝对路径
    syntax_list : list[str]
        SPSS 语法字符串列表，按顺序执行
    spv_output_path : str
        输出 .spv 文件的绝对路径
    sav_output_path : str, optional
        如需保存修改后的数据（如含预测概率），指定 .sav 输出路径

    Returns
    -------
    bool
        是否成功

    Example
    -------
    >>> syntax = [
    ...     "LOGISTIC REGRESSION VARIABLES 分组 /METHOD=ENTER x1 /PRINT=CI(95).",
    ...     "ROC x1 BY 分组 (1) /PLOT=CURVE(REFERENCE) /PRINT=SE COORDINATES.",
    ... ]
    >>> run_spss_analysis('data.sav', syntax, 'output.spv')
    """
    sav_path = os.path.abspath(sav_path).replace('\\', '/')
    spv_output_path = os.path.abspath(spv_output_path).replace('\\', '/')
    if sav_output_path:
        sav_output_path = os.path.abspath(sav_output_path).replace('\\', '/')

    os.makedirs(os.path.dirname(spv_output_path), exist_ok=True)

    # ── 方案一：SpssClient（支持中文输出，推荐） ──
    try:
        import SpssClient
        SpssClient.StartClient()
        try:
            SpssClient.RunSyntax(f"GET FILE='{sav_path}'.")
            for syntax in syntax_list:
                SpssClient.RunSyntax(syntax)
            SpssClient.RunSyntax(f"OUTPUT SAVE OUTFILE='{spv_output_path}'.")
            if sav_output_path:
                SpssClient.RunSyntax(f"SAVE OUTFILE='{sav_output_path}'.")
            print(f'[SpssClient] SPV 已保存: {spv_output_path}')
            if sav_output_path:
                print(f'[SpssClient] SAV 已保存: {sav_output_path}')
            return True
        finally:
            try:
                SpssClient.StopClient()
            except:
                pass
    except Exception as e:
        print(f'[SpssClient] 失败: {e}')
        print('[SpssClient] 回退到 OMS 方案...')

    # ── 方案二：spss.Submit + OMS（英文输出，但稳定） ──
    try:
        import spss
        spss.Submit(f"GET FILE='{sav_path}'.")

        # OMS 捕获所有输出到 SPV
        spss.Submit(f"""OMS /SELECT ALL
  /DESTINATION FORMAT=SPV OUTFILE='{spv_output_path}'
  /TAG='spv_all'.""")

        for syntax in syntax_list:
            spss.Submit(syntax)

        spss.Submit("OMSEND TAG='spv_all'.")

        if sav_output_path:
            spss.Submit(f"SAVE OUTFILE='{sav_output_path}'.")

        print(f'[OMS] SPV 已保存: {spv_output_path}')
        if sav_output_path:
            print(f'[OMS] SAV 已保存: {sav_output_path}')
        return True
    except Exception as e:
        print(f'[OMS] 也失败了: {e}')
        return False


# ══════ 示例：Logistic 回归 + ROC 分析 ══════
if __name__ == '__main__':
    BASE = os.path.dirname(os.path.abspath(__file__))

    # --- 自定义区域（修改以下内容适配不同项目） ---
    SAV_FILE = os.path.join(BASE, '数据分析.sav')
    OUT_DIR  = os.path.join(BASE, '交付成果')
    SPV_FILE = os.path.join(OUT_DIR, 'SPSS分析完整过程.spv')
    SAV_OUT  = os.path.join(OUT_DIR, '含预测概率的数据.sav')

    DV = '分组'  # 因变量
    # 单因素候选自变量
    UNI_VARS = ['VLTR', 'VLLR', 'VLHR', 'A1BR', 'NA1R', 'HTR',
                '白细胞', '单核细胞', '高密度', '低密度', '载脂', '白蛋白',
                'WHR', '性别', '吸烟', '二聚体']
    # 单因素显著变量（P<0.05，先用Python跑出来）
    SIG_VARS = ['A1BR', 'NA1R', '白细胞', '单核细胞', '高密度', '低密度',
                '载脂', '白蛋白', 'WHR', '性别', '吸烟', '二聚体']
    # 最终独立因素（多因素逐步回归后保留的）
    FINAL_VARS = ['低密度', 'WHR', '性别', '二聚体']
    # --- 自定义区域结束 ---

    syntax_list = []

    # 1. 单因素 Logistic 回归
    for v in UNI_VARS:
        syntax_list.append(
            f"LOGISTIC REGRESSION VARIABLES {DV}\n"
            f"  /METHOD=ENTER {v}\n"
            f"  /PRINT=CI(95)\n"
            f"  /CRITERIA=PIN(0.05) POUT(0.10) ITERATE(20) CUT(0.5)."
        )

    # 2. 多因素后退法
    sig_str = ' '.join(SIG_VARS)
    syntax_list.append(
        f"LOGISTIC REGRESSION VARIABLES {DV}\n"
        f"  /METHOD=BSTEP(WALD) {sig_str}\n"
        f"  /SAVE=PRED\n"
        f"  /PRINT=CI(95) GOODFIT ITER(1) SUMMARY\n"
        f"  /CRITERIA=PIN(0.05) POUT(0.10) ITERATE(20) CUT(0.5)."
    )

    # 3. 最终模型验证
    final_str = ' '.join(FINAL_VARS)
    syntax_list.append(
        f"LOGISTIC REGRESSION VARIABLES {DV}\n"
        f"  /METHOD=ENTER {final_str}\n"
        f"  /PRINT=CI(95) GOODFIT SUMMARY\n"
        f"  /CRITERIA=PIN(0.05) POUT(0.10) ITERATE(20) CUT(0.5)."
    )

    # 4. ROC 曲线
    roc_vars = ' '.join(FINAL_VARS) + ' PRE_1'
    syntax_list.append(
        f"ROC {roc_vars} BY {DV} (1)\n"
        f"  /PLOT=CURVE(REFERENCE)\n"
        f"  /PRINT=SE COORDINATES\n"
        f"  /CRITERIA=CUTOFF(INCLUDE) TESTPOS(LARGE) DISTRIBUTION(FREE) CI(95)."
    )

    run_spss_analysis(SAV_FILE, syntax_list, SPV_FILE, SAV_OUT)
