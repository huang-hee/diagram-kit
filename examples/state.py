#!/usr/bin/env python3
"""状态图：起点实心圆，终点外环加实心圆，状态用圆角卡片，转移线写触发条件，终态按状态色上色。

用到：dot 起止、状态色 ok / bad、key 当前关注的状态、回环拐点。
运行后在本目录生成 state.drawio 和 state.png。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
from drawio_kit import Diagram  # noqa: E402

MIN_SIDE = int(os.environ.get('DIAGRAM_MIN_SIDE', 4000))

d = Diagram('订单状态', '订单从创建到结束会经过哪些状态，由什么触发')
start = d.dot(140, 120, 'start')
pending = d.box(60, 190, 180, 56, '待支付', '创建后 30 分钟内', role='lav')
paid = d.box(60, 320, 180, 56, '已支付', '收到支付回调', role='key')
done = d.box(60, 450, 180, 56, '已完成', '确认收货', role='ok')
cancelled = d.box(360, 320, 180, 56, '已取消', '超时或用户取消', role='bad')
end = d.dot(140, 560, 'end')

d.edge(start, pending, src='B', dst='T')
d.edge(pending, paid, '支付成功', src='B', dst='T')
d.edge(pending, cancelled, '超时', src='R', dst='T', points=[(450, 218)])
d.edge(paid, done, '确认收货', src='B', dst='T')
d.edge(done, end, src='B', dst='T')
d.edge(cancelled, end, src='B', dst='R', points=[(450, 571)])

y = d.panel(620, 120, 420, '规则', ['待支付超过 30 分钟自动取消', '已支付的订单只能走售后，不能取消'])
d.panel(620, y + 20, 420, '不在这张图里', ['售后、退款的子状态'], kind='soft')
d.legend(60, 620, [('lav', '普通状态'), ('key', '关注的状态'), ('ok', '正常终态'), ('bad', '异常终态')])
d.footer(60, 652, '读图：实心圆是起点，外环圆是终点；线上文字是触发转移的事件。')

name = os.path.join(HERE, 'state')
d.save(name + '.drawio')
d.export(name + '.drawio', name + '.png', scale=d.scale_for(MIN_SIDE))
