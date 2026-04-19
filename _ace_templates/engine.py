# -*- coding: utf-8 -*-
"""
_ace_templates/engine.py — ACE 模板引擎统一调度器
入口脚本，根据 config.yaml 中的 project_type 自动路由到对应的 pipeline。

用法：
  python engine.py --config /path/to/project/config.yaml
  python engine.py --init A1 --dest /path/to/project/   # 初始化项目配置
  python engine.py --list                                 # 列出所有模板类型
"""
import sys, os, argparse, shutil, yaml, importlib, json, glob

ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(ENGINE_DIR, 'templates')

# ── 模板类型注册表 ──
TEMPLATE_REGISTRY = {
    'A1_questionnaire': {
        'name': '问卷全套分析',
        'desc': '信度效度+描述统计+相关+差异+回归',
        'pipeline': 'A1_questionnaire.pipeline',
        'frequency': '最高（约40%的单子）',
    },
    'A2_questionnaire_mediation': {
        'name': '问卷+中介/调节效应',
        'desc': 'A1基础上增加Bootstrap中介+交互项调节',
        'pipeline': 'A2_questionnaire_mediation.pipeline',
        'frequency': '高（约20%）',
    },
    'B1_cross_section': {
        'name': '截面实证回归',
        'desc': '描述统计+相关+VIF+递进回归+稳健性+异质性',
        'pipeline': 'B1_cross_section.pipeline',
        'frequency': '中（约15%）',
    },
    'C1_anova': {
        'name': '方差分析',
        'desc': '单/双因素ANOVA+LSD事后比较+三线表',
        'pipeline': 'C1_anova.pipeline',
        'frequency': '中（约10%）',
    },
    'D1_medical': {
        'name': '医学/临床统计',
        'desc': '频数分布+卡方+交叉分析+非参数检验',
        'pipeline': 'D1_medical.pipeline',
        'frequency': '中（约10%）',
    },
}


def list_templates():
    """列出所有可用模板类型"""
    print('\n╔══════════════════════════════════════════════════╗')
    print('║         ACE 模板引擎 — 可用模板类型               ║')
    print('╚══════════════════════════════════════════════════╝\n')
    for key, info in TEMPLATE_REGISTRY.items():
        print(f'  📦 {key}')
        print(f'     名称: {info["name"]}')
        print(f'     功能: {info["desc"]}')
        print(f'     频率: {info["frequency"]}')
        print()


def list_presets():
    """列出所有可用的格式预设"""
    preset_dir = os.path.join(ENGINE_DIR, 'format_presets')
    preset_files = glob.glob(os.path.join(preset_dir, '*.json'))

    print('\n╔══════════════════════════════════════════════════╗')
    print('║         ACE 模板引擎 — 可用格式预设               ║')
    print('╚══════════════════════════════════════════════════╝\n')

    if not preset_files:
        print('  ⚠️ 未找到格式预设文件')
        return

    for f in sorted(preset_files):
        name = os.path.splitext(os.path.basename(f))[0]
        try:
            with open(f, 'r', encoding='utf-8') as fp:
                data = json.load(fp)
            desc = data.get('description', '')
            body = data.get('body', {})
            font_sz = body.get('font_size_pt', '?')
            ls = body.get('line_spacing_multiple', body.get('line_spacing_pt', '?'))
            indent = body.get('first_line_indent_chars', body.get('first_line_indent_cm', '?'))
            print(f'  🎨 {name}')
            print(f'     {desc}')
            print(f'     正文: {font_sz}pt | 行距: {ls}x | 缩进: {indent}字符')
            print()
        except Exception as e:
            print(f'  ⚠️ {name}: 读取失败 ({e})')

    print(f'  共 {len(preset_files)} 套预设，在 config.yaml 中通过 format_preset 字段选择\n')


def init_project(template_type, dest_dir):
    """初始化项目——复制 config_example.yaml 到目标目录"""
    if template_type not in TEMPLATE_REGISTRY:
        print(f'❌ 未知模板类型: {template_type}')
        print(f'   可用: {", ".join(TEMPLATE_REGISTRY.keys())}')
        return

    src = os.path.join(TEMPLATE_DIR, template_type, 'config_example.yaml')
    if not os.path.exists(src):
        print(f'❌ 模板配置不存在: {src}')
        return

    os.makedirs(dest_dir, exist_ok=True)
    dst = os.path.join(dest_dir, 'config.yaml')
    shutil.copy2(src, dst)
    print(f'✅ 已初始化 {TEMPLATE_REGISTRY[template_type]["name"]} 配置到:')
    print(f'   {dst}')
    print(f'\n📝 下一步: 编辑 config.yaml 填入你的变量信息，然后运行:')
    print(f'   python engine.py --config "{dst}"')


def run_from_config(config_path, dry_run=False):
    """根据 config.yaml 的 project_type 自动路由到对应 pipeline"""
    if not os.path.exists(config_path):
        print(f'❌ 配置文件不存在: {config_path}')
        return

    with open(config_path, 'r', encoding='utf-8') as f:
        cfg = yaml.safe_load(f)

    # config 必填字段校验
    from shared.utils import validate_config
    errors = validate_config(cfg)
    if errors:
        print('❌ 配置文件校验失败:')
        for e in errors:
            print(f'   • {e}')
        return

    project_type = cfg.get('project_type', '')
    if project_type not in TEMPLATE_REGISTRY:
        print(f'❌ 未知的 project_type: {project_type}')
        print(f'   可用: {", ".join(TEMPLATE_REGISTRY.keys())}')
        return

    # 格式预设校验
    preset_name = cfg.get('output', {}).get('format_preset', 'thesis_songti')
    preset_dir = os.path.join(ENGINE_DIR, 'format_presets')
    preset_path = os.path.join(preset_dir, f'{preset_name}.json')
    if not os.path.exists(preset_path):
        available = [os.path.splitext(f)[0] for f in os.listdir(preset_dir) if f.endswith('.json')]
        print(f'❌ 格式预设不存在: {preset_name}')
        print(f'   可用预设: {", ".join(sorted(available))}')
        return

    info = TEMPLATE_REGISTRY[project_type]
    print(f'\n🚀 ACE 模板引擎 — {info["name"]}')
    print(f'   项目: {cfg.get("project_name", "未命名")}')
    print(f'   类型: {project_type}')
    print(f'   预设: {preset_name}')
    print('=' * 50)

    if dry_run:
        print('\n✅ 干跑模式：配置校验通过，未执行分析')
        return

    # 动态加载 pipeline
    template_path = os.path.join(TEMPLATE_DIR, project_type)
    sys.path.insert(0, template_path)

    try:
        spec = importlib.util.spec_from_file_location(
            f'pipeline_{project_type}',
            os.path.join(template_path, 'pipeline.py'))
        pipeline_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(pipeline_module)
        pipeline_module.run_pipeline(config_path)
    except FileNotFoundError:
        print(f'❌ 加载 pipeline 失败')
        print(f'   请确认 {template_path}/pipeline.py 存在')
    except Exception as e:
        print(f'❌ 执行出错: {e}')
        import traceback
        traceback.print_exc()
    finally:
        if template_path in sys.path:
            sys.path.remove(template_path)


def auto_detect_type(data_path):
    """自动检测数据类型（启发式）"""
    import pandas as pd

    try:
        df = pd.read_excel(data_path, nrows=5)
    except Exception:
        return None

    cols = [str(c).lower() for c in df.columns]
    col_text = ' '.join(cols)

    # 启发式判断
    if any(k in col_text for k in ['likert', '非常不同意', '不同意', '一般', '同意']):
        return 'A1_questionnaire'
    if any(k in col_text for k in ['中介', 'mediation', '调节', 'moderation']):
        return 'A2_questionnaire_mediation'
    if any(k in col_text for k in ['roe', 'lev', 'size', 'growth', 'tobin']):
        return 'B1_cross_section'
    if any(k in col_text for k in ['实验组', '对照组', 'group', 't0', 't1', '时间点']):
        return 'C1_anova'
    if any(k in col_text for k in ['证型', '中医', '体质', 'tcm', 'vas', 'bmi']):
        return 'D1_medical'

    return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='ACE 模板引擎 — 统一调度器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python engine.py --list                          列出所有模板
  python engine.py --init A1 --dest ./项目名/      初始化配置
  python engine.py --config ./项目名/config.yaml   运行分析
  python engine.py --detect ./项目名/数据.xlsx     自动识别类型
        '''
    )
    parser.add_argument('--config', help='运行：config.yaml 路径')
    parser.add_argument('--init', help='初始化：模板类型（如 A1_questionnaire）')
    parser.add_argument('--dest', help='初始化目标目录', default='.')
    parser.add_argument('--list', action='store_true', help='列出所有模板类型')
    parser.add_argument('--list-presets', action='store_true', help='列出所有格式预设')
    parser.add_argument('--detect', help='自动检测数据类型：数据文件路径')
    parser.add_argument('--dry-run', action='store_true', help='只校验配置不执行分析')

    args = parser.parse_args()

    if args.list:
        list_templates()
    elif args.list_presets:
        list_presets()
    elif args.init:
        init_project(args.init, args.dest)
    elif args.detect:
        detected = auto_detect_type(args.detect)
        if detected:
            print(f'🔍 检测到可能的类型: {detected} ({TEMPLATE_REGISTRY[detected]["name"]})')
        else:
            print('🔍 无法自动识别，请手动选择模板类型')
    elif args.config:
        run_from_config(args.config, dry_run=args.dry_run)
    else:
        parser.print_help()
