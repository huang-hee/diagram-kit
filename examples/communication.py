#!/usr/bin/env python3
"""通信图（UML）：对象写成 :类名，连线上写编号消息（1、1.1、1.1.1），关键消息的接收方用主色。

用到：actor、box、带编号标签的 edge、panel、legend、footer。
运行后在本目录生成 communication.drawio 和 communication.png。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
from drawio_kit import Diagram  # noqa: E402

MIN_SIDE = int(os.environ.get('DIAGRAM_MIN_SIDE', 4000))

d = Diagram('下单的对象协作', '一次下单里哪些对象互相发消息，顺序编号是什么')
user = d.actor(80, 270, '用户')  # 小人中线对齐到 288，和控制器卡片一条直线
ctrl = d.box(240, 260, 200, 56, ':OrderController', '接口层', role='lav')
svc = d.box(560, 260, 200, 56, ':OrderService', '领域层', role='lav')
stock = d.box(880, 160, 200, 56, ':StockService', '库存', role='lav')
pay = d.box(880, 360, 200, 56, ':PayClient', '支付', role='key')

d.edge(user, ctrl, '1: 下单', src='R', dst='L', label_offset=-0.4)
d.edge(ctrl, svc, '1.1: create()', src='R', dst='L')
d.edge(svc, stock, '1.1.1: lock()', src='T', dst='L', points=[(660, 188)])
d.edge(svc, pay, '1.1.2: pay()', src='B', dst='L', points=[(660, 388)])

y = d.panel(40, 480, 560, '编号规则', ['数字按嵌套层级：1 发起，1.1 是它引出的调用，1.1.1 再往下一层', '同一层按先后顺序递增'])
d.panel(640, 480, 440, '对照', ['同一场景的时间顺序见时序图示例'], kind='soft', h=y - 480)
d.legend(40, y + 24, [('lav', '对象'), ('key', '关键消息的接收方'), ('edge', '消息，线上是编号和方法')])
d.footer(40, y + 56, '读图：按编号读顺序，1.1 在 1 之后、1.1.1 在 1.1 之后；主色对象是本次关注的支付调用。')

name = os.path.join(HERE, 'communication')
d.save(name + '.drawio')
d.export(name + '.drawio', name + '.png', scale=d.scale_for(MIN_SIDE))
