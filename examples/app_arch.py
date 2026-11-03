#!/usr/bin/env python3
"""应用架构图：每层一条横向分层带，层内卡片网格对齐；横切关注点用右侧贯穿条；外部系统灰色放最外侧。

用到：band 分层、vband、ext 外部系统、1/4 端口（TL / TR / BL / BR）、dashed 异步线、key 本次改动。
运行后在本目录生成 app_arch.drawio 和 app_arch.png。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
from drawio_kit import Diagram  # noqa: E402

MIN_SIDE = int(os.environ.get('DIAGRAM_MIN_SIDE', 4000))

d = Diagram('商城应用架构', '系统由哪些应用组成，运行时谁调用谁')
BW = 1000
d.band(40, 120, BW, 110, '前端层', '用户触点')
d.band(40, 250, BW, 210, '服务层', '业务逻辑')
d.band(40, 480, BW, 120, '基础层', '中间件 · 存储')
d.vband(1060, 120, 50, 480, '安全 · 监控')

web = d.box(220, 143, 200, 64, '商城 Web', 'React', role='peach')
mini = d.box(460, 143, 200, 64, '小程序', '微信', role='peach')
gw = d.box(340, 270, 200, 64, 'API 网关', '鉴权 · 限流', role='lav')
goods = d.box(220, 376, 200, 64, '商品服务', '类目 · 库存', role='lav')
order = d.box(460, 376, 200, 64, '订单服务', '下单 · 支付回调', role='key')
mq = d.box(220, 505, 200, 70, 'RocketMQ', '订单事件', role='mint', shape='cyl')
db = d.box(460, 505, 200, 70, 'MySQL', '业务库', role='mint', shape='cyl')
pay = d.box(1150, 376, 200, 64, '支付平台', '外部系统', role='ext')

d.edge(web, gw, src='B', dst='TL')
d.edge(mini, gw, src='B', dst='TR')
d.edge(gw, goods, src='BL', dst='T')
d.edge(gw, order, src='BR', dst='T')
d.edge(goods, db, src='B', dst='TL')
d.edge(order, db, src='B', dst='TR')
d.edge(order, mq, '订单事件', src='BL', dst='TR', dashed=True, label_offset=0.3)
d.edge(order, pay, '发起支付', src='R', dst='L')

y = d.panel(40, 640, 560, '依据', ['A12 服务拆分原则：按业务域拆分', '订单服务是本次改造范围'])
d.panel(640, 640, 560, '不在这张图里', ['CDN、对象存储', '运维与发布流水线'], kind='soft', h=y - 640)
d.legend(40, y + 24, [('peach', '前端'), ('lav', '服务'), ('key', '本次改动'), ('mint', '中间件 / 存储'),
                      ('ext', '外部系统'), ('edge', '同步调用'), ('edge-dashed', '异步消息')])
d.footer(40, y + 56, '读图：横带是分层，自上而下是调用方向；右侧竖条贯穿所有层；灰色是外部系统。')

name = os.path.join(HERE, 'app_arch')
d.save(name + '.drawio')
d.export(name + '.drawio', name + '.png', scale=d.scale_for(MIN_SIDE))
