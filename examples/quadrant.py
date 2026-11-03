#!/usr/bin/env python3
"""象限图：四个象限用主色渐层的浅底，元素是编号圆点加短标签，坐标轴写清两端含义，右侧面板列评分口径和编号对照。

用到：rect 象限底、line 坐标轴（带箭头）、text 刻度和标签、badge 编号点、panel 两块说明。
运行后在本目录生成 quadrant.drawio 和 quadrant.png。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
from drawio_kit import Diagram, P  # noqa: E402

MIN_SIDE = int(os.environ.get('DIAGRAM_MIN_SIDE', 4000))

d = Diagram('需求优先级评估', '先定评分口径，再按价值和成本排出先做什么')
X0, Y0, S = 110, 140, 480  # 象限区左上角与边长
H = S / 2
# 四个象限：左上最深（先做）> 右上 > 右下 > 左下，颜色取主色渐层
QUADS = [((X0, Y0), 'ramp:3', '优先交付', '高价值 · 低成本'), ((X0 + H, Y0), 'ramp:2', '战略投入', '高价值 · 高成本'),
         ((X0, Y0 + H), 'ramp:0', '顺手优化', '低价值 · 低成本'), ((X0 + H, Y0 + H), 'ramp:1', '暂缓投入', '低价值 · 高成本')]
for (x, y), paint, title, sub in QUADS:
    fill, _, color = P.paint(d.t.s, paint)
    d.rect(x, y, H, H, fill, stroke=d.t.bg)
    d.text(x + 14, y + 10, H - 28, 22, title, size=13, color=color, bold=True)
    d.text(x + 14, y + 32, H - 28, 18, sub, size=11, color=color)
# 坐标轴：左边和底边，带箭头；刻度 1–5
d.line(X0, Y0 + S, X0, Y0 - 16, width=1.5, arrow='block')
d.line(X0, Y0 + S, X0 + S + 16, Y0 + S, width=1.5, arrow='block')
for k in range(1, 6):
    t = (k - 1) / 4 * S
    d.text(X0 - 34, Y0 + S - t - 9, 24, 18, str(k), size=11, color=d.t.muted, align='right')
    d.text(X0 + t - 12, Y0 + S + 6, 24, 18, str(k), size=11, color=d.t.muted, align='center')
d.text(X0 - 40, Y0 - 44, 120, 20, '价值 V ↑', size=12, bold=True)
d.text(X0 + S - 120, Y0 + S + 26, 140, 20, '实现成本 E →', size=12, bold=True, align='right')

# 需求：编号、名称、价值 V、成本 E（1–5 分）
ITEMS = [('A', '自助重置密码', 4.3, 1.5), ('B', '工单超时提醒', 3.6, 2.5), ('C', '单点登录', 4.2, 3.6),
         ('D', '跨系统审批', 3.8, 4.4), ('E', '通知文案优化', 2.3, 1.6), ('F', '列表排序', 1.6, 2.4),
         ('G', '全站动效改版', 2.4, 3.6), ('H', '多主题皮肤', 1.4, 4.5)]
for key, name, v, e in ITEMS:
    px = X0 + (e - 1) / 4 * S
    py = Y0 + S - (v - 1) / 4 * S
    d.badge(px - 13, py - 13, key, role='key')
    d.text(px + 16, py - 18, 150, 36, f'<b>{name}</b><br><span style="font-size:11px;color:{d.t.muted}">V {v} / E {e}</span>',
           size=12, html=True)

PX = X0 + S + 80
y = d.panel(PX, Y0 - 20, 420, '评分依据', ['价值 V = 0.4 × 用户收益 + 0.35 × 业务收益 + 0.25 × 战略匹配',
                                           '成本 E = 0.5 × 开发 + 0.3 × 联调测试 + 0.2 × 上线运维', '各项 1–5 分，3 为分界'])
d.panel(PX, y + 20, 420, '编号对照', [f'{k}  {n}　V {v} / E {e}' for k, n, v, e in ITEMS], kind='soft')
d.legend(X0, Y0 + S + 60, [('key', '需求，编号见右侧对照')])
d.footer(X0, Y0 + S + 92, '读图：横轴是实现成本，纵轴是价值；左上象限先做，圆点位置就是综合评分。')

name = os.path.join(HERE, 'quadrant')
d.save(name + '.drawio')
d.export(name + '.drawio', name + '.png', scale=d.scale_for(MIN_SIDE))
