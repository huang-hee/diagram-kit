#!/usr/bin/env python3
"""类图：每个类一张表格卡片（表头按角色上色，字段和方法用分隔线隔开），关系线用 UML 箭头。

用到：table（sep 分隔字段和方法、sub 写构造型）、rel（inherit / assoc / depend）、panel、legend、footer。
运行后在本目录生成 class.drawio 和 class.png。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
from drawio_kit import Diagram  # noqa: E402

MIN_SIDE = int(os.environ.get('DIAGRAM_MIN_SIDE', 4000))

d = Diagram('订单领域类图', '下单涉及哪些类，谁继承谁、谁依赖谁')
handler = d.table(420, 120, 240, 'AbstractHandler', ['+handle() void'], role='sage', sub='«abstract»')
service = d.table(420, 260, 240, 'OrderService', ['+createOrder() Order', '+pay(Order) PayResult'], role='key', sub='本次改动')
# 三张卡片高度不同，y 按中线对齐到 OrderService 的 305，连线才是直线
gateway = d.table(780, 271, 260, 'PaymentGateway', ['+pay(Order) PayResult'], role='apricot', sub='«interface»')
order = d.table(60, 245, 260, 'Order', ['-Long id', '-OrderStatus status', ('', 'sep'), '+pay() void'], role='lav')
status = d.table(60, 460, 260, 'OrderStatus', ['PENDING', 'PAID'], role='mint', sub='«enumeration»')

d.rel(service, handler, 'inherit', src='T', dst='B')
d.rel(service, gateway, 'assoc', '调用', src='R', dst='L')
d.rel(service, order, 'depend', '创建', src='L', dst='R')
d.rel(order, status, 'assoc', src='B', dst='T')

y = d.panel(420, 460, 620, '范围', ['只画本次下单改动涉及的类和成员', '支付网关是接口，实现类在支付模块里'])
d.legend(60, y + 24, [('lav', '类'), ('key', '本次改动'), ('apricot', '接口'), ('mint', '枚举'), ('sage', '抽象类'), ('edge-open', '关联'), ('edge-dashed-open', '依赖')])
d.footer(60, y + 56, '读图：空心三角指向父类；开放箭头的实线是关联，虚线是依赖；表头颜色是类的种类。')

name = os.path.join(HERE, 'class')
d.save(name + '.drawio')
d.export(name + '.drawio', name + '.png', scale=d.scale_for(MIN_SIDE))
