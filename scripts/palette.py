#!/usr/bin/env python3
"""配色方案与各工具的配色输出（Mermaid / draw.io / CSS / 图表代码）。

<方案> 可省略，省略时用全局默认方案（见 DEFAULT_SCHEME）。

用法:
  palette.py types                              列出图型（按分类）及其 Mermaid 图型
  palette.py schemes                            列出全部方案，标出默认
  palette.py show [方案]                        方案解析后的全部 token（JSON）
  palette.py roles <type> [方案]                角色 -> 填充 / 描边 / 字色
  palette.py mermaid <type> [方案] [--body F] [--init] [--md]
                                                Mermaid 配置 + 图头 + 正文 + classDef
                                                F = 正文文件（图头可有可无，有则沿用；'-' 读标准输入）
                                                --init: 输出 %%{init}%% 指令而不是 YAML frontmatter
                                                --md: 包进 ```mermaid 围栏；桑基图节点写成 英文|中文 时
                                                      在围栏下面附中英对照表
  palette.py drawio <type> [方案]               每个角色的 draw.io style 字符串
  palette.py css [方案|type]                    CSS 变量（HTML / SVG 输出用），附 diagram-design 角色一组
  palette.py chart [方案|type]                  图表代码用的 JSON 色表（matplotlib / ECharts / Vega）；
                                                `nodes` = 分类色加深到和页面拉开的版本
  palette.py check [方案 ...]                   结构校验 + 每个角色字对填充的对比度
"""
import colorsys
import csv
import json
import re
import sys

# ---------------------------------------------------------------------------
# 颜色工具
# ---------------------------------------------------------------------------


def toRgb(color):
    """hex 转 (r, g, b)。

    参数:
        color: '#RRGGBB'
    返回:
        0–255 的三元组
    """
    h = color.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def toHex(rgb):
    """(r, g, b) 转大写 hex，分量超界时截断。

    参数:
        rgb: 三元组，可以是小数
    返回:
        '#RRGGBB'
    """
    return '#' + ''.join(f'{max(0, min(255, round(c))):02X}' for c in rgb)


def mix(a, b, t):
    """把 a 向 b 混合 t。

    参数:
        a: 起始色
        b: 目标色
        t: 比例，0 为 a，1 为 b
    返回:
        混合后的 hex
    """
    ra, rb = toRgb(a), toRgb(b)
    return toHex(tuple(ra[i] + (rb[i] - ra[i]) * t for i in range(3)))


def tint(color, t):
    """向白混合 t。"""
    return mix(color, '#FFFFFF', t)


def shade(color, t):
    """向黑混合 t。"""
    return mix(color, '#000000', t)


def luminance(color):
    """WCAG 相对亮度。

    参数:
        color: hex
    返回:
        0–1
    """
    def channel(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4

    r, g, b = toRgb(color)
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def contrast(a, b):
    """WCAG 对比度。

    参数:
        a: hex
        b: hex
    返回:
        ≥1 的比值
    """
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def toHsl(color):
    """hex 转 (h, s, l)，三个分量都在 0–1。"""
    r, g, b = (v / 255 for v in toRgb(color))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return h, s, l


def fromHsl(h, s, l):
    """(h, s, l) 转 hex，三个分量都在 0–1。"""
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return toHex((r * 255, g * 255, b * 255))


def deepen(color, l=0.30, s_min=0.30, s_max=0.70):
    """同色相加深：保留色相，饱和度夹到区间，明度压到 l。

    参数:
        color: 起始色
        l: 目标明度
        s_min: 饱和度下限
        s_max: 饱和度上限
    返回:
        加深后的 hex
    """
    h, s, _ = toHsl(color)
    return fromHsl(h, min(max(s, s_min), s_max), l)


def isDark(color):
    """亮度低于 0.22 算深色（深色填充上用白字）。"""
    return luminance(color) < 0.22


def isApart(a, b):
    """两色拉得开：明暗对比 ≥1.5，或色相差 ≥40° 且两者都有饱和度，或一灰一彩。

    参数:
        a: hex
        b: hex
    返回:
        bool
    """
    # 明暗差够大直接算拉开
    if contrast(a, b) >= 1.5:
        return True
    ha, sa, _ = toHsl(a)
    hb, sb, _ = toHsl(b)
    # 一灰一彩也算拉开
    if abs(sa - sb) >= 0.4:
        return True
    # 都有饱和度时看色相差
    d = abs(ha - hb) * 360
    d = min(d, 360 - d)
    return d >= 40 and sa >= 0.25 and sb >= 0.25


def readable(fill, preferred, fallbacks, need=4.5):
    """字色：首选色够 need 就用它，否则按顺序取第一个够的备选，再不行取白 / 黑里够的，最后取对比最高的。

    参数:
        fill: 填充色
        preferred: 首选字色
        fallbacks: 备选字色列表
        need: 最低对比度
    返回:
        字色 hex
    """
    # 首选够用直接返回
    if contrast(fill, preferred) >= need:
        return preferred
    # 备选里取第一个够用的
    for c in fallbacks:
        if contrast(fill, c) >= need:
            return c
    # 白 / 黑兜底
    for c in ('#FFFFFF', '#000000'):
        if contrast(fill, c) >= need:
            return c
    # 全不够时取对比最高的
    pool = [preferred] + list(fallbacks) + ['#FFFFFF', '#000000']
    return max(pool, key=lambda c: contrast(fill, c))


def readableOnSolid(fill, text):
    """实色块上的短标签字色：先试白 3:1，再试黑，最后正文色。"""
    for c in ('#FFFFFF', '#111111'):
        if contrast(fill, c) >= 3.0:
            return c
    return readable(fill, text, ['#FFFFFF', '#111111'], 3.0)


def standOut(color, bg, need):
    """把颜色向页面底色的反方向推，直到对底对比度 ≥ need。

    参数:
        color: 起始色
        bg: 页面底色
        need: 最低对比度
    返回:
        调整后的 hex
    """
    toward = '#000000' if luminance(bg) > 0.5 else '#FFFFFF'
    while contrast(color, bg) < need:
        color = mix(color, toward, 0.06)
    return color


def fitLabels(colors, cands, need=3.0):
    """给一组实色块选同一个标签色，再把对比不够的块推到够为止。

    参数:
        colors: 实色块列表
        cands: 候选标签色
        need: 最低对比度
    返回:
        (标签色, 调整后的色块列表)
    """
    # 取最差情况最好的候选
    best = max(cands, key=lambda t: min(contrast(c, t) for c in colors))
    away = '#FFFFFF' if luminance(best) < 0.5 else '#000000'
    fixed = []
    # 逐个把不够的块往反方向推
    for c in colors:
        while contrast(c, best) < need:
            c = mix(c, away, 0.06)
        fixed.append(c)
    return best, fixed


# ---------------------------------------------------------------------------
# 方案
#   slots 四个槽的语义：
#     0 = 主体 / 处理 / 任务 / 类   1 = 开始结束 / 次要 / 接口 / 库
#     2 = 数据 / 文档 / 枚举 / 制品  3 = 判断 / 网关 / 参与者 / 约束
#   槽里写 'primary' 表示这个槽让给主色：填充用主色的浅调，描边和字用主色
#   extra = 同一方案里的附加色，只进系列色
#   描边、槽字色、soft、系列色、渐层都由 resolveScheme 派生
# ---------------------------------------------------------------------------

STATE = {'ok': '#4AB777', 'warn': '#E8A35D', 'bad': '#E35144', 'info': '#516DF6', 'done': '#BBBBBB'}

DEFAULT_SCHEME = 'macaron'

SCHEMES = {
    'macaron': dict(
        name='马卡龙', mood='薰衣草 / 蜜桃 / 薄荷 / 杏，宝蓝强调；通用默认',
        bg='#FFFFFF', text='#33384A', line='#3B6FC2', primary='#3B6FC2',
        slots=['#D2D6F1', '#FBDBD1', '#D8F0ED', '#F6DEB6'], extra=['#DEE7CD']),
    'cotton': dict(
        name='棉糖', mood='粉蓝 / 粉红 / 粉绿 / 鹅黄，灰线，钢蓝强调',
        bg='#FFFFFF', text='#333333', line='#909090', primary='#1B6EBB',
        slots=['#C8E2FA', '#EDD2D6', '#DDEFD9', '#F0DA9D']),
    'mist': dict(
        name='薄雾', mood='淡蓝 / 淡绿 / 杏 / 淡紫，灰绿字，青蓝强调',
        bg='#FFFFFF', text='#3A4A40', line='#BABFB8', primary='#248AB2',
        slots=['#CEEAF5', '#CEE0CA', '#FCE8D0', '#E3D7EC']),
    'morandi': dict(
        name='莫兰迪', mood='灰绿 / 杏 / 淡紫 / 淡青，橄榄强调',
        bg='#FFFFFF', text='#3E4A3D', line='#B4B5A7', primary='#5E7A55',
        slots=['#E4F5DA', '#F7D4B5', '#D2D6F8', '#DBF5F5'], extra=['#F9DCDB', '#B9E9E7']),
    'cream': dict(
        name='奶油', mood='奶油 / 卡其 / 淡绿 / 米灰，橄榄棕强调',
        bg='#FFFFFE', text='#5A4E3A', line='#C4BCA6', primary='#8C7A55',
        slots=['#FDEED4', '#E0D3BA', '#DAE9D9', '#C4BCA6']),
    'pebble': dict(
        name='鹅卵石', mood='蓝灰 / 藕粉 / 浅灰，石墨强调，冷灰底',
        bg='#F9FBFC', text='#3C454B', line='#8B9297', primary='#5F6C72',
        slots=['#BCCBCF', '#DDC1CE', '#DCE0E3', '#8B9297']),
    'sage': dict(
        name='鼠尾草', mood='鼠尾草绿四阶，大地色系列，白底',
        bg='#FFFFFF', text='#30473D', line='#3D4D46', primary='#38755B',
        slots=['#6B9080', '#A4C3B2', '#CCE3DE', '#F6FFF8'],
        extra=['#748EAF', '#AFA57B', '#C19D5F', '#A87365', '#9B8867']),
    'candy': dict(
        name='糖果', mood='薰衣草 / 长春花 / 青 / 粉红，靛蓝强调',
        bg='#FAFAFA', text='#2E2F45', line='#A7AFF2', primary='#202DB6',
        slots=['#C7CBF5', '#7B87EC', '#BAEAEB', '#F4BEDB'], extra=['#B0E28F']),
    'slate': dict(
        name='石板珊瑚', mood='石板蓝 + 珊瑚红，暖白底',
        bg='#FFFEFC', text='#2A3346', line='#8B929E', primary='#3D4B67',
        slots=['#E7EAF0', 'primary', '#FBE2E3', '#EB6E72']),
    'moss': dict(
        name='苔藓', mood='苔绿 / 灰绿 / 奶黄，深苔强调，暖白底',
        bg='#FCFCF8', text='#1F3C23', line='#9DA59A', primary='#1F3C23',
        slots=['#E7EEE0', 'primary', '#D0D9C8', '#FFF4CF'], extra=['#828B7E']),
    'latte': dict(
        name='拿铁', mood='杏黄 / 薄荷 / 琥珀，炭灰强调',
        bg='#FEFEFE', text='#3B3D4B', line='#BFC3C6', primary='#3B3D4B',
        slots=['#FBE2B4', 'primary', '#C5E0DA', '#F4B246'], extra=['#E6BCBD', '#F5EBDF']),
    'blush': dict(
        name='胭脂', mood='粉 / 珊瑚 / 米粉，灰紫强调，暖粉底',
        bg='#FFF7F5', text='#5A5A70', line='#F9B6AE', primary='#7D7D98',
        slots=['#F6DAD7', '#F37464', '#FBE9E6', '#F9B6AE']),
}


def _slotText(fill, text):
    """槽字色：深填充用白；浅填充同色相加深到 4.5:1；中间调加深不到时白字够 3:1 就用白，否则正文色。"""
    # 深填充直接白字
    if isDark(fill):
        return '#FFFFFF'
    # 浅填充按同色相逐级加深
    for l in (0.26, 0.22, 0.18, 0.14):
        c = deepen(fill, l=l)
        if contrast(fill, c) >= 4.5:
            return c
    # 中间调退到白字 3:1
    if contrast(fill, '#FFFFFF') >= 3.0:
        return '#FFFFFF'
    return text


def _buildSeries(slot_fills, extras, primary, bg):
    """系列色：槽填充 + 附加色（去主色、去近白），不足 6 个用槽填充加深 22% 补。

    参数:
        slot_fills: 四个槽的填充
        extras: 方案附加色
        primary: 主色（排除）
        bg: 页面底色
    返回:
        6–8 个 hex
    """
    out = []
    # 槽填充和附加色按顺序收，去重、去主色、去近白
    for c in list(slot_fills) + list(extras):
        if c.upper() == primary.upper() or c.upper() in (x.upper() for x in out):
            continue
        if contrast(c, bg) < 1.08:
            continue
        out.append(c)
    # 不足 6 个用槽填充的加深版补
    i = 0
    while len(out) < 6 and i < len(slot_fills):
        c = shade(slot_fills[i], 0.22)
        if c.upper() not in (x.upper() for x in out) and c.upper() != primary.upper():
            out.append(c)
        i += 1
    return out[:8]


def resolveScheme(sid):
    """按派生规则把方案展开成完整 token。

    参数:
        sid: 方案 id
    返回:
        含 id / bg / surface / text / muted / line / border / primary / onPrimary / slots / series /
        soft / accent / ramp / note / state 的 dict
    抛出:
        SystemExit: 方案不存在
    """
    if sid not in SCHEMES:
        raise SystemExit(f'方案不存在：{sid}；执行 `palette.py schemes` 查看可用方案')
    spec = SCHEMES[sid]
    bg, text, primary = spec['bg'], spec['text'], spec['primary']
    s = dict(id=sid, name=spec['name'], mood=spec['mood'], bg=bg, surface='#FFFFFF', text=text, primary=primary)
    # 主色上的字：白够 3:1 就用白
    s['onPrimary'] = readableOnSolid(primary, text)
    # 槽：'primary' 槽取主色浅调，其余按填充派生描边和字色
    slots = []
    for f in spec['slots']:
        if f == 'primary':
            slots.append((mix(primary, bg, 0.72), primary, primary))
            continue
        stroke = f if isDark(f) else shade(f, 0.30)
        slots.append((f, stroke, _slotText(f, text)))
    s['slots'] = slots
    # 连线对底 ≥3:1，描边 ≥2:1
    s['line'] = standOut(spec['line'], bg, 3.0)
    s['border'] = standOut(spec.get('border', spec['line']), bg, 2.0)
    # soft 容器从描边色派生，对底至少 1.1:1
    soft = mix(s['border'], bg, 0.90)
    while contrast(soft, bg) < 1.10:
        soft = mix(soft, s['border'], 0.08)
    s['soft'] = soft
    # 弱化色、主色浅调、渐层、便签、状态色
    s['muted'] = mix(text, bg, 0.45)
    s['accent'] = mix(primary, bg, 0.72)
    s['ramp'] = [mix(primary, bg, t) for t in (0.85, 0.65, 0.45, 0.25, 0.0)]
    note_fill = mix('#FFF4C2', bg, 0.2)
    s['note'] = (note_fill, shade(note_fill, 0.35), readable(note_fill, text, ['#111111']))
    s['state'] = dict(STATE)
    # 系列色从槽色同源派生
    s['series'] = _buildSeries([f for f, _, _ in slots], spec.get('extra', []), primary, bg)
    return s


def paint(s, key):
    """把 paint key 解析成 (填充, 描边, 字色)。

    参数:
        s: resolveScheme 的结果
        key: primary / accent / slotN / surface / soft / boundary / muted / dark / note /
             ok / warn / bad / info / done / series:N / solid:N / ramp:N
    返回:
        三元组
    抛出:
        KeyError: key 不认识
    """
    fallbacks = [s['text'], '#FFFFFF', '#111111']
    if key.startswith('slot'):
        return s['slots'][int(key[4:])]
    if key == 'primary':
        return (s['primary'], s['primary'], s['onPrimary'])
    if key == 'accent':
        return (s['accent'], s['primary'], readable(s['accent'], s['text'], fallbacks))
    if key == 'surface':
        return (s['surface'], s['border'], s['text'])
    if key == 'soft':
        return (s['soft'], s['border'], s['text'])
    if key == 'boundary':
        return (s['bg'], s['border'], s['text'])
    if key == 'muted':
        f = mix(s['muted'], s['bg'], 0.85)
        return (f, s['muted'], readable(f, s['text'], fallbacks))
    if key == 'dark':
        return (s['text'], s['text'], s['bg'])
    if key == 'note':
        return s['note']
    if key in s['state']:
        c = s['state'][key]
        f = mix(c, s['bg'], 0.82)
        return (f, c, readable(f, s['text'], fallbacks))
    if key.startswith('series:'):
        c = s['series'][int(key[7:]) % len(s['series'])]
        f = mix(c, s['bg'], 0.80)
        return (f, c, readable(f, s['text'], fallbacks))
    if key.startswith('solid:'):
        c = s['series'][int(key[6:]) % len(s['series'])]
        return (c, c, readableOnSolid(c, s['text']))
    if key.startswith('ramp:'):
        f = s['ramp'][int(key[5:])]
        return (f, s['primary'], readable(f, s['text'], fallbacks))
    raise KeyError(key)


# ---------------------------------------------------------------------------
# 图型：角色（css class、说明、paint key、是否虚线）
# ---------------------------------------------------------------------------


def defineRoles(*items):
    """把 (class, 说明, paint[, 'dashed']) 元组列表转成角色 dict 列表。"""
    return [dict(cls=it[0], label=it[1], paint=it[2], dashed=len(it) > 3) for it in items]


TYPES = {
    # 思考梳理 ---------------------------------------------------------------
    'mindmap': dict(name='思维导图', cat='thinking', kind='mindmap',
        roles=defineRoles(('root', '中心主题', 'primary'), ('b1', '分支 1', 'solid:0'), ('b2', '分支 2', 'solid:1'),
                          ('b3', '分支 3', 'solid:2'), ('b4', '分支 4', 'solid:3'), ('b5', '分支 5', 'solid:4'),
                          ('b6', '分支 6', 'solid:5'))),
    'org': dict(name='树形图 / 组织结构图', cat='thinking', kind='flow',
        roles=defineRoles(('top', '顶层节点', 'primary'), ('l2', '第二层', 'slot0'), ('l3', '第三层及以下', 'surface'),
                          ('aux', '虚线汇报 / 助理', 'muted', 'dashed'))),
    'fishbone': dict(name='鱼骨图', cat='thinking', kind='ishikawa',
        roles=defineRoles(('head', '问题（鱼头）', 'slot3'), ('cat', '原因大类', 'slot0'), ('cause', '具体原因', 'surface'),
                          ('verified', '已验证的根因', 'bad'))),
    'concept': dict(name='概念图', cat='thinking', kind='flow',
        roles=defineRoles(('core', '核心概念', 'primary'), ('concept', '一级概念', 'slot0'), ('sub', '二级概念', 'surface'),
                          ('example', '例子 / 实例', 'slot2'))),
    'affinity': dict(name='亲和图', cat='thinking', kind='flow',
        roles=defineRoles(('g1', '分组 1 便签', 'series:0'), ('g2', '分组 2 便签', 'series:1'), ('g3', '分组 3 便签', 'series:2'),
                          ('g4', '分组 4 便签', 'series:3'), ('title', '分组标题', 'primary'))),
    # 流程行为 ---------------------------------------------------------------
    'flowchart': dict(name='流程图', cat='flow', kind='flow',
        roles=defineRoles(('startend', '开始 / 结束', 'slot1'), ('process', '处理步骤', 'slot0'), ('decision', '判断', 'slot3'),
                          ('data', '数据 / 文档', 'slot2'), ('key', '关键路径', 'primary'), ('error', '异常分支', 'bad'))),
    'swimlane': dict(name='泳道图', cat='flow', kind='flow',
        roles=defineRoles(('startend', '开始 / 结束', 'slot1'), ('task', '任务', 'slot0'), ('decision', '判断', 'slot3'),
                          ('handoff', '跨泳道交接点', 'primary'), ('lane', '泳道底色', 'soft'))),
    'sequence': dict(name='时序图', cat='flow', kind='sequence',
        roles=defineRoles(('participant', '参与者', 'slot0'), ('activation', '激活条', 'slot2'), ('note', '注释', 'note'),
                          ('frame', 'alt / loop 框', 'surface'))),
    'state': dict(name='状态图', cat='flow', kind='state',
        roles=defineRoles(('normal', '普通状态', 'slot0'), ('active', '进行中', 'primary'), ('ok', '成功终态', 'ok'),
                          ('fail', '失败 / 取消终态', 'bad'), ('composite', '复合状态', 'soft'))),
    'activity': dict(name='活动图（UML）', cat='flow', kind='flow',
        roles=defineRoles(('action', '动作', 'slot0'), ('decision', '判断 / 合并', 'slot3'), ('object', '对象节点', 'slot2'),
                          ('bar', '分叉 / 汇合条、起止点', 'dark'), ('partition', '分区底色', 'soft'))),
    'communication': dict(name='通信图（UML）', cat='flow', kind='flow',
        roles=defineRoles(('object', '对象', 'slot0'), ('actor', '参与者', 'slot3'), ('msg', '消息编号强调', 'primary'))),
    'interaction': dict(name='交互概览图（UML）', cat='flow', kind='flow',
        roles=defineRoles(('frame', 'sd / ref 交互帧', 'surface'), ('occurrence', '交互引用', 'slot0'), ('decision', '判断', 'slot3'),
                          ('bar', '起止点', 'dark'))),
    'timing': dict(name='时间图（UML）', cat='flow', kind='drawio',
        roles=defineRoles(('lifeline', '生命线行', 'soft'), ('s1', '状态段 1', 'series:0'), ('s2', '状态段 2', 'series:1'),
                          ('s3', '状态段 3', 'series:2'), ('axis', '时间轴 / 刻度', 'muted'))),
    'journey': dict(name='用户旅程图', cat='product', kind='journey',
        roles=defineRoles(('stage1', '阶段 1', 'series:0'), ('stage2', '阶段 2', 'series:1'), ('stage3', '阶段 3', 'series:2'),
                          ('stage4', '阶段 4', 'series:3'), ('pain', '痛点标注', 'bad'))),
    # 系统结构 ---------------------------------------------------------------
    'c4': dict(name='C4 模型（Context / Container / Component）', cat='structure', kind='c4',
        roles=defineRoles(('person', '人员', 'primary'), ('system', '本系统 / 容器', 'slot0'), ('component', '组件', 'slot2'),
                          ('db', '数据库', 'slot2'), ('external', '外部系统', 'muted'), ('boundary', '边界', 'boundary', 'dashed'))),
    'biz_arch': dict(name='业务架构图', cat='structure', kind='block',
        roles=defineRoles(('channel', '用户触点层', 'primary'), ('domain', '业务域标题', 'slot1'), ('capability', '业务能力', 'slot0'),
                          ('shared', '共享能力 / 中台', 'slot2'), ('band', '分层底色', 'soft'))),
    'app_arch': dict(name='应用架构图', cat='structure', kind='flow',
        roles=defineRoles(('client', '前端 / 渠道应用', 'slot1'), ('service', '服务', 'slot0'), ('infra', '中间件 / 基础服务', 'slot2'),
                          ('external', '外部系统', 'muted'), ('layer', '分层容器', 'soft', 'dashed'))),
    'data_arch': dict(name='数据架构图', cat='structure', kind='flow',
        roles=defineRoles(('source', '数据源', 'slot1'), ('compute', '采集 / 计算', 'slot0'), ('store', '存储', 'slot2'),
                          ('consume', '数据消费 / 报表', 'slot3'), ('layer', '分层容器', 'soft', 'dashed'))),
    'tech_arch': dict(name='技术架构图', cat='structure', kind='block',
        roles=defineRoles(('layer', '层名称', 'primary'), ('item', '技术组件', 'surface'), ('cross', '横切能力（日志 / 监控 / CI）', 'slot3'),
                          ('highlight', '本次新增 / 重点', 'slot1'))),
    'deploy_arch': dict(name='部署架构图', cat='structure', kind='flow',
        roles=defineRoles(('zone', '地域 / 可用区 / VPC', 'boundary', 'dashed'), ('subnet', '子网 / 集群', 'soft'),
                          ('node', '计算节点 / Pod', 'slot0'), ('gateway', '负载均衡 / 网关', 'slot1'), ('db', '数据库 / 存储', 'slot2'),
                          ('security', '安全设备', 'bad'))),
    'network': dict(name='网络拓扑图', cat='structure', kind='flow',
        roles=defineRoles(('internet', '外网', 'muted'), ('dmz', 'DMZ 区', 'warn'), ('intranet', '内网区', 'soft'),
                          ('device', '网络设备', 'slot0'), ('server', '服务器', 'surface'), ('security', '防火墙 / WAF', 'bad'))),
    # 建模设计 ---------------------------------------------------------------
    'class': dict(name='类图', cat='modeling', kind='class',
        roles=defineRoles(('cls', '普通类', 'slot0'), ('iface', '接口', 'slot1'), ('enum', '枚举', 'slot2'),
                          ('abstract', '抽象类 / 约束', 'slot0', 'dashed'), ('focus', '本次改动的类', 'primary'))),
    'er': dict(name='ER 图', cat='modeling', kind='er',
        roles=defineRoles(('entity', '实体', 'slot0'), ('core', '核心实体', 'accent'), ('link', '中间表', 'slot2'))),
    'usecase': dict(name='用例图', cat='modeling', kind='usecase',
        roles=defineRoles(('person', '参与者', 'slot3'), ('uc', '用例', 'slot0'), ('ext', '扩展 / 包含用例', 'slot1'),
                          ('boundary', '系统边界', 'boundary', 'dashed'))),
    'object': dict(name='对象图（UML）', cat='modeling', kind='class',
        roles=defineRoles(('obj', '对象', 'slot0'), ('focus', '关注的对象', 'primary'), ('value', '值对象', 'slot2'))),
    'component': dict(name='组件图（UML）', cat='modeling', kind='flow',
        roles=defineRoles(('comp', '组件', 'slot0'), ('lib', '库', 'slot1'), ('iface', '接口', 'slot3'),
                          ('group', '包 / 子系统', 'soft', 'dashed'))),
    'package': dict(name='包图（UML）', cat='modeling', kind='flow',
        roles=defineRoles(('pkg1', '顶层包', 'ramp:1'), ('pkg2', '子包', 'ramp:0'), ('focus', '关注的包', 'primary'))),
    'uml_deploy': dict(name='部署图（UML）', cat='modeling', kind='flow',
        roles=defineRoles(('device', '设备节点', 'slot0'), ('env', '执行环境', 'slot1'), ('artifact', '制品', 'slot2'),
                          ('zone', '网络边界', 'boundary', 'dashed'))),
    'composite': dict(name='组合结构图（UML）', cat='modeling', kind='flow',
        roles=defineRoles(('frame', '类元边框', 'boundary', 'dashed'), ('part', '部件', 'slot0'), ('port', '端口', 'slot3'))),
    'profile': dict(name='Profile 图（UML）', cat='modeling', kind='class',
        roles=defineRoles(('stereo', '构造型', 'slot1'), ('meta', '元类', 'slot0'), ('tagged', '标记值', 'slot2'))),
    'requirement': dict(name='需求图', cat='product', kind='requirement',
        roles=defineRoles(('req', '需求', 'slot0'), ('element', '设计 / 测试元素', 'slot2'))),
    # 产品设计 ---------------------------------------------------------------
    'ui_flow': dict(name='页面流程图 / 交互流程', cat='product', kind='flow',
        roles=defineRoles(('page', '页面', 'slot0'), ('action', '用户操作', 'slot2'), ('decision', '判断 / 状态分支', 'slot3'),
                          ('entry', '入口 / 出口', 'slot1'), ('annotation', '交互说明', 'note'))),
    'wireframe': dict(name='线框图 / 原型图', cat='product', kind='drawio',
        roles=defineRoles(('canvas', '页面画布', 'surface'), ('block', '占位块 / 图片', 'muted'),
                          ('primaryBtn', '主按钮 / 关键操作', 'primary'), ('component', '组件区块', 'soft'),
                          ('marker', '标注编号 / 说明', 'bad'))),
    'story_map': dict(name='用户故事地图', cat='product', kind='flow',
        roles=defineRoles(('activity', '用户活动（骨架）', 'primary'), ('task', '用户任务', 'slot0'), ('story', '故事卡', 'note'),
                          ('mvp', 'MVP / 本期发布', 'slot3'), ('later', '后续版本', 'muted'))),
    # 计划进度 ---------------------------------------------------------------
    'gantt': dict(name='甘特图', cat='planning', kind='gantt',
        roles=defineRoles(('task', '普通任务', 'slot0'), ('active', '进行中', 'accent'), ('done', '已完成', 'done'),
                          ('crit', '关键路径', 'bad'), ('milestone', '里程碑', 'slot3'), ('section', '分组底色', 'soft'))),
    'timeline': dict(name='时间线', cat='planning', kind='timeline',
        roles=defineRoles(('p1', '时期 1', 'solid:0'), ('p2', '时期 2', 'solid:1'), ('p3', '时期 3', 'solid:2'),
                          ('p4', '时期 4', 'solid:3'), ('p5', '时期 5', 'solid:4'))),
    'roadmap': dict(name='路线图', cat='planning', kind='timeline',
        roles=defineRoles(('now', 'Now（已确定）', 'ramp:4'), ('next', 'Next（规划中）', 'ramp:2'), ('later', 'Later（方向）', 'ramp:0'),
                          ('t1', '主题泳道 1', 'series:0'), ('t2', '主题泳道 2', 'series:1'))),
    'kanban': dict(name='看板', cat='planning', kind='kanban',
        roles=defineRoles(('todo', '待办列', 'solid:0'), ('doing', '进行中列', 'solid:1'), ('review', '测试列', 'solid:2'),
                          ('done', '完成列', 'solid:3'), ('urgent', '高优先级标签', 'bad'))),
    'gitgraph': dict(name='Git 分支图', cat='planning', kind='git',
        roles=defineRoles(('main', 'main 分支', 'solid:0'), ('develop', 'develop 分支', 'solid:1'),
                          ('feature', 'feature 分支', 'solid:2'), ('hotfix', 'hotfix 分支', 'solid:3'))),
    # 数据呈现 ---------------------------------------------------------------
    'bar_line': dict(name='柱状图 / 折线图', cat='data', kind='xychart',
        roles=defineRoles(('s1', '系列 1 / 主系列', 'solid:0'), ('s2', '系列 2', 'solid:1'), ('s3', '系列 3', 'solid:2'),
                          ('axis', '坐标轴 / 网格', 'muted'))),
    'pie': dict(name='饼图 / 环形图', cat='data', kind='pie',
        roles=defineRoles(('p1', '扇区 1', 'solid:0'), ('p2', '扇区 2', 'solid:1'), ('p3', '扇区 3', 'solid:2'),
                          ('p4', '扇区 4', 'solid:3'), ('other', '其他（最后一块）', 'muted'))),
    'quadrant': dict(name='象限图', cat='data', kind='quadrant',
        roles=defineRoles(('q1', '第一象限（右上）', 'ramp:2'), ('q2', '第二象限（左上）', 'ramp:3'),
                          ('q3', '第三象限（左下）', 'ramp:0'), ('q4', '第四象限（右下）', 'ramp:1'), ('point', '数据点', 'primary'))),
    'sankey': dict(name='桑基图', cat='data', kind='sankey',
        roles=defineRoles(('n1', '节点 1', 'solid:0'), ('n2', '节点 2', 'solid:1'), ('n3', '节点 3', 'solid:2'),
                          ('n4', '节点 4', 'solid:3'))),
    'radar': dict(name='雷达图', cat='data', kind='radar',
        roles=defineRoles(('c1', '对象 1', 'solid:0'), ('c2', '对象 2', 'solid:1'), ('c3', '对象 3', 'solid:2'),
                          ('grid', '网格 / 轴', 'muted'))),
    'scatter': dict(name='散点图', cat='data', kind='chart',
        roles=defineRoles(('g1', '分组 1', 'solid:0'), ('g2', '分组 2', 'solid:1'), ('g3', '分组 3', 'solid:2'),
                          ('trend', '趋势线', 'muted'))),
    'distribution': dict(name='直方图 / 箱线图', cat='data', kind='chart',
        roles=defineRoles(('bar', '分布主体', 'primary'), ('median', '中位数 / 均值线', 'slot3'), ('outlier', '离群点', 'bad'),
                          ('axis', '坐标轴 / 网格', 'muted'))),
    'venn': dict(name='韦恩图', cat='data', kind='venn',
        roles=defineRoles(('a', '集合 A', 'solid:0'), ('b', '集合 B', 'solid:1'), ('c', '集合 C', 'solid:2'))),
    'treemap': dict(name='矩形树图', cat='data', kind='treemap',
        roles=defineRoles(('section', '分组', 'ramp:1'), ('leaf', '叶子', 'ramp:0'), ('focus', '重点叶子', 'primary'))),
}

CATS = {
    'thinking': '思考梳理', 'flow': '流程行为', 'structure': '系统结构',
    'modeling': '建模设计', 'product': '产品设计', 'planning': '计划进度', 'data': '数据呈现',
}

FONT = 'PingFang SC, Microsoft YaHei, Noto Sans CJK SC, Source Han Sans SC, sans-serif'

HEADERS = {
    'flow': 'flowchart LR', 'drawio': 'flowchart LR', 'mindmap': 'mindmap', 'ishikawa': 'ishikawa-beta',
    'sequence': 'sequenceDiagram', 'state': 'stateDiagram-v2', 'class': 'classDiagram', 'er': 'erDiagram',
    'usecase': 'usecase-beta', 'journey': 'journey', 'c4': 'C4Container', 'block': 'block-beta',
    'requirement': 'requirementDiagram', 'gantt': 'gantt', 'timeline': 'timeline', 'kanban': 'kanban', 'git': 'gitGraph',
    'xychart': 'xychart-beta', 'pie': 'pie', 'quadrant': 'quadrantChart', 'sankey': 'sankey-beta',
    'radar': 'radar-beta', 'venn': 'venn-beta', 'treemap': 'treemap-beta',
}
HEADER_OVERRIDE = {'swimlane': 'swimlane-beta LR', 'org': 'flowchart TB', 'deploy_arch': 'flowchart TB',
                   'network': 'flowchart TB', 'package': 'flowchart TB', 'activity': 'flowchart TB'}


def roleTable(tid, sid):
    """图型的角色表。

    参数:
        tid: 图型 id
        sid: 方案 id
    返回:
        (方案 token, [(class, 说明, paint, 是否虚线, (填充, 描边, 字色)), ...])
    """
    s = resolveScheme(sid)
    rows = [(r['cls'], r['label'], r['paint'], r['dashed'], paint(s, r['paint'])) for r in TYPES[tid]['roles']]
    return s, rows


# ---------------------------------------------------------------------------
# Mermaid 输出
# ---------------------------------------------------------------------------

SANKEY_NAMES = {}  # 桑基图输出时填入：英文节点名 -> 中文
INIT_STYLE = False  # True 时输出 %%{init}%% 指令而不是 YAML frontmatter

HEADER_RE = re.compile(
    r'^(?:(?:flowchart|graph|swimlane(?:-beta)?)(?:\s+(?:TB|TD|BT|RL|LR))?'
    r'|sequenceDiagram|classDiagram(?:-v2)?|stateDiagram(?:-v2)?|erDiagram|journey|gantt|mindmap|timeline|kanban'
    r'|pie(?:\s+showData)?(?:\s+title\s.*)?|quadrantChart|requirementDiagram|gitGraph(?:\s+(?:LR|TB|BT):?)?'
    r'|C4(?:Context|Container|Component|Dynamic|Deployment)'
    r'|(?:sankey|block|radar|venn|treemap|ishikawa|architecture|usecase)(?:-beta)?'
    r'|xychart(?:-beta)?(?:\s+horizontal)?)\s*$')

C4_ROLES = [('Person', 'person'), ('ComponentDb', 'db'), ('ContainerDb', 'db'), ('SystemDb', 'db'),
            ('ComponentQueue', 'component'), ('ContainerQueue', 'system'), ('SystemQueue', 'system'),
            ('Component', 'component'), ('Container', 'system'), ('System', 'system')]

SANKEY_HINT = (
    '两种改法：\n'
    '  1. 写成 英文|中文（如 Visits|访问）：图里显示英文，加 --md 会在图下面附中英对照表\n'
    '  2. 图里直接显示中文：node $SKILL/scripts/sankey_echarts.js 数据.csv（ECharts 出 SVG / PNG）')


def _frontmatter(theme_vars, extra=None):
    """把主题变量写成 YAML frontmatter 或 %%{init}%% 指令。

    参数:
        theme_vars: themeVariables
        extra: 其他 config 项（如 sankey）
    返回:
        文本
    """
    # init 指令直接序列化成 JSON
    if INIT_STYLE:
        cfg = {'theme': 'base', **(extra or {}), 'themeVariables': theme_vars}
        return '%%{init: ' + json.dumps(cfg, ensure_ascii=False) + '}%%'
    lines = ['---', 'config:', '  theme: base']
    # 其他 config 项最多嵌三层
    if extra:
        for k, v in extra.items():
            lines.append(f'  {k}:')
            for kk, vv in v.items():
                if isinstance(vv, dict):
                    lines.append(f'    {kk}:')
                    for k3, v3 in vv.items():
                        lines.append(f'      "{k3}": "{v3}"')
                else:
                    lines.append(f'    {kk}: {json.dumps(vv, ensure_ascii=False)}')
    # themeVariables 允许一层嵌套（xyChart / radar）
    lines.append('  themeVariables:')
    for k, v in theme_vars.items():
        if isinstance(v, dict):
            lines.append(f'    {k}:')
            for kk, vv in v.items():
                lines.append(f'      {kk}: {json.dumps(vv, ensure_ascii=False)}')
        else:
            lines.append(f'    {k}: {json.dumps(v, ensure_ascii=False)}')
    lines.append('---')
    return '\n'.join(lines)


def _baseVars(s):
    """所有图型共用的主题变量：未挂 class 的节点是中性的，颜色一律由 classDef 决定。"""
    f1, _, _ = s['slots'][1]
    return {
        'fontFamily': FONT, 'background': s['bg'],
        'primaryColor': s['surface'], 'primaryBorderColor': s['border'], 'primaryTextColor': s['text'],
        'nodeTextColor': s['text'],
        'secondaryColor': f1, 'tertiaryColor': s['soft'],
        'lineColor': s['line'], 'textColor': s['text'],
        'clusterBkg': s['soft'], 'clusterBorder': s['border'],
        'edgeLabelBackground': s['bg'], 'titleColor': s['text'],
        'noteBkgColor': s['note'][0], 'noteBorderColor': s['note'][1], 'noteTextColor': s['note'][2],
    }


def _classDefs(rows):
    """角色表转 classDef 行：主色角色描边 2px，虚线角色加 dasharray。"""
    out = []
    for cls, _, p, dashed, (f, st, t) in rows:
        extra = ',stroke-dasharray:5 4' if dashed else ''
        if p in ('primary', 'accent'):
            extra += ',stroke-width:2px'
        out.append(f'classDef {cls} fill:{f},stroke:{st},color:{t}{extra}')
    return out


def _splitBody(body):
    """去掉用户正文里的 frontmatter，返回 (自带图头或 None, 其余正文)。"""
    lines = body.splitlines()
    # 去掉开头的 --- ... --- 块
    if lines and lines[0].strip() == '---':
        end = next((i for i in range(1, len(lines)) if lines[i].strip() == '---'), None)
        if end is not None:
            lines = lines[end + 1:]
    # 第一行非空非注释的内容若是图头就摘出来
    for i, ln in enumerate(lines):
        t = ln.strip()
        if not t or t.startswith('%%'):
            continue
        if HEADER_RE.match(t):
            return t, '\n'.join(lines[:i] + lines[i + 1:])
        break
    return None, '\n'.join(lines)


def _c4Styles(body, rows, s):
    """按 C4 正文里的元素和关系生成 UpdateElementStyle / UpdateRelStyle。"""
    paints = {cls: (f, st, tx) for cls, _, _, _, (f, st, tx) in rows}
    out = []
    # 元素：按宏名映射角色，_Ext 后缀走 external
    for m in re.finditer(r'^\s*(\w+?)(_Ext)?\(\s*(\w+)', body, re.M):
        macro, ext, alias = m.group(1), m.group(2), m.group(3)
        role = next((r for k, r in C4_ROLES if macro == k), None)
        if role is None:
            continue
        f, st, tx = paints['external' if ext else role]
        out.append(f'UpdateElementStyle({alias}, $fontColor="{tx}", $bgColor="{f}", $borderColor="{st}")')
    # 关系（边界没有样式宏，用 Mermaid 默认）
    for m in re.finditer(r'^\s*(?:Bi)?Rel(?:_\w+)?\(\s*(\w+)\s*,\s*(\w+)', body, re.M):
        out.append(f'UpdateRelStyle({m.group(1)}, {m.group(2)}, $textColor="{s["text"]}", $lineColor="{s["line"]}")')
    return out


def _csvField(v):
    """CSV 字段：含逗号或引号时加引号。"""
    return '"' + v.replace('"', '""') + '"' if any(ch in v for ch in ',"') else v


def _parseSankey(body):
    """解析桑基图 CSV 正文，节点可写成 英文|中文。

    参数:
        body: 正文
    返回:
        (ASCII 正文, 节点出现顺序, {英文: 中文})
    抛出:
        SystemExit: 节点名含非 ASCII 字符（Mermaid 词法不认）
    """
    out, nodes, names, bad = [], [], {}, []
    for ln in body.splitlines():
        t = ln.strip()
        # 空行和注释原样保留
        if not t or t.startswith('%%'):
            out.append(ln)
            continue
        row = next(csv.reader([t], skipinitialspace=True))
        fields = []
        # 前两列是节点名，拆 英文|中文，记非 ASCII
        for k, v in enumerate(row):
            v = v.strip()
            if k < 2:
                if '|' in v:
                    en, cn = (x.strip() for x in v.split('|', 1))
                    names.setdefault(en, cn)
                    v = en
                if any(ord(ch) > 126 for ch in v):
                    bad.append(v)
                if v and v not in nodes:
                    nodes.append(v)
            fields.append(_csvField(v))
        out.append(','.join(fields))
    if bad:
        raise SystemExit('桑基图节点名只能用 ASCII 字符（Mermaid 词法限制，加引号也不行），这些不行：'
                         + '、'.join(dict.fromkeys(bad)) + '\n' + SANKEY_HINT)
    return '\n'.join(out), nodes, names


def _mappingTable(names):
    """英文节点名到中文的 Markdown 对照表。"""
    rows = ['| 图中名称 | 中文 |', '|---|---|'] + [f'| {en} | {cn} |' for en, cn in names.items()]
    return '\n'.join(rows)


def _countPieRows(body):
    """数饼图正文里的数据行（"标签" : 数值）。"""
    return len(re.findall(r'^\s*"[^"]*"\s*:\s*[\d.]+', body, re.M))


def emitMermaid(tid, sid, body=None):
    """输出带配色的 Mermaid 代码。

    参数:
        tid: 图型 id
        sid: 方案 id
        body: 正文（可含图头），None 时输出占位
    返回:
        frontmatter + 图头 + 正文 + classDef / 说明
    """
    t = TYPES[tid]
    s, rows = roleTable(tid, sid)
    kind = t['kind']
    v = _baseVars(s)
    tail = []
    series = s['series']
    own_header = None
    # 正文自带图头时沿用
    if body is not None:
        own_header, body = _splitBody(body)

    def label(c):
        return readableOnSolid(c, s['text'])

    if kind in ('flow', 'drawio'):
        tail = _classDefs(rows)
        tail.append('%% 用法：节点 A:::' + rows[0][0] + ' 或 class A,B ' + rows[0][0])
        if kind == 'drawio':
            tail.insert(0, '%% 该图 Mermaid 没有原生类型，优先用 drawio；下面是 flowchart 近似画法的配色')
    elif kind == 'usecase':
        # 用例 / 参与者 / 边界各有专用变量，按角色给默认色；要单独强调再挂 class
        uf, ust, _ = s['slots'][0]
        af, ast, _ = s['slots'][3]
        v.update({'usecaseBkg': uf, 'usecaseBorder': ust, 'usecaseActorBkg': af, 'usecaseActorBorder': ast,
                  'usecaseBoundaryBkg': s['bg'], 'usecaseBoundaryBorder': s['border'],
                  'usecaseIncludeLine': s['line'], 'usecaseExtendLine': s['line']})
        tail = _classDefs(rows)
        tail.append('%% 用法：Order("下单"):::ext、actor Admin("管理员"):::person；systemBoundary 也能挂 :::boundary；class 名不能用 actor 这类关键字')
    elif kind == 'mindmap':
        # 根节点用主色，分支从系列色第 1 个起
        v.update({'git0': s['primary'], 'gitBranchLabel0': s['onPrimary']})
        for i in range(12):
            c = series[i % len(series)]
            v[f'cScale{i + 1}' if i < 11 else 'cScale0'] = c
            v[f'cScaleLabel{i + 1}' if i < 11 else 'cScaleLabel0'] = label(c)
        tail = ['%% 根节点用 git0；第 n 个一级分支用 cScale<n>']
    elif kind in ('timeline', 'kanban', 'radar'):
        # 分段 / 列 / 曲线按出现顺序轮换系列色
        for i in range(12):
            c = series[i % len(series)]
            v[f'cScale{i}'] = c
            v[f'cScaleLabel{i}'] = label(c)
        if kind == 'radar':
            v['radar'] = {'axisColor': s['muted'], 'graticuleColor': mix(s['muted'], s['bg'], 0.5), 'curveOpacity': 0.35}
            tail = ['%% 第 n 条曲线用 cScale<n-1>，曲线不超过 3 条']
        if kind == 'timeline' and tid == 'roadmap':
            for i, c in enumerate(reversed(s['ramp'])):
                v[f'cScale{i}'] = c
                v[f'cScaleLabel{i}'] = readable(c, s['text'], ['#FFFFFF', '#111111'])
            tail = ['%% section 依次为 Now / Next / Later，颜色由深到浅']
    elif kind == 'ishikawa':
        f, st, tx = paint(s, 'slot3')
        v.update({'mainBkg': f, 'lineColor': st, 'textColor': s['text']})
        tail = ['%% 鱼骨图只认 mainBkg（鱼头和大类框）、lineColor、textColor；要给大类分色请用 drawio']
    elif kind == 'sequence':
        # 参与者框取第一个浅色槽，名字用正文色（actor 关键字的人形名字也用它，要能在页面底色上读）
        f0, st0, _ = next((sl for sl in s['slots'] if sl[2] != '#FFFFFF'), s['slots'][0])
        f2, st2, _ = s['slots'][2]
        v.update({
            'actorBkg': f0, 'actorBorder': st0, 'actorTextColor': s['text'], 'actorLineColor': s['muted'],
            'signalColor': s['line'], 'signalTextColor': s['text'],
            'labelBoxBkgColor': s['surface'], 'labelBoxBorderColor': s['border'], 'labelTextColor': s['text'],
            'loopTextColor': s['text'], 'activationBkgColor': f2, 'activationBorderColor': st2,
            'sequenceNumberColor': s['bg'],
        })
        f3, _, _ = s['slots'][3]
        tail = [f'%% 用 box 给一组参与者加底色：box {mix(f3, s["bg"], 0.5)} 外部系统 ... end',
                '%% 参与者是人时用 actor 关键字（小人图形不受 actorBkg 填充影响）']
    elif kind == 'state':
        v.update({'stateBkg': s['slots'][0][0], 'stateLabelColor': s['slots'][0][2],
                  'compositeBackground': s['soft'], 'compositeTitleBackground': s['soft'],
                  'compositeBorder': s['border'], 'transitionColor': s['line'],
                  'transitionLabelColor': s['text'], 'specialStateColor': s['text'],
                  'innerEndBackground': s['text']})
        tail = _classDefs(rows)
        tail.append('%% 用法：class 已支付 ok（classDef 写在状态定义之后）')
    elif kind == 'class':
        v.update({'classText': s['slots'][0][2]})
        tail = _classDefs(rows)
        tail.append('%% 用法：class OrderService:::focus，或 cssClass "PayGateway" iface')
    elif kind == 'er':
        # 关系标签框不要底色；字段行奇偶用 surface / soft
        v.update({'tertiaryColor': s['bg'],
                  'attributeBackgroundColorOdd': s['surface'], 'attributeBackgroundColorEven': s['soft']})
        tail = _classDefs(rows)
        tail.append('%% 用法：ORDERS:::core（实体名后加 :::类名）')
    elif kind == 'journey':
        for i in range(8):
            v[f'fillType{i}'] = paint(s, f'series:{i}')[0]
        v['faceColor'] = s['note'][0]
        tail = ['%% 第 n 个 section 用 fillType<n-1>']
    elif kind == 'c4':
        if body is not None:
            tail = _c4Styles(body, rows, s)
        else:
            tail = ['%% C4 的元素颜色不走主题变量，要在图里逐个写 UpdateElementStyle（用 --body 传入正文时自动生成）：']
            for cls, lbl, p, _, (f, st, tx) in rows:
                if cls == 'boundary':
                    continue
                tail.append(f'%% {lbl}: UpdateElementStyle(别名, $fontColor="{tx}", $bgColor="{f}", $borderColor="{st}")')
            tail.append(f'%% 关系: UpdateRelStyle(起点, 终点, $textColor="{s["text"]}", $lineColor="{s["line"]}")')
            tail.append('%% 边界（Container_Boundary 等）没有样式宏，保持 Mermaid 默认的虚线框；边界角色的颜色只用于 drawio')
    elif kind == 'block':
        tail = _classDefs(rows)
        tail.append('%% 用法：class a,b capability（block-beta 里写在块定义之后）')
    elif kind == 'requirement':
        f0, st0, t0 = s['slots'][0]
        v.update({'requirementBackground': f0, 'requirementBorderColor': st0, 'requirementTextColor': t0,
                  'relationColor': s['line'], 'relationLabelBackground': s['bg'], 'relationLabelColor': s['text']})
        tail = _classDefs(rows)
        tail.append('%% element 的配色：classDef 后 class 元素名 element')
    elif kind == 'gantt':
        f0, st0, t0 = s['slots'][0]
        af, ast, _ = paint(s, 'accent')
        df, dst, _ = paint(s, 'done')
        cf, cst, _ = paint(s, 'bad')
        v.update({
            'taskBkgColor': f0, 'taskBorderColor': st0, 'taskTextColor': t0, 'taskTextLightColor': t0,
            'taskTextDarkColor': s['text'], 'taskTextOutsideColor': s['text'],
            'activeTaskBkgColor': af, 'activeTaskBorderColor': ast,
            'doneTaskBkgColor': df, 'doneTaskBorderColor': dst,
            'critBkgColor': cf, 'critBorderColor': cst,
            'sectionBkgColor': s['soft'], 'altSectionBkgColor': s['bg'], 'sectionBkgColor2': s['soft'],
            'todayLineColor': cst,
        })
        tail = ['%% active / done / crit / milestone 上的文字都用 taskTextDarkColor；网格竖线由渲染端决定，主题变量改不了']
    elif kind == 'pie':
        # 扇区标签统一一个颜色，不够 3:1 的扇区微调；带正文时最后一块当"其他"用弱化色
        lab, cols = fitLabels([series[i % len(series)] for i in range(12)], ['#FFFFFF', s['text'], '#111111'], 3.0)
        for i, c in enumerate(cols):
            v[f'pie{i + 1}'] = c
        n = _countPieRows(body) if body else 0
        if 0 < n <= 12:
            v[f'pie{n}'] = paint(s, 'muted')[0]
        v.update({'pieStrokeColor': s['bg'], 'pieOuterStrokeColor': s['bg'], 'pieTitleTextColor': s['text'],
                  'pieSectionTextColor': lab, 'pieLegendTextColor': s['text'], 'pieOpacity': '1'})
        tail = ['%% 超过 5 类就把小项合并成"其他"，放到最后；带 --body 时最后一块自动用弱化色']
    elif kind == 'quadrant':
        for i, p in {1: 'ramp:2', 2: 'ramp:3', 3: 'ramp:0', 4: 'ramp:1'}.items():
            f, _, tx = paint(s, p)
            v[f'quadrant{i}Fill'] = f
            v[f'quadrant{i}TextFill'] = tx
        v.update({'quadrantPointFill': s['primary'], 'quadrantPointTextFill': s['text'],
                  'quadrantXAxisTextFill': s['text'], 'quadrantYAxisTextFill': s['text'],
                  'quadrantInternalBorderStrokeFill': s['border'], 'quadrantExternalBorderStrokeFill': s['border'],
                  'quadrantTitleFill': s['text']})
        tail = ['%% 象限深浅按优先级：左上最深（马上做）> 右上 > 右下 > 左下']
    elif kind == 'xychart':
        v['xyChart'] = {'backgroundColor': s['bg'], 'titleColor': s['text'],
                        'xAxisLabelColor': s['text'], 'xAxisTitleColor': s['text'],
                        'xAxisTickColor': s['muted'], 'xAxisLineColor': s['muted'],
                        'yAxisLabelColor': s['text'], 'yAxisTitleColor': s['text'],
                        'yAxisTickColor': s['muted'], 'yAxisLineColor': s['muted'],
                        'plotColorPalette': ', '.join(series[:6])}
        tail = ['%% 第 n 个 bar/line 用 plotColorPalette 的第 n 个颜色；只想突出一根柱子时改用单色 + 灰']
    elif kind == 'sankey':
        series = [standOut(c, s['bg'], 1.6) for c in series]
        if body is not None:
            body, order, names = _parseSankey(body)
            nodes = {n: series[i % len(series)] for i, n in enumerate(order)}
            if names:
                body += '\n' + '\n'.join(f'%% {en} = {cn}' for en, cn in names.items())
                SANKEY_NAMES.update(names)
        else:
            nodes = {f'<节点{i + 1}>': series[i % len(series)] for i in range(len(series))}
        front = _frontmatter({'fontFamily': FONT, 'textColor': s['text']},
                             {'sankey': {'linkColor': 'source', 'nodeColors': nodes}})
        if body is not None:
            return front + '\n' + (own_header or HEADERS['sankey']) + '\n' + body
        note = '%% 把 <节点n> 换成 CSV 里的节点名（用 --body 传入正文时自动生成）；节点名只能用 ASCII，可写成 英文|中文'
        return front + '\n' + HEADERS['sankey'] + '\n' + note
    elif kind == 'git':
        for i in range(8):
            c = series[i % len(series)]
            v[f'git{i}'] = c
            v[f'gitBranchLabel{i}'] = label(c)
            v[f'gitInv{i}'] = s['bg']
        v.update({'commitLabelColor': s['text'], 'commitLabelBackground': s['soft'],
                  'tagLabelColor': s['onPrimary'], 'tagLabelBackground': s['primary'], 'tagLabelBorder': s['primary']})
    elif kind == 'venn':
        for i in range(8):
            v[f'venn{i + 1}'] = series[i % len(series)]
        v.update({'vennTitleTextColor': s['text'], 'vennSetTextColor': s['text']})
    elif kind == 'treemap':
        # 分组按 60% 透明度画，叶子再叠 30% 父色（合计约 72%）；把颜色调浅到正文在叠色上可读
        for k in range(12):
            c = series[k % len(series)]
            while contrast(mix(s['bg'], c, 0.72), s['text']) < 4.5:
                c = mix(c, s['bg'], 0.1)
            v[f'cScale{k}'] = c
            v[f'cScalePeer{k}'] = series[k % len(series)]
            v[f'cScaleLabel{k}'] = s['text']
        pf, pst, pt = paint(s, 'primary')
        tail = [f'classDef focus fill:{pf},fill-opacity:1,stroke:{pst},color:{pt}',
                '%% 分组颜色按出现顺序取 cScale0..；重点叶子在节点后加 :::focus']
    elif kind == 'chart':
        return '%% 该图用代码绘制（matplotlib / ECharts），配色用：\n' + emitChart(sid)
    header = own_header or HEADER_OVERRIDE.get(tid, HEADERS[kind])
    main_part = body if body is not None else '    %% 在这里写图的正文'
    return '\n'.join([_frontmatter(v), header, main_part] + tail)


# ---------------------------------------------------------------------------
# draw.io / CSS / 图表 输出
# ---------------------------------------------------------------------------


def emitDrawio(tid, sid):
    """每个角色的 draw.io style 字符串，第一行是页面背景。"""
    s, rows = roleTable(tid, sid)
    base = 'rounded=1;whiteSpace=wrap;html=1;arcSize=12;fontSize=13;'
    out = [f'# {TYPES[tid]["name"]} · {s["name"]}　页面背景 {s["bg"]}（Format → Background）']
    # 角色
    for _, lbl, p, dashed, (f, st, tx) in rows:
        dash = 'dashed=1;dashPattern=6 4;' if dashed else ''
        width = 'strokeWidth=2;' if p in ('primary', 'accent') else ''
        out.append(f'{lbl:<16} {base}fillColor={f};strokeColor={st};fontColor={tx};{width}{dash}')
    # 连线、容器、泳道、边界、文字
    out += [
        f'{"连线":<16} edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor={s["line"]};fontColor={s["text"]};'
        f'fontSize=11;endArrow=block;endFill=1;endSize=6;jumpStyle=arc;',
        f'{"虚线（异步/依赖）":<12} edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;dashed=1;strokeColor={s["line"]};'
        f'fontColor={s["text"]};fontSize=11;endArrow=open;endSize=6;',
        f'{"分组容器":<16} rounded=1;arcSize=3;whiteSpace=wrap;html=1;fillColor={s["soft"]};strokeColor={s["border"]};'
        f'fontColor={s["text"]};verticalAlign=top;align=left;spacingLeft=10;spacingTop=6;fontStyle=1;fontSize=14;',
        f'{"泳道":<16} swimlane;horizontal=0;startSize=32;html=1;fillColor={s["soft"]};swimlaneFillColor={s["bg"]};'
        f'strokeColor={s["border"]};fontColor={s["text"]};fontStyle=1;fontSize=14;',
        f'{"边界（虚线）":<14} rounded=1;arcSize=3;html=1;fillColor=none;dashed=1;dashPattern=6 4;strokeColor={s["border"]};'
        f'fontColor={s["text"]};verticalAlign=top;align=left;spacingLeft=10;',
        f'{"标题文字":<16} text;html=1;align=left;verticalAlign=middle;fontColor={s["text"]};fontSize=18;fontStyle=1;',
        f'{"说明文字":<16} text;html=1;align=left;verticalAlign=top;whiteSpace=wrap;fontColor={mix(s["text"], s["bg"], 0.2)};fontSize=12;',
    ]
    return '\n'.join(out)


def _rgba(color, alpha):
    """hex 转 rgba() 字符串。"""
    r, g, b = toRgb(color)
    return f'rgba({r},{g},{b},{alpha})'


def diagramDesignTokens(s):
    """把方案映射成 diagram-design 的语义角色（paper / ink / accent …）。

    diagram-design 的 muted / soft / link / accent 都会当文字用，所以这里统一压到对底 4.5:1。

    参数:
        s: resolveScheme 的结果
    返回:
        {角色名: 颜色}
    """
    bg, text = s['bg'], s['text']
    accent = standOut(s['primary'], bg, 4.5)
    tokens = {
        'paper': bg,
        'paper-2': mix(bg, text, 0.04),
        'ink': text,
        'ink-strong': '#111111',
        'muted': standOut(mix(text, bg, 0.45), bg, 4.5),
        'soft': standOut(mix(text, bg, 0.25), bg, 4.5),
        'rule': _rgba(text, 0.12),
        'rule-solid': s['border'],
        'accent': accent,
        'accent-tint': _rgba(accent, 0.08),
        'link': standOut(s['line'], bg, 4.5),
    }
    # 系列色只取前 5 个，非焦点系列用
    for i, c in enumerate(s['series'][:5]):
        tokens[f'series-{i + 1}'] = c
    return tokens


def emitCss(sid):
    """方案的 CSS 变量：第一组是本方案的 token，第二组按 diagram-design 的角色命名。"""
    s = resolveScheme(sid)
    lines = [':root {']
    for k in ('bg', 'surface', 'soft', 'accent', 'text', 'muted', 'line', 'border', 'primary', 'onPrimary'):
        lines.append(f'  --{k}: {s[k]};')
    for i, (f, st, t) in enumerate(s['slots']):
        lines += [f'  --slot{i}-fill: {f};', f'  --slot{i}-stroke: {st};', f'  --slot{i}-text: {t};']
    for i, c in enumerate(s['series']):
        lines.append(f'  --series-{i + 1}: {c};')
    for k, c in s['state'].items():
        lines.append(f'  --state-{k}: {c};')
    lines.append('}')
    # diagram-design 角色
    lines.append('/* diagram-design 角色：paper / ink / muted / soft / rule / accent / link / series，按名字填进它的 style-guide 或 profile */')
    lines.append(':root {')
    for k, c in diagramDesignTokens(s).items():
        lines.append(f'  --dd-{k}: {c};')
    lines.append('}')
    return '\n'.join(lines)


def emitChart(sid):
    """图表代码用的 JSON 色表。"""
    s = resolveScheme(sid)
    return json.dumps({
        'background': s['bg'], 'text': s['text'], 'axis': s['muted'],
        'grid': mix(s['muted'], s['bg'], 0.6), 'primary': s['primary'],
        'categorical': s['series'], 'sequential': s['ramp'],
        'highlight': s['primary'], 'deemphasis': mix(s['muted'], s['bg'], 0.4), 'state': s['state'],
        'nodes': [standOut(c, s['bg'], 1.6) for c in s['series']],
    }, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# 校验
# ---------------------------------------------------------------------------


def _structureIssues(s):
    """方案的结构校验：主色独立、主色托白字、连线对底、容器对底、系列色数量、槽字色。"""
    issues = []
    fills = [f for f, _, _ in s['slots']]
    # 主色不与槽相同且拉得开
    if any(s['primary'].upper() == f.upper() for f in fills):
        issues.append('主色与某个槽填充相同')
    elif not all(isApart(s['primary'], f) for f in fills):
        issues.append('主色与某个槽填充拉不开')
    # 主色托白字
    if contrast(s['primary'], '#FFFFFF') < 3.0:
        issues.append(f'主色上白字 {contrast(s["primary"], "#FFFFFF"):.2f} < 3')
    # 连线、描边、容器对底
    if contrast(s['line'], s['bg']) < 3.0:
        issues.append(f'连线对底 {contrast(s["line"], s["bg"]):.2f} < 3')
    if contrast(s['border'], s['bg']) < 2.0:
        issues.append(f'描边对底 {contrast(s["border"], s["bg"]):.2f} < 2')
    if contrast(s['soft'], s['bg']) < 1.10:
        issues.append(f'容器对底 {contrast(s["soft"], s["bg"]):.2f} < 1.1')
    # 系列色数量
    if len(s['series']) < 6:
        issues.append(f'系列色只有 {len(s["series"])} 个')
    # 槽字色
    for i, (f, _, t) in enumerate(s['slots']):
        need = 3.0 if t == '#FFFFFF' else 4.5
        if contrast(f, t) < need:
            issues.append(f'槽 {i} 字色 {contrast(f, t):.2f} < {need}')
    return issues


def check(sids):
    """校验方案：先查结构，再查每个图型每个角色的字对填充（实色块 3:1，其余 4.5:1）。

    参数:
        sids: 方案 id 列表
    """
    bad = 0
    for sid in sids:
        s = resolveScheme(sid)
        # 结构
        for msg in _structureIssues(s):
            bad += 1
            print(f'{sid:<10}结构          {msg}')
        # 角色字对填充
        for tid in TYPES:
            _, rows = roleTable(tid, sid)
            for _, lbl, p, _, (f, _, tx) in rows:
                need = 3.0 if p.startswith('solid:') or p == 'primary' or tx == '#FFFFFF' else 4.5
                r = contrast(f, tx)
                if r < need:
                    bad += 1
                    print(f'{sid:<10}{tid:<14}{lbl:<14} {f} on {tx}  {r:.2f} < {need}')
    print('全部通过' if not bad else f'{bad} 项不通过')


# ---------------------------------------------------------------------------
# 命令行
# ---------------------------------------------------------------------------


def _requireType(tid):
    """图型不存在时退出。"""
    if tid not in TYPES:
        raise SystemExit(f'图型不存在：{tid}；执行 `palette.py types` 查看可用图型')
    return tid


def _typeAndScheme(args):
    """从参数里取 (图型, 方案)，方案缺省用全局默认。"""
    tid = _requireType(args[0])
    sid = args[1] if len(args) > 1 and not args[1].startswith('--') else DEFAULT_SCHEME
    return tid, sid


def _schemeArg(args):
    """从参数里取方案：缺省或给的是图型时都用全局默认。"""
    if not args or args[0] in TYPES:
        return DEFAULT_SCHEME
    return args[0]


def _readBody(args):
    """读 --body 指定的正文，'-' 读标准输入。

    抛出:
        SystemExit: 文件不存在或读不了
    """
    i = args.index('--body')
    if i + 1 >= len(args):
        raise SystemExit('--body 后面要跟正文文件路径，或 - 表示标准输入')
    src = args[i + 1]
    if src == '-':
        return sys.stdin.read().rstrip('\n')
    try:
        with open(src, encoding='utf-8') as fh:
            return fh.read().rstrip('\n')
    except OSError as e:
        raise SystemExit(f'读不了正文文件 {src}：{e.strerror}')


def main(argv):
    """命令入口。"""
    if len(argv) < 2 or argv[1] in ('-h', '--help', 'help'):
        print(__doc__)
        return
    cmd, args = argv[1], argv[2:]
    global INIT_STYLE
    # --init 影响 frontmatter 写法
    if '--init' in args:
        INIT_STYLE = True
        args = [a for a in args if a != '--init']
    if cmd == 'schemes':
        for sid, sp in SCHEMES.items():
            mark = '默认' if sid == DEFAULT_SCHEME else '    '
            print(f'{mark} {sid:<10} {sp["name"]:<6} {sp["mood"]}')
    elif cmd == 'types':
        for cat, cname in CATS.items():
            print(f'## {cname}')
            for tid, t in TYPES.items():
                if t['cat'] == cat:
                    header = HEADER_OVERRIDE.get(tid) or HEADERS.get(t['kind'], '代码绘图')
                    print(f'  {tid:<14} {t["name"]:<28} {header}')
    elif cmd == 'show':
        print(json.dumps(resolveScheme(_schemeArg(args)), ensure_ascii=False, indent=2))
    elif cmd == 'roles':
        tid, sid = _typeAndScheme(args)
        s, rows = roleTable(tid, sid)
        print(f'# {TYPES[tid]["name"]} · {sid}（页面背景 {s["bg"]}，连线 {s["line"]}，正文 {s["text"]}）')
        for cls, lbl, _, dashed, (f, st, tx) in rows:
            print(f'{cls:<12} {lbl:<18} fill {f}  stroke {st}  text {tx}{"  虚线" if dashed else ""}')
    elif cmd == 'mermaid':
        tid, sid = _typeAndScheme(args)
        body = _readBody(args) if '--body' in args else None
        code = emitMermaid(tid, sid, body)
        if '--md' in args:
            code = '```mermaid\n' + code + '\n```'
            if SANKEY_NAMES:
                code += '\n\n' + _mappingTable(SANKEY_NAMES)
        print(code)
    elif cmd == 'drawio':
        print(emitDrawio(*_typeAndScheme(args)))
    elif cmd == 'css':
        print(emitCss(_schemeArg(args)))
    elif cmd == 'chart':
        print(emitChart(_schemeArg(args)))
    elif cmd == 'check':
        check(args or list(SCHEMES))
    else:
        print(__doc__)


if __name__ == '__main__':
    try:
        main(sys.argv)
    except BrokenPipeError:
        pass
