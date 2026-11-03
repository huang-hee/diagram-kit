#!/usr/bin/env python3
"""交互概览图（UML）：用活动图的控制流把 ref / sd 片段串起来，片段框左上角带标签，不通过时回到上一个片段。

用到：dot、frame（ref / sd 标签）、box（diamond）、带拐点的回退 edge、panel、legend、footer。
运行后在本目录生成 interaction.drawio 和 interaction.png。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
from drawio_kit import Diagram  # noqa: E402

MIN_SIDE = int(os.environ.get('DIAGRAM_MIN_SIDE', 4000))

d = Diagram('登录与下单的交互概览', '两段交互怎么串起来，没登录时回到哪里')
X = 200
start = d.dot(X + 109, 120, 'start')  # 圆直径 22，x 取 309 让圆心对齐框的中线 320
login = d.frame(X, 180, 240, 72, 'ref', '登录', '引用已有的登录时序图', role='lav')
dec = d.box(X + 20, 300, 200, 88, '已登录?', role='apricot', shape='diamond')
order = d.frame(X, 440, 240, 72, 'sd', '下单', '内联片段：提交订单 → 支付', role='key')
end = d.dot(X + 109, 560, 'end')

d.edge(start, login, src='B', dst='T')
d.edge(login, dec, src='B', dst='T')
d.edge(dec, order, '是', src='B', dst='T', label_offset=-0.3)
d.edge(order, end, src='B', dst='T')
d.edge(dec, login, '否', src='R', dst='R', points=[(540, 344), (540, 216)], dashed=True, label_offset=-0.4)

y = d.panel(640, 120, 420, '片段对照', ['ref 登录 → 时序图「登录」', 'sd 下单 → 时序图「下单与支付回调」'])
d.panel(640, y + 20, 420, '不在这张图里', ['注册、找回密码的交互'], kind='soft')
d.legend(X, 620, [('lav', 'ref 引用片段'), ('key', 'sd 内联片段'), ('apricot', '判断'), ('edge', '控制流'), ('edge-dashed', '回退')])
d.footer(X, 652, '读图：和活动图一样自上而下；框左上角的 ref / sd 说明这是引用还是内联的交互片段。')

name = os.path.join(HERE, 'interaction')
d.save(name + '.drawio')
d.export(name + '.drawio', name + '.png', scale=d.scale_for(MIN_SIDE))
