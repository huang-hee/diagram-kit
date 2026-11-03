#!/usr/bin/env python3
"""活动图（UML）：起止实心圆，主路径竖排一列，判断的"否"向右，分叉 / 汇合用粗横条，对象节点用平行四边形。

用到：dot、bar、box（diamond / para）、edge、panel、legend、footer。
运行后在本目录生成 activity.drawio 和 activity.png。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
from drawio_kit import Diagram  # noqa: E402

MIN_SIDE = int(os.environ.get('DIAGRAM_MIN_SIDE', 4000))

d = Diagram('订单处理活动', '接单后怎么判断库存，发货时哪些动作并行')
X = 200  # 主列左边，节点宽 200
start = d.dot(X + 89, 120, 'start')
recv = d.box(X + 20, 180, 160, 56, '接收订单', '校验参数', role='lav')
dec = d.box(X, 276, 200, 88, '库存足够?', role='apricot', shape='diamond')  # y 不取整十：让菱形中线和缺货单对齐在 320
fork = d.bar(X - 80, 400, 360)
ship = d.box(X - 80, 450, 160, 56, '发货', '生成运单', role='lav')
notify = d.box(X + 120, 450, 160, 56, '通知用户', '短信 · 推送', role='lav')
join = d.bar(X - 80, 550, 360)
FX, NX = (200 - 120) / 360, (400 - 120) / 360  # 两条并行分支在横条上的出入口位置：卡片中线相对横条左边的比例
short = d.box(X + 320, 292, 160, 56, '缺货单', '对象节点', role='mint', shape='para')
end = d.dot(X + 89, 600, 'end')

d.edge(start, recv, src='B', dst='T')
d.edge(recv, dec, src='B', dst='T')
d.edge(dec, fork, '是', src='B', dst='T', label_offset=-0.3)
d.edge(fork, ship, src=(FX, 1), dst='T')
d.edge(fork, notify, src=(NX, 1), dst='T')
d.edge(ship, join, src='B', dst=(FX, 0))
d.edge(notify, join, src='B', dst=(NX, 0))
d.edge(join, end, src='B', dst='T')
d.edge(dec, short, '否', src='R', dst='L', label_offset=-0.4)
d.edge(short, end, src='B', dst='R', points=[(600, 611)])

y = d.panel(760, 120, 400, '依据', ['P-03 发货规范：发货与通知并行，都完成才算结束', '缺货单转人工跟进，不阻塞主流程'])
d.panel(760, y + 20, 400, '不在这张图里', ['退款、改地址等异常分支'], kind='soft')
d.legend(X - 80, 660, [('lav', '动作'), ('apricot', '判断'), ('mint', '对象节点'), ('edge', '控制流')])
d.footer(X - 80, 692, '读图：实心圆是开始，外环圆是结束；粗横条之间的动作并行，都完成才汇合。')

name = os.path.join(HERE, 'activity')
d.save(name + '.drawio')
d.export(name + '.drawio', name + '.png', scale=d.scale_for(MIN_SIDE))
