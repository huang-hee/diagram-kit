#!/usr/bin/env python3
"""用例图：参与者（小人）在边界外，用例是胶囊卡片排在系统边界里，扩展关系用虚线并标 «extend»。

用到：actor、group（dashed 系统边界）、box（pill）、edge（dashed + open 箭头）、panel、legend、footer。
运行后在本目录生成 usecase.drawio 和 usecase.png。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
from drawio_kit import Diagram  # noqa: E402

MIN_SIDE = int(os.environ.get('DIAGRAM_MIN_SIDE', 4000))

d = Diagram('电商系统用例', '顾客能用系统做什么，哪些功能是可选扩展')
customer = d.actor(80, 250, '顾客')
d.group(260, 120, 520, 400, '电商系统', dashed=True)
browse = d.box(400, 170, 220, 52, '浏览商品', '搜索 · 按类目筛选', role='lav', shape='pill')
order = d.box(400, 280, 220, 52, '下单', '选地址 · 提交', role='lav', shape='pill')
coupon = d.box(400, 420, 220, 52, '使用优惠券', '扩展用例', role='apricot', shape='pill')

d.edge(customer, browse, src=(1, 0.3), dst='L', arrow='none')
d.edge(customer, order, src=(1, 0.7), dst='L', arrow='none')
d.edge(coupon, order, '«extend»', src='T', dst='B', dashed=True, arrow='open')

y = d.panel(840, 120, 320, '边界', ['只画顾客侧的用例', '支付由外部支付平台完成，不在系统边界内'])
d.panel(840, y + 20, 320, '不在这张图里', ['运营后台的用例', '客服工单'], kind='soft')
d.legend(80, 580, [('lav', '用例'), ('apricot', '扩展用例'), ('line', '参与者关联'), ('edge-dashed-open', '«extend» 扩展')])
d.footer(80, 612, '读图：小人是参与者，虚线框是系统边界；实线是参与者能做的事，虚线箭头是可选的扩展。')

name = os.path.join(HERE, 'usecase')
d.save(name + '.drawio')
d.export(name + '.drawio', name + '.png', scale=d.scale_for(MIN_SIDE))
