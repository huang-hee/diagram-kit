#!/usr/bin/env python3
"""C4 容器图：人在左、系统边界在中间、外部系统在右；关系线写"动词 + 协议"。

用到：actor、group（dashed 边界）、box（cyl）、ext 外部系统、带标签的 edge、panel、legend、footer。
运行后在本目录生成 c4.drawio 和 c4.png。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
from drawio_kit import Diagram  # noqa: E402

MIN_SIDE = int(os.environ.get('DIAGRAM_MIN_SIDE', 4000))

d = Diagram('电商系统容器图', 'C4 第二层：系统里有哪些可独立部署的容器，谁调用谁')
customer = d.actor(80, 250, '顾客', '下单的人')
d.group(260, 120, 700, 300, '电商系统 · 系统边界', dashed=True)
web = d.box(290, 170, 220, 64, 'Web 前端', '容器 · React', role='peach')
order = d.box(700, 170, 220, 64, '订单服务', '容器 · Spring Boot', role='key')
db = d.box(700, 320, 220, 70, '业务库', '容器 · MySQL', role='mint', shape='cyl')
pay = d.box(1100, 170, 200, 64, '支付平台', '外部系统', role='ext')

d.edge(customer, web, '使用 · HTTPS', src='R', dst='L')
d.edge(web, order, '调用 API · HTTPS', src='R', dst='L')
d.edge(order, db, '读写 · JDBC', src='B', dst='T', label_offset=0)
d.edge(order, pay, '发起支付 · HTTPS', src='R', dst='L')

y = d.panel(40, 460, 600, 'C4 层级', ['这张是 Container 层：只画容器，不画容器里的组件', '上一层 Context 只有系统和外部，下一层 Component 展开订单服务'])
d.panel(680, 460, 620, '不在这张图里', ['消息队列、缓存', '运维与发布流水线'], kind='soft', h=y - 460)
d.legend(40, y + 24, [('peach', '前端容器'), ('key', '服务容器'), ('mint', '存储容器'), ('ext', '外部系统'), ('edge', '调用，标注动词和协议')])
d.footer(40, y + 56, '读图：虚线框是系统边界，框内是容器；人和外部系统在框外；线上文字是动词加协议。')

name = os.path.join(HERE, 'c4')
d.save(name + '.drawio')
d.export(name + '.drawio', name + '.png', scale=d.scale_for(MIN_SIDE))
