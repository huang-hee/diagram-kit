#!/usr/bin/env python3
"""对象图（UML）：某一时刻的对象快照，卡片表头写"实例名 : 类名"，每行一个"字段 = 值"；关注的对象用主色。

用到：table、rel（assoc）、panel、legend、footer。
运行后在本目录生成 object.drawio 和 object.png。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
from drawio_kit import Diagram  # noqa: E402

MIN_SIDE = int(os.environ.get('DIAGRAM_MIN_SIDE', 4000))

d = Diagram('一笔已支付订单的对象快照', '支付成功那一刻，订单、用户、金额对象各是什么值')
user1 = d.table(60, 151, 240, 'user1 : User', ['id = 7', 'mobile = 138****0001'], role='lav', sub='对象')
# 两侧卡片比 order1 矮，y 取 151 让中线对齐到 196，链接线才是直线
order1 = d.table(420, 140, 260, 'order1 : Order', ['id = 1001', 'status = PAID', 'created_at = 10:32:05'], role='key', sub='关注的对象')
money = d.table(800, 151, 240, 'amount : Money', ['value = 99.00', 'currency = CNY'], role='mint', sub='值对象')

d.rel(user1, order1, 'assoc', 'user', src='R', dst='L')
d.rel(order1, money, 'assoc', 'amount', src='R', dst='L')

y = d.panel(60, 320, 560, '快照时刻', ['支付回调写入 status = PAID 之后', '值取自测试库里的一笔真实订单'])
d.panel(660, 320, 380, '对照', ['类的定义见类图示例'], kind='soft', h=y - 320)
d.legend(60, y + 24, [('lav', '对象'), ('key', '关注的对象'), ('mint', '值对象'), ('edge-open', '链接，线上是字段名')])
d.footer(60, y + 56, '读图：表头是"实例 : 类"，每行是"字段 = 值"；线上的字段名说明谁持有谁。')

name = os.path.join(HERE, 'object')
d.save(name + '.drawio')
d.export(name + '.drawio', name + '.png', scale=d.scale_for(MIN_SIDE))
