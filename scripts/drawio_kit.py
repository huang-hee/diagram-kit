#!/usr/bin/env python3
"""按 references/design-rules.md 的统一风格生成 draw.io 图：颜色取自 palette.py，版式、尺寸、连线规则写在组件里。

用法（在自己的出图脚本里）:
  import sys; sys.path.insert(0, '$SKILL/scripts')
  from drawio_kit import Diagram
  d = Diagram('标题', '这张图回答的问题', scheme='macaron')   # scheme 省略时用默认方案
  a = d.box(120, 140, 200, 64, '主名', '说明', role='lav')
  b = d.box(420, 140, 200, 64, '主名', '说明', role='key')
  d.edge(a, b, '标签', src='R', dst='L')
  d.legend(120, 260, [('lav', '处理'), ('key', '焦点'), ('edge', '调用')])
  d.save('图.drawio'); d.export('图.drawio', '图.png')     # 2 倍、边距 24、PNG 内嵌可编辑 XML

坐标约定：左上角为原点，单位 px，取 10 的倍数；标题区占 y 0–100，主体从 y≈120 开始。
角色（role）：lav / peach / mint / apricot（四个槽位）、sage / slate（第 5、6 个系列色）、ext（外部系统）、
key（强调色，一图 1–2 个）、ok / bad（状态）、note（说明）、white（白底描边）、soft（浅底）、pending（待定，配 dashed）。
端口（src / dst）：R L T B，或 TR TL BR BL RT RB LT LB（边上 1/4、3/4 处），或 (x, y) 相对坐标。
"""
from __future__ import annotations

import base64
import math
import os
import subprocess
import sys
import urllib.parse
import xml.etree.ElementTree as ET
import zlib
from html import escape as _esc

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import palette as P  # noqa: E402

FONT = P.FONT
SERIES = ['lav', 'peach', 'mint', 'apricot', 'sage', 'slate']
TOKENS = {
    'title_size': 22, 'subtitle_size': 13, 'band_size': 14, 'node_size': 13, 'sub_size': 11,
    'edge_label_size': 12, 'panel_size': 12, 'edge_width': 1.5, 'key_edge_width': 2.5,
    'stroke_width': 1, 'radius': 8, 'export_scale': 2, 'export_border': 24,
}
PORTS = {
    'R': (1, 0.5), 'L': (0, 0.5), 'T': (0.5, 0), 'B': (0.5, 1),
    'TR': (0.75, 0), 'TL': (0.25, 0), 'BR': (0.75, 1), 'BL': (0.25, 1),
    'RT': (1, 0.25), 'RB': (1, 0.75), 'LT': (0, 0.25), 'LB': (0, 0.75),
}


def text_width(s: str, size: int = 13) -> int:
    """估算一行文字的像素宽度：中日韩字符 1 个字号，大写和数字 0.68，其余拉丁字符 0.56，窄标点 0.32。"""
    w = 0.0
    for ch in s:
        if ord(ch) > 0x2E80:
            w += size
        elif ch.isupper() or ch.isdigit():
            w += size * 0.68
        elif ch == '_':
            w += size * 0.6
        elif ch in ' .,:;!|\'`':
            w += size * 0.32
        else:
            w += size * 0.56
    return int(w)


def wrap_lines(s: str, size: int, maxw: float) -> int:
    """按宽度估算换行后的行数（手动换行符分段各自计算）。"""
    return sum(max(1, math.ceil(text_width(part, size) / maxw)) for part in s.split('\n'))


class Theme:
    """一个配色方案在 drawio 里的全部取色：角色色、线色、正文与次要字色、浅底、ramp。"""

    def __init__(self, sid: str | None = None):
        s = P.resolveScheme(sid or P.DEFAULT_SCHEME)
        self.s = s
        self.bg = s['bg']
        self.text = s['text']
        self.muted = P.mix(s['text'], s['bg'], 0.2)
        self.line = s['line']
        self.soft = s['soft']
        self.border = s['border']
        self.ramp = s['ramp']
        self.primary = s['primary']
        self.on_primary = s['onPrimary']
        series = s['series']
        ext = P.paint(s, 'muted')
        self.roles = {
            'lav': P.paint(s, 'slot0'), 'peach': P.paint(s, 'slot1'), 'mint': P.paint(s, 'slot2'), 'apricot': P.paint(s, 'slot3'),
            'sage': (series[4], s['muted'], s['text']), 'slate': (series[5], s['muted'], s['text']),
            'ext': ext, 'key': P.paint(s, 'primary'), 'ok': P.paint(s, 'ok'), 'bad': P.paint(s, 'bad'),
            'note': P.paint(s, 'note'), 'white': P.paint(s, 'boundary'), 'soft': P.paint(s, 'soft'),
            'pending': (ext[0], s['muted'], self.muted),
        }

    def fill(self, role):
        return self.roles[role][0]

    def stroke(self, role):
        return self.roles[role][1]

    def font(self, role):
        return self.roles[role][2]

    def deep(self, role: str) -> str:
        """系列色的深色版本（一级分支实底用）：四个槽位取配套字色，其余由系列色混向正文色派生。"""
        if role in ('lav', 'peach', 'mint', 'apricot'):
            return self.font(role)
        return P.mix(self.fill(role), self.text, 0.62)


def _label_html(title: str, sub: str | None, sub_size: int, sub_color: str, bold: bool) -> str:
    t = '<br>'.join(_esc(x) for x in title.split('\n'))
    t = f'<b>{t}</b>' if bold else t
    if sub:
        s = '<br>'.join(_esc(x) for x in sub.split('\n'))
        t += f'<br><span style="font-size:{sub_size}px;color:{sub_color};font-weight:normal">{s}</span>'
    return t


def _compress(xml: str) -> str:
    data = urllib.parse.quote(xml, safe="-_.!~*'()")
    co = zlib.compressobj(9, zlib.DEFLATED, -15)
    return base64.b64encode(co.compress(data.encode()) + co.flush()).decode()


def _fmt(v: float) -> str:
    return f'{v:.2f}'.rstrip('0').rstrip('.')


class Diagram:
    """一张 draw.io 图。组件方法返回新建单元的 id，连线用这些 id。"""

    def __init__(self, title: str = '', subtitle: str = '', scheme: str | None = None, x0: int = 40, y0: int = 32):
        self.t = Theme(scheme)
        self.title = title
        self.cells: list[ET.Element] = []
        self.n = 0
        self.bounds = [10 ** 9, 10 ** 9, -10 ** 9, -10 ** 9]
        if title:
            self.header(title, subtitle, x0, y0)

    # ---------- 基础 ----------
    def _id(self, prefix='c'):
        self.n += 1
        return f'{prefix}{self.n}'

    def _track(self, x, y, w, h):
        b = self.bounds
        b[0], b[1] = min(b[0], x), min(b[1], y)
        b[2], b[3] = max(b[2], x + w), max(b[3], y + h)

    def vertex(self, value, style, x, y, w, h, parent='1', cid=None):
        """原始单元：value 是 HTML，style 是 drawio 样式串。组件不够用时用它补。"""
        cid = cid or self._id('v')
        c = ET.Element('mxCell', id=cid, value=value, style=style, vertex='1', parent=parent)
        ET.SubElement(c, 'mxGeometry', x=_fmt(x), y=_fmt(y), width=_fmt(w), height=_fmt(h), attrib={'as': 'geometry'})
        self.cells.append(c)
        if parent == '1':
            self._track(x, y, w, h)
        return cid

    # ---------- 标题区与文字 ----------
    def header(self, title, subtitle='', x=40, y=32):
        """标题区：左侧 6px 主色竖条 + 标题 22 加粗 + 副标题 13 次要色。"""
        t = self.t
        self.vertex('', f'rounded=1;arcSize=50;fillColor={t.primary};strokeColor=none;', x, y + 4, 6, 50)
        self.vertex(_esc(title), f'text;html=1;align=left;verticalAlign=middle;fontFamily={FONT};fontSize={TOKENS["title_size"]};'
                                 f'fontStyle=1;fontColor={t.text};', x + 18, y, max(400, text_width(title, 22) + 40), 32)
        if subtitle:
            self.vertex(_esc(subtitle), f'text;html=1;align=left;verticalAlign=middle;fontFamily={FONT};fontSize={TOKENS["subtitle_size"]};'
                                        f'fontColor={t.muted};', x + 18, y + 32, max(400, text_width(subtitle, 13) + 40), 24)

    def text(self, x, y, w, h, s, size=12, color=None, bold=False, align='left', valign='middle', html=False):
        v = s if html else '<br>'.join(_esc(p) for p in s.split('\n'))
        st = (f'text;html=1;whiteSpace=wrap;align={align};verticalAlign={valign};fontFamily={FONT};'
              f'fontSize={size};fontColor={color or self.t.text};fontStyle={1 if bold else 0};spacing=0;')
        return self.vertex(v, st, x, y, w, h)

    def footer(self, x, y, s, w=1100):
        """读图行：12 号次要色，只写图里能看到的东西。"""
        return self.text(x, y, w, 20, s, size=12, color=self.t.muted)

    # ---------- 节点 ----------
    def box(self, x, y, w, h, title, sub=None, role='lav', shape='rect', size=None, bold=True,
            dashed=False, stroke_width=None, align='center', parent='1', cid=None, extra='', sub_color=None):
        """节点：主名加粗 + 说明小字。shape: rect pill diamond cyl para circle doc hex note square。
        用 extra 改成深色底时，同时传 sub_color（如 d.t.bg），否则说明小字是默认字色。"""
        t = self.t
        fill, stroke, font = t.roles[role]
        size = size or TOKENS['node_size']
        sub_color = sub_color or (font if role not in ('white', 'pending') else t.muted)
        value = _label_html(title, sub, TOKENS['sub_size'], sub_color, bold)
        shapes = {
            'rect': f'rounded=1;arcSize={TOKENS["radius"]};absoluteArcSize=1;',
            'pill': 'rounded=1;arcSize=50;',
            'diamond': 'rhombus;',
            'cyl': 'shape=cylinder3;boundedLbl=1;backgroundOutline=1;size=8;',
            'para': 'shape=parallelogram;perimeter=parallelogramPerimeter;fixedSize=1;size=14;',
            'circle': 'ellipse;aspect=fixed;',
            'doc': 'shape=document;boundedLbl=1;size=0.18;',
            'hex': 'shape=hexagon;perimeter=hexagonPerimeter2;fixedSize=1;size=14;',
            'note': 'shape=note;size=14;',
            'square': 'rounded=0;',
        }
        st = (shapes[shape] + f'whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};fontColor={font};'
              f'fontFamily={FONT};fontSize={size};align={align};verticalAlign=middle;'
              f'strokeWidth={stroke_width or TOKENS["stroke_width"]};spacing=6;')
        if dashed or role == 'pending':
            st += 'dashed=1;dashPattern=5 3;'
        return self.vertex(value, st + extra, x, y, w, h, parent=parent, cid=cid)

    def dot(self, x, y, kind='start', size=22):
        """状态图起止：start 实心圆；end 外环 + 实心圆（连线接返回的外环 id）。"""
        t = self.t
        if kind == 'start':
            return self.vertex('', f'ellipse;aspect=fixed;fillColor={t.text};strokeColor=none;', x, y, size, size)
        outer = self.vertex('', f'ellipse;aspect=fixed;fillColor={t.bg};strokeColor={t.text};strokeWidth=1.5;', x, y, size, size)
        self.vertex('', f'ellipse;aspect=fixed;fillColor={t.text};strokeColor=none;', x + 5, y + 5, size - 10, size - 10)
        return outer

    def bar(self, x, y, w, h=8):
        """活动图的分叉 / 汇合粗横条。"""
        return self.vertex('', f'rounded=1;arcSize=50;fillColor={self.t.text};strokeColor=none;', x, y, w, h)

    def table(self, x, y, w, title, rows, role='lav', sub=None, row_h=22, head_h=36):
        """ER 实体 / 类卡片。rows: 字符串或 (文字, 'pk' | 'fk' | 'muted' | 'sep')。返回外框 id。"""
        t = self.t
        fill, stroke, font = t.roles[role]
        body_h = sum(8 if (isinstance(r, tuple) and r[1] == 'sep') else row_h for r in rows) + 10
        h = head_h + body_h
        outer = self.vertex('', f'rounded=1;arcSize=8;absoluteArcSize=1;fillColor={t.bg};strokeColor={stroke};strokeWidth=1;', x, y, w, h)
        self.vertex('', f'rounded=1;arcSize=8;absoluteArcSize=1;fillColor={fill};strokeColor=none;', x + 1, y + 1, w - 2, head_h)
        self.vertex('', f'rounded=0;fillColor={fill};strokeColor=none;', x + 1, y + head_h - 8, w - 2, 8)
        self.vertex(_label_html(title, sub, 11, font, True),
                    f'text;html=1;whiteSpace=wrap;align=center;verticalAlign=middle;fontFamily={FONT};fontSize=13;fontColor={font};',
                    x, y, w, head_h)
        cy = y + head_h + 5
        for r in rows:
            txt, kind = (r, None) if isinstance(r, str) else r
            if kind == 'sep':
                self.line(x + 10, cy + 4, x + w - 10, cy + 4, color=stroke, width=1)
                cy += 8
                continue
            st = f'text;html=1;align=left;verticalAlign=middle;fontFamily={FONT};fontSize=12;spacingLeft=12;'
            st += {'pk': f'fontStyle=1;fontColor={t.text};', 'fk': f'fontColor={t.muted};', 'muted': f'fontColor={t.muted};'}.get(kind, f'fontColor={t.text};')
            self.vertex(_esc(txt), st, x, cy, w, row_h)
            cy += row_h
        return outer

    def chevron(self, x, y, w, h, title, sub=None, role='lav', size=14):
        """阶段箭头条（用户旅程、路线图的阶段）：系列色深色实底白字，首尾相接时下一个 x = 上一个 x + w - 8。"""
        t = self.t
        dk = t.deep(role)
        return self.vertex(_label_html(title, sub, 11, t.bg, True),
                           f'shape=step;perimeter=stepPerimeter;fixedSize=1;size=16;whiteSpace=wrap;html=1;fillColor={dk};strokeColor=none;'
                           f'fontColor={t.bg};fontFamily={FONT};fontSize={size};align=center;verticalAlign=middle;spacingLeft=14;spacingRight=8;',
                           x, y, w, h)

    def badge(self, x, y, n, size=26, role='key'):
        """编号徽标（步骤号、象限图的编号点）。"""
        fill, _, font = self.t.roles[role]
        return self.vertex(str(n), f'ellipse;aspect=fixed;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={self.t.bg};strokeWidth=2;'
                                   f'fontColor={font};fontFamily={FONT};fontSize=13;fontStyle=1;align=center;verticalAlign=middle;',
                           x, y, size, size)

    def sticky(self, x, y, w, h, s, role='note', size=12):
        """便签（亲和图、看板卡片）：折角便签，文字左对齐。"""
        fill, stroke, _ = self.t.roles[role]
        return self.vertex(_esc(s).replace('\n', '<br>'),
                           f'shape=note;size=12;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};fontColor={self.t.text};'
                           f'fontFamily={FONT};fontSize={size};align=left;verticalAlign=middle;spacingLeft=12;spacingRight=10;',
                           x, y, w, h)

    # ---------- 分层与分组 ----------
    def band(self, x, y, w, h, label, sub=None, label_w=130, tint=None, label_fill=None):
        """横向分层带：左侧标签栏 + 浅底内容区，不描边。"""
        t = self.t
        self.vertex('', f'rounded=1;arcSize=8;absoluteArcSize=1;fillColor={tint or t.soft};strokeColor=none;', x, y, w, h)
        self.vertex(_label_html(label, sub, 11, t.muted, True),
                    f'rounded=1;arcSize=8;absoluteArcSize=1;whiteSpace=wrap;html=1;fillColor={label_fill or t.ramp[0]};strokeColor=none;'
                    f'fontColor={t.text};fontFamily={FONT};fontSize={TOKENS["band_size"]};align=center;verticalAlign=middle;spacing=8;',
                    x, y, label_w, h)

    def vband(self, x, y, w, h, label, fill=None, color=None):
        """右侧纵向贯穿条（横切关注点），文字竖排。"""
        t = self.t
        v = '<br>'.join(_esc(c) for c in label)
        return self.vertex(v, f'rounded=1;arcSize=8;absoluteArcSize=1;whiteSpace=wrap;html=1;fillColor={fill or t.ramp[0]};strokeColor=none;'
                              f'fontColor={color or t.text};fontFamily={FONT};fontSize=14;fontStyle=1;align=center;verticalAlign=middle;',
                           x, y, w, h)

    def group(self, x, y, w, h, label=None, dashed=False, fill=None, stroke=None, label_size=13):
        """分组容器：浅底无边框；dashed=True 时为只表示边界的虚线框。"""
        t = self.t
        st = (f'rounded=1;arcSize=10;absoluteArcSize=1;whiteSpace=wrap;html=1;fillColor={fill or t.soft};'
              f'strokeColor={stroke or "none"};fontColor={t.text};fontFamily={FONT};fontSize={label_size};fontStyle=1;'
              f'align=left;verticalAlign=top;spacingLeft=14;spacingTop=8;')
        if dashed:
            st += f'dashed=1;dashPattern=6 4;strokeColor={stroke or t.border};fillColor={fill or "none"};'
        return self.vertex(_esc(label or ''), st, x, y, w, h)

    def frame(self, x, y, w, h, tag, title, sub=None, role='lav', dashed=False):
        """交互概览的 ref / sd 框：卡片 + 左上角小标签。"""
        t = self.t
        cid = self.box(x, y, w, h, title, sub, role=role, dashed=dashed, extra='spacingTop=14;')
        tw = text_width(tag, 11) + 16
        self.vertex(_esc(tag), f'rounded=1;arcSize=4;absoluteArcSize=1;html=1;fillColor={t.stroke(role)};strokeColor=none;'
                               f'fontColor={t.bg};fontFamily={FONT};fontSize=11;fontStyle=1;align=center;verticalAlign=middle;spacing=0;',
                    x + 8, y + 6, tw, 18)
        return cid

    # ---------- 说明区 ----------
    def panel(self, x, y, w, title, lines, kind='note', h=None):
        """说明面板（note 放依据与例外，soft 放次要信息），高度按文字量估算；返回底边 y。"""
        t = self.t
        n = sum(wrap_lines(s, TOKENS['panel_size'], w - 32) for s in lines)
        h = h or (30 + n * 20 + len(lines) * 2 + 14)
        fill, stroke, _ = t.roles[kind]
        self.vertex('', f'rounded=1;arcSize=8;absoluteArcSize=1;fillColor={fill};strokeColor={stroke};strokeWidth=1;', x, y, w, h)
        body = f'<b style="font-size:13px">{_esc(title)}</b>' + ''.join(f'<div style="margin-top:6px">{_esc(s)}</div>' for s in lines)
        self.vertex(body, f'text;html=1;whiteSpace=wrap;align=left;verticalAlign=top;fontFamily={FONT};fontSize=12;fontColor={t.text};spacing=0;',
                    x + 16, y + 14, w - 32, h - 24)
        return y + h

    def legend(self, x, y, items, gap=28):
        """图例一行。items 的第一项：role（pending 画虚线框）、'edge' / 'edge-dashed' / 'edge-key'（带箭头的线）、
        'line' / 'line-dashed'（不带箭头的线）、('color', 填充) 或 ('color', 填充, 描边)（自定义色块）。返回结束 x。"""
        t = self.t
        cx = x
        for kind, lab in items:
            if isinstance(kind, tuple):
                self.vertex('', f'rounded=1;arcSize=4;absoluteArcSize=1;fillColor={kind[1]};'
                                f'strokeColor={kind[2] if len(kind) > 2 else "none"};', cx, y + 2, 22, 14)
                sw = 22
            elif kind.startswith('line'):
                self.line(cx, y + 9, cx + 32, y + 9, dashed=kind == 'line-dashed')
                sw = 32
            elif kind.startswith('edge'):
                self.line(cx, y + 9, cx + 32, y + 9, dashed=kind == 'edge-dashed', arrow='block',
                          width=TOKENS['key_edge_width'] if kind == 'edge-key' else None)
                sw = 32
            else:
                fill, stroke, _ = t.roles[kind]
                st = f'rounded=1;arcSize=4;absoluteArcSize=1;fillColor={fill};strokeColor={stroke};'
                if kind == 'pending':
                    st += 'dashed=1;dashPattern=3 2;'
                self.vertex('', st, cx, y + 2, 22, 14)
                sw = 22
            tw = text_width(lab, 12) + 4
            self.text(cx + sw + 8, y, tw, 18, lab, size=12, color=t.muted)
            cx += sw + 8 + tw + gap
        return cx

    # ---------- 连线 ----------
    def edge(self, s, t_, label=None, src=None, dst=None, dashed=False, key=False, points=None, color=None, width=None,
             arrow='block', start_arrow=None, label_offset=None, parent='1', extra=''):
        """正交连线。src / dst 指定端口；points 是显式拐点；label_offset 取 -1..1，把标签挪离拐角。"""
        t = self.t
        st = ('edgeStyle=orthogonalEdgeStyle;rounded=1;arcSize=12;orthogonalLoop=1;jettySize=auto;html=1;'
              f'strokeColor={color or t.line};strokeWidth={width or (TOKENS["key_edge_width"] if key else TOKENS["edge_width"])};'
              f'endArrow={arrow};endFill={0 if arrow in ("open", "none") else 1};endSize=7;jumpStyle=arc;jumpSize=8;'
              f'fontFamily={FONT};fontSize={TOKENS["edge_label_size"]};fontColor={t.text};labelBackgroundColor={t.bg};')
        if start_arrow:
            st += f'startArrow={start_arrow};startFill=1;startSize=7;'
        if dashed:
            st += 'dashed=1;dashPattern=6 4;'
        for k, port in (('exit', src), ('entry', dst)):
            if port:
                px, py = PORTS[port] if isinstance(port, str) else port
                st += f'{k}X={px};{k}Y={py};{k}Dx=0;{k}Dy=0;'
        e = ET.Element('mxCell', id=self._id('e'), value=_esc(label) if label else '', style=st + extra,
                       edge='1', parent=parent, source=s, target=t_)
        g = ET.SubElement(e, 'mxGeometry', relative='1', attrib={'as': 'geometry'})
        if label_offset is not None:
            g.set('x', str(label_offset))
        if points:
            arr = ET.SubElement(g, 'Array', attrib={'as': 'points'})
            for px, py in points:
                ET.SubElement(arr, 'mxPoint', x=_fmt(px), y=_fmt(py))
        self.cells.append(e)
        return e.get('id')

    def line(self, x1, y1, x2, y2, color=None, width=None, dashed=False, arrow='none', points=None):
        """按坐标画的线（生命线、坐标轴、鱼骨、时序消息）；arrow='block' 时带实心箭头。"""
        st = (f'html=1;rounded=0;endArrow={arrow};endFill={0 if arrow in ("open", "none") else 1};endSize=7;'
              f'strokeColor={color or self.t.line};strokeWidth={width or TOKENS["edge_width"]};')
        if dashed:
            st += 'dashed=1;dashPattern=6 4;'
        e = ET.Element('mxCell', id=self._id('l'), value='', style=st, edge='1', parent='1')
        g = ET.SubElement(e, 'mxGeometry', relative='1', attrib={'as': 'geometry'})
        ET.SubElement(g, 'mxPoint', x=_fmt(x1), y=_fmt(y1), attrib={'as': 'sourcePoint'})
        ET.SubElement(g, 'mxPoint', x=_fmt(x2), y=_fmt(y2), attrib={'as': 'targetPoint'})
        if points:
            arr = ET.SubElement(g, 'Array', attrib={'as': 'points'})
            for px, py in points:
                ET.SubElement(arr, 'mxPoint', x=_fmt(px), y=_fmt(py))
        self.cells.append(e)
        self._track(min(x1, x2), min(y1, y2), abs(x2 - x1) + 1, abs(y2 - y1) + 1)
        return e.get('id')

    # ---------- 脑图与树 ----------
    def mindmap(self, root, branches, cx, cy=None, top=None, sides='both', root_w=150, gap_x=40, leaf_h=30, gap_y=10):
        """脑图，也用作横向树（sides='right'）。branches: [(一级标签, [子节点])]，子节点为字符串、(标签, [子节点])
        或 (标签, [子节点], {'pending': True})（待定，灰色虚线）。给 top 时内容顶边贴齐 top（标题区下方用 top=120），
        否则以 cy 为中线。一级分支按系列色全局轮换。"""
        t = self.t

        def lab(n):
            return (n, []) if isinstance(n, str) else (n[0], n[1])

        def pending(n):
            return not isinstance(n, str) and len(n) > 2 and n[2].get('pending')

        def own_h(label, level):
            return (40 if level == 1 else leaf_h) + label.count('\n') * 17

        def width_of(label, level):
            size = 14 if level == 1 else (13 if level == 2 else 12)
            return max(text_width(max(label.split('\n'), key=len), size) + 30, 96 if level == 1 else 72)

        def height_of(n, level):
            label, kids = lab(n)
            if not kids:
                return own_h(label, level)
            return max(own_h(label, level), sum(height_of(k, level + 1) for k in kids) + gap_y * (len(kids) - 1))

        def level_widths(nodes, level, acc):
            for n in nodes:
                label, kids = lab(n)
                acc[level] = max(acc.get(level, 0), width_of(label, level))
                level_widths(kids, level + 1, acc)
            return acc

        half = len(branches) if sides == 'right' else (len(branches) + 1) // 2
        items = list(enumerate(branches))
        sides_list = [(items[:half], 1), (items[half:], -1)]
        totals = [sum(height_of(n, 1) for _, n in it) + gap_y * 2.4 * (len(it) - 1) if it else 0 for it, _ in sides_list]
        if top is not None:
            cy = top + max(totals) / 2
        root_h = 56
        rid = self.box(cx - root_w / 2, cy - root_h / 2, root_w, root_h, root, role='key', shape='pill', size=18)

        def place(nodes, level, x_edge, y_top, direction, parent_id, color, widths):
            y = y_top
            for idx, n in nodes:
                label, kids = lab(n)
                role = SERIES[idx % len(SERIES)] if level == 1 else color
                fill, stroke, _ = t.roles[role]
                dk = t.deep(role)
                h_sub, h_own, w = height_of(n, level), own_h(label, level), widths[level]
                x = x_edge if direction > 0 else x_edge - w
                ny = round(y + (h_sub - h_own) / 2)
                if pending(n):
                    nid = self.box(x, ny, w, h_own, label, size=12, bold=False, role='pending', align='left', extra='spacingLeft=10;')
                    ecolor, ew = t.stroke('pending'), 1.2
                elif level == 1:
                    nid = self.box(x, ny, w, h_own, label, size=14, role='white', extra=f'fillColor={dk};strokeColor={dk};fontColor={t.bg};')
                    ecolor, ew = dk, 2
                elif level == 2:
                    nid = self.box(x, ny, w, h_own, label, size=13, bold=False, role='white', align='left',
                                   extra=f'fillColor={fill};strokeColor=none;fontColor={t.text};spacingLeft=10;')
                    ecolor, ew = dk, 1.5
                else:
                    nid = self.box(x, ny, w, h_own, label, size=12, bold=False, role='white', align='left',
                                   extra=f'fillColor={t.bg};strokeColor={stroke};fontColor={t.text};spacingLeft=10;')
                    ecolor, ew = stroke, 1.2
                self.edge(parent_id, nid, src='R' if direction > 0 else 'L', dst='L' if direction > 0 else 'R',
                          color=ecolor, width=ew, arrow='none')
                if kids:
                    place([(None, k) for k in kids], level + 1, x + w + gap_x if direction > 0 else x - gap_x,
                          y, direction, nid, role, widths)
                y += h_sub + (gap_y * 2.4 if level == 1 else gap_y)

        for (it, direction), total in zip(sides_list, totals):
            if it:
                widths = level_widths([n for _, n in it], 1, {})
                x_edge = cx + root_w / 2 + gap_x + 16 if direction > 0 else cx - root_w / 2 - gap_x - 16
                place(it, 1, x_edge, cy - total / 2, direction, rid, None, widths)
        return rid

    def tree_down(self, root, children, x, y, gap_x=20, gap_y=56, node_h=40, leaf_h=34):
        """自上而下的树。根用强调色，一级按系列色轮换，二级浅底，更深白底描边。返回 (根 id, 总宽, 总高)。"""
        t = self.t

        def lab(n):
            return (n, []) if isinstance(n, str) else n

        def own_w(label, level):
            size = 14 if level <= 1 else 12
            return max(text_width(max(label.split('\n'), key=len), size) + 28, 88 if level <= 1 else 72)

        def sub_w(n, level):
            label, kids = lab(n)
            if not kids:
                return own_w(label, level)
            return max(own_w(label, level), sum(sub_w(k, level + 1) for k in kids) + gap_x * (len(kids) - 1))

        depth = [y]

        def place(n, level, left, top, color):
            label, kids = lab(n)
            w_sub, w = sub_w(n, level), own_w(label, level)
            h = node_h if level <= 1 else leaf_h + label.count('\n') * 16
            nx = left + (w_sub - w) / 2
            if level == 0:
                nid = self.box(nx, top, w, h, label, role='key', size=15)
            elif level == 1:
                dk = t.deep(color)
                nid = self.box(nx, top, w, h, label, size=14, role='white', extra=f'fillColor={dk};strokeColor={dk};fontColor={t.bg};')
            else:
                fill, stroke, _ = t.roles[color]
                nid = self.box(nx, top, w, h, label, size=12, bold=False, role='white',
                               extra=f'fillColor={fill if level == 2 else t.bg};strokeColor={stroke};fontColor={t.text};')
            depth[0] = max(depth[0], top + h)
            cx = left
            for i, k in enumerate(kids):
                kc = SERIES[i % len(SERIES)] if level == 0 else color
                kid = place(k, level + 1, cx, top + h + gap_y, kc)
                self.edge(nid, kid, src='B', dst='T', arrow='none', width=1.2, color=t.line if level == 0 else t.stroke(kc))
                cx += sub_w(k, level + 1) + gap_x
            return nid

        rid = place((root, children), 0, x, y, None)
        return rid, sub_w((root, children), 0), depth[0] - y

    # ---------- 鱼骨 ----------
    def fishbone(self, problem, cats, x, y, length=1100, bone_h=190, cause_w=210):
        """鱼骨图：cats = [(大类, [原因])]，上下交替；鱼头在右。返回鱼头 id。"""
        t = self.t
        head = self.box(x + length, y - 40, 210, 80, problem, role='apricot', size=14)
        self.line(x, y, x + length, y, width=3)
        n_cols = max(1, math.ceil(len(cats) / 2))
        span = length / n_cols
        bone = t.stroke('lav')
        for i, (cat, causes) in enumerate(cats):
            col, up = i // 2, i % 2 == 0
            bh = max(bone_h, 34 * len(causes) + 70)
            dx = min(bh * 0.55, span * 0.6)
            bx = x + span * col + span * 0.95 - dx
            top_y = y - bh if up else y + bh
            self.box(bx - 76, top_y - 40 if up else top_y, 152, 40, cat, role='lav')
            self.line(bx, top_y, bx + dx, y, color=bone, width=1.5)
            for j, c in enumerate(causes):
                k = (j + 1) / (len(causes) + 1)
                px, py = bx + dx * k, top_y + (y - top_y) * k
                self.line(px - 26, py, px, py, color=bone, width=1)
                self.text(px - 30 - cause_w, py - 11, cause_w, 22, c, size=12, align='right')
        return head

    # ---------- 时序 ----------
    def seq(self, parts, x0=60, y0=120, gap=200, head_w=160, head_h=54, groups=None):
        """新建时序图。parts: [(key, 标题, 副标题, role)]，role='actor' 画小人。返回 Seq，依次调用 msg / note / frag / els / end，最后 finish。"""
        return Seq(self, parts, x0, y0, gap, head_w, head_h, groups)

    # ---------- 图表图元 ----------
    def path(self, segs, fill, stroke='none', width=1, fill_opacity=100, dashed=False):
        """任意路径（drawio stencil）。segs: [('M', x, y), ('L', x, y), ('C', x1, y1, x2, y2, x, y), ('Z',)]，绝对坐标。"""
        xs, ys = [], []
        for s in segs:
            if s[0] != 'Z':
                xs += s[1::2]
                ys += s[2::2]
        x0, y0 = min(xs), min(ys)
        w, h = max(max(xs) - x0, 1), max(max(ys) - y0, 1)
        parts = []
        for s in segs:
            if s[0] == 'M':
                parts.append(f'<move x="{_fmt(s[1] - x0)}" y="{_fmt(s[2] - y0)}"/>')
            elif s[0] == 'L':
                parts.append(f'<line x="{_fmt(s[1] - x0)}" y="{_fmt(s[2] - y0)}"/>')
            elif s[0] == 'C':
                parts.append(f'<curve x1="{_fmt(s[1] - x0)}" y1="{_fmt(s[2] - y0)}" x2="{_fmt(s[3] - x0)}" y2="{_fmt(s[4] - y0)}" '
                             f'x3="{_fmt(s[5] - x0)}" y3="{_fmt(s[6] - y0)}"/>')
            else:
                parts.append('<close/>')
        op = 'fillstroke' if stroke != 'none' and fill != 'none' else ('fill' if stroke == 'none' else 'stroke')
        shape = (f'<shape name="p" w="{_fmt(w)}" h="{_fmt(h)}" aspect="variable" strokewidth="inherit"><connections/>'
                 f'<background><path>{"".join(parts)}</path></background><foreground><{op}/></foreground></shape>')
        st = (f'shape=stencil({_compress(shape)});html=1;fillColor={fill};strokeColor={stroke};strokeWidth={width};'
              f'fillOpacity={fill_opacity};')
        if dashed:
            st += 'dashed=1;dashPattern=4 3;'
        return self.vertex('', st, x0, y0, w, h)

    def polygon(self, pts, fill, stroke='none', width=1, fill_opacity=100):
        segs = [('M',) + tuple(pts[0])] + [('L',) + tuple(p) for p in pts[1:]] + [('Z',)]
        return self.path(segs, fill, stroke, width, fill_opacity)

    def ribbon(self, x0, a0, b0, x1, a1, b1, fill, opacity=40):
        """桑基流：左端竖线段 (x0, a0..b0) 到右端 (x1, a1..b1) 的贝塞尔丝带，宽度与数值成比例。"""
        m = (x0 + x1) / 2
        segs = [('M', x0, a0), ('C', m, a0, m, a1, x1, a1), ('L', x1, b1), ('C', m, b1, m, b0, x0, b0), ('Z',)]
        return self.path(segs, fill, 'none', 1, opacity)

    def sector(self, cx, cy, r, a0, a1, fill, inner=0, width=2):
        """饼 / 环扇区。角度用弧度，从 12 点钟方向顺时针；inner > 0 为环形。"""
        n = max(8, int(abs(a1 - a0) / (2 * math.pi) * 96))

        def pt(rad, a):
            return cx + rad * math.sin(a), cy - rad * math.cos(a)
        outer = [pt(r, a0 + (a1 - a0) * i / n) for i in range(n + 1)]
        pts = outer + [pt(inner, a1 - (a1 - a0) * i / n) for i in range(n + 1)] if inner > 0 else [(cx, cy)] + outer
        return self.polygon(pts, fill, self.t.bg, width)

    def rect(self, x, y, w, h, fill, stroke='none', extra=''):
        """无文字的直角矩形（柱、刻度带、矩形树的格子）。"""
        return self.vertex('', f'rounded=0;html=1;fillColor={fill};strokeColor={stroke};{extra}', x, y, w, h)

    # ---------- 输出 ----------
    def xml(self) -> str:
        mxfile = ET.Element('mxfile', host='diagram-kit')
        dg = ET.SubElement(mxfile, 'diagram', name=self.title or 'diagram', id='diagram')
        model = ET.SubElement(dg, 'mxGraphModel', dx='1200', dy='800', grid='1', gridSize='10', guides='1', tooltips='1',
                              connect='1', arrows='1', fold='1', page='0', pageScale='1', background=self.t.bg, math='0', shadow='0')
        root = ET.SubElement(model, 'root')
        ET.SubElement(root, 'mxCell', id='0')
        ET.SubElement(root, 'mxCell', id='1', parent='0')
        for c in self.cells:
            root.append(c)
        ET.indent(mxfile)
        return ET.tostring(mxfile, encoding='unicode')

    def save(self, path: str) -> str:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(self.xml())
        return path

    @staticmethod
    def export(drawio_path: str, png_path: str, scale: int | None = None, border: int | None = None, cli: str = 'drawio') -> str:
        """用 draw.io 桌面版命令行导出 PNG（内嵌 XML，可再用 draw.io 打开编辑）。"""
        subprocess.run([cli, '-x', '-f', 'png', '-s', str(scale or TOKENS['export_scale']), '-b', str(border or TOKENS['export_border']),
                        '-e', '-o', png_path, drawio_path], check=True, capture_output=True)
        return png_path


class Seq:
    """时序图：参与者头卡片 + 虚线生命线；消息竖向等距；alt / opt / loop 片段；note 卡片。由 Diagram.seq 创建。"""

    def __init__(self, d: Diagram, parts, x0, y0, gap, head_w, head_h, groups):
        t = d.t
        self.d, self.gap, self.head_w, self.groups = d, gap, head_w, groups or []
        self.x, self.order, self.frames, self.bg = {}, [], [], []
        self.bg_at = len(d.cells)
        self.group_top = y0 - 34 if self.groups else y0
        for i, (k, title, sub, role) in enumerate(parts):
            cx = x0 + head_w / 2 + i * gap
            self.x[k] = cx
            self.order.append(k)
            if role == 'actor':
                d.vertex('', f'shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;outlineConnect=0;'
                             f'fillColor={t.fill("peach")};strokeColor={t.font("peach")};strokeWidth=1.5;', cx - 12, y0 - 2, 24, 36)
                d.text(cx - 60, y0 + 36, 120, 20, title, size=13, bold=True, align='center')
            else:
                d.box(cx - head_w / 2, y0, head_w, head_h, title, sub, role=role)
        self.head_bottom = y0 + head_h
        self.y = self.head_bottom + 26
        self.n = 0

    def _to_bg(self, before):
        moved = self.d.cells[before:]
        del self.d.cells[before:]
        self.bg.extend(moved)

    def _label(self, cx, maxw, text, top):
        t = self.d.t
        lines = wrap_lines(text, 12, maxw)
        h = lines * 17
        w = min(maxw, max(text_width(s, 12) for s in text.split('\n')) + 8)
        ws = 'wrap' if lines > text.count('\n') + 1 else 'nowrap'
        self.d.vertex(_esc(text).replace('\n', '<br>'), f'text;html=1;whiteSpace={ws};align=center;verticalAlign=bottom;'
                                                       f'fontFamily={FONT};fontSize=12;fontColor={t.text};spacing=0;', cx - w / 2, top, w, h)
        return h

    def _num(self, x, y):
        t = self.d.t
        self.n += 1
        self.d.vertex(str(self.n), f'ellipse;aspect=fixed;html=1;fillColor={t.primary};strokeColor={t.bg};strokeWidth=1.5;'
                                   f'fontColor={t.on_primary};fontFamily={FONT};fontSize=10;fontStyle=1;spacing=0;', x - 10, y - 10, 20, 20)

    def msg(self, a, b, text, kind='sync', number=True):
        """kind: sync 实线实心箭头；async 实线空心箭头；ret 虚线返回；fail 以叉收尾。"""
        if a == b:
            return self.self_msg(a, text, number)
        xa, xb = self.x[a], self.x[b]
        h = self._label((xa + xb) / 2, max(abs(xb - xa) + 16, 150), text, self.y)
        y = self.y + h + 5
        arrow = {'async': 'open', 'fail': 'cross'}.get(kind, 'block')
        self.d.line(xa, y, xb, y, dashed=kind == 'ret', arrow=arrow)
        if number:
            self._num(xa, y)
        self.y = y + 24
        return y

    def self_msg(self, a, text, number=True, maxw=None):
        t = self.d.t
        x = self.x[a]
        maxw = maxw or int(self.gap * 1.3)
        h = wrap_lines(text, 12, maxw) * 17
        y = self.y + 6
        self.d.line(x, y, x, y + 22, arrow='block', points=[(x + 32, y), (x + 32, y + 22)])
        self.d.vertex(_esc(text).replace('\n', '<br>'), f'text;html=1;whiteSpace=wrap;align=left;verticalAlign=middle;fontFamily={FONT};'
                                                       f'fontSize=12;fontColor={t.text};spacing=0;', x + 42, y + 11 - h / 2, maxw, h)
        if number:
            self._num(x, y)
        self.y = y + max(22, 11 + h / 2) + 24
        return y

    def space(self, dy):
        self.y += dy

    def note(self, a, b, text, kind='note', pad=70, width=None):
        t = self.d.t
        xa, xb = sorted((self.x[a], self.x[b]))
        left, w = ((xa + xb) / 2 - width / 2, width) if width else (xa - pad, xb - xa + 2 * pad)
        h = wrap_lines(text, 12, w - 24) * 17 + 16
        top = self.y
        fill, stroke, _ = t.roles[kind]
        st = (f'rounded=1;arcSize=6;absoluteArcSize=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};'
              f'fontColor={t.muted if kind == "pending" else t.text};fontFamily={FONT};fontSize=12;align=center;verticalAlign=middle;spacing=8;')
        if kind == 'pending':
            st += 'dashed=1;dashPattern=5 3;'
        self.d.vertex(_esc(text).replace('\n', '<br>'), st, left, top, w, h)
        self.y = top + h + 22
        return top

    def frag(self, kind, cond, a, b, pad=None):
        """开片段（alt / opt / loop），左右跨到参与者 a、b 外侧；用 els 分隔、end 收口。"""
        pad = pad if pad is not None else 100 - len(self.frames) * 24
        xa, xb = sorted((self.x[a], self.x[b]))
        top = self.y
        self.frames.append({'kind': kind, 'top': top, 'left': xa - pad, 'right': xb + pad})
        self._cond(xa - pad, top, kind, cond)
        self.y = top + 40
        return top

    def _cond(self, left, top, kind, cond, divider=False):
        d, t = self.d, self.d.t
        if not divider:
            tw = text_width(kind, 11) + 18
            d.vertex(_esc(kind), f'shape=mxgraph.sysml.package;html=1;labelX={tw};align=left;spacingLeft=8;rounded=0;'
                                 f'fillColor={t.ramp[0]};strokeColor={t.line};strokeWidth=1;fontFamily={FONT};fontSize=11;fontStyle=1;'
                                 f'fontColor={t.text};verticalAlign=middle;', left, top, tw, 22)
            if cond:
                d.text(left + tw + 8, top + 2, text_width(cond, 12) + 16, 18, f'[{cond}]', size=12, color=t.muted)
        else:
            d.text(left + 10, top + 4, text_width(cond, 12) + 16, 18, f'[{cond}]', size=12, color=t.muted)

    def els(self, cond):
        f = self.frames[-1]
        before = len(self.d.cells)
        self.d.line(f['left'], self.y, f['right'], self.y, width=1, dashed=True)
        self._to_bg(before)
        self._cond(f['left'], self.y, f['kind'], cond, divider=True)
        self.y += 40

    def end(self):
        f = self.frames.pop()
        bottom = self.y - 4
        before = len(self.d.cells)
        self.d.vertex('', f'rounded=0;fillColor=none;strokeColor={self.d.t.line};strokeWidth=1;dashed=1;dashPattern=6 4;',
                      f['left'], f['top'], f['right'] - f['left'], bottom - f['top'])
        self._to_bg(before)
        self.y = bottom + 24

    def finish(self, tail=24):
        """画分组底色与生命线并放到最底层；返回时序图底边 y。"""
        d, t = self.d, self.d.t
        bottom = self.y + tail
        before = len(d.cells)
        for label, keys in self.groups:
            xs = [self.x[k] for k in keys]
            left, right = min(xs) - self.head_w / 2 - 16, max(xs) + self.head_w / 2 + 16
            d.vertex(_esc(label), f'rounded=1;arcSize=10;absoluteArcSize=1;html=1;fillColor={t.soft};strokeColor=none;fontColor={t.text};'
                                  f'fontFamily={FONT};fontSize=12;fontStyle=1;align=left;verticalAlign=top;spacingLeft=12;spacingTop=6;',
                     left, self.group_top, right - left, bottom - self.group_top + 10)
        for k in self.order:
            d.line(self.x[k], self.head_bottom, self.x[k], bottom, color=t.stroke('ext'), width=1, dashed=True)
        moved = d.cells[before:]
        del d.cells[before:]
        d.cells[self.bg_at:self.bg_at] = moved + self.bg
        return bottom


def squarify(items, x, y, w, h):
    """矩形树图布局。items: [(键, 值)]，值降序；返回 [(键, x, y, w, h)]。"""
    items = [it for it in items if it[1] > 0]
    total = sum(v for _, v in items)
    rest = [(k, v * w * h / total) for k, v in items]
    out, row = [], []

    def worst(r, side):
        s = sum(a for _, a in r)
        return max(side * side * max(a for _, a in r) / (s * s), (s * s) / (side * side * min(a for _, a in r)))

    def layout(r, x, y, w, h):
        s = sum(a for _, a in r)
        if w >= h:
            cw, cy = s / h, y
            for k, a in r:
                out.append((k, x, cy, cw, a / cw))
                cy += a / cw
            return x + cw, y, w - cw, h
        ch, cx = s / w, x
        for k, a in r:
            out.append((k, cx, y, a / ch, ch))
            cx += a / ch
        return x, y + ch, w, h - ch

    while rest:
        side = min(w, h)
        if not row or worst(row + [rest[0]], side) <= worst(row, side):
            row.append(rest.pop(0))
        else:
            x, y, w, h = layout(row, x, y, w, h)
            row = []
    if row:
        layout(row, x, y, w, h)
    return out
