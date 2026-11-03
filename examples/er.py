#!/usr/bin/env python3
"""ER 图：每个实体是一张表格卡片，表头用角色色，主键加粗、外键次要色，关系线标注基数。

用到：table（pk / fk / sep / muted）、ER 鸟足箭头、key 核心实体。
运行后在本目录生成 er.drawio 和 er.png。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
from drawio_kit import Diagram  # noqa: E402

MIN_SIDE = int(os.environ.get('DIAGRAM_MIN_SIDE', 4000))

d = Diagram('订单数据模型', '用户、订单、订单项之间的关系和关键字段')
users = d.table(40, 120, 240, 'USERS', [('id  bigint', 'pk'), 'mobile  varchar', ('', 'sep'), ('created_at  datetime', 'muted')],
                role='lav', sub='用户')
orders = d.table(400, 120, 260, 'ORDERS', [('id  bigint', 'pk'), ('user_id  bigint', 'fk'), 'status  tinyint',
                                           'amount  decimal(12,2)', ('', 'sep'), ('created_at  datetime', 'muted')],
                 role='key', sub='核心实体')
items = d.table(780, 120, 260, 'ORDER_ITEM', [('id  bigint', 'pk'), ('order_id  bigint', 'fk'), 'sku_id  bigint', 'quantity  int'],
                role='mint', sub='订单项')

d.edge(users, orders, '下单', src='R', dst='L', arrow='ERoneToMany', start_arrow='ERmandOne')
d.edge(orders, items, '包含', src='R', dst='L', arrow='ERoneToMany', start_arrow='ERmandOne')

y = d.panel(40, 330, 560, '约定', ['主键加粗，外键用次要字色', '金额统一 decimal(12,2)，时间统一 datetime'])
d.legend(40, y + 24, [('lav', '实体'), ('key', '核心实体'), ('mint', '关联实体')])
d.footer(40, y + 56, '读图：线两端的符号表示 1 对多；表头颜色是实体角色，主色是核心实体。')

name = os.path.join(HERE, 'er')
d.save(name + '.drawio')
d.export(name + '.drawio', name + '.png', scale=d.scale_for(MIN_SIDE))
