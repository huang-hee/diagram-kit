#!/usr/bin/env python3
"""需求图（SysML）：每个需求一张卡片（id、风险、验证方式），设计元素和测试用虚线追踪到需求，线上写关系词。

用到：table（sub 写 «requirement» 等构造型）、rel（depend 带关系词）、panel、legend、footer。
运行后在本目录生成 requirement.drawio 和 requirement.png。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
from drawio_kit import Diagram  # noqa: E402

MIN_SIDE = int(os.environ.get('DIAGRAM_MIN_SIDE', 4000))

d = Diagram('下单需求追踪', '下单需求由什么代码满足、由什么测试验证，派生出哪条性能需求')
req = d.table(360, 120, 280, '用户可提交订单', ['id = R1', 'risk = high', 'verifymethod = test'], role='lav', sub='«requirement»')
perf = d.table(760, 120, 280, '下单接口 300ms 内响应', ['id = R1.1', 'risk = medium', 'verifymethod = analysis'], role='apricot', sub='«performanceRequirement»')
api = d.table(360, 340, 280, 'order_api', ['type = code', 'OrderController.create'], role='mint', sub='«element»')
test = d.table(760, 340, 280, 'order_test', ['type = test case', 'OrderApiTest'], role='mint', sub='«element»')

d.rel(api, req, 'depend', '«satisfies»', src='T', dst='B')
d.rel(test, perf, 'depend', '«verifies»', src='T', dst='B')
d.rel(perf, req, 'depend', '«derives»', src='L', dst='R')

y = d.panel(40, 120, 280, '范围', ['只画有追踪价值的关系', '需求清单本身在需求文档里'])
d.panel(40, y + 20, 280, '不在这张图里', ['登录、支付的需求'], kind='soft')
d.legend(40, 520, [('lav', '需求'), ('apricot', '派生的性能需求'), ('mint', '设计元素 / 测试'), ('edge-dashed-open', '追踪关系，线上是关系词')])
d.footer(40, 552, '读图：卡片里是需求的编号、风险和验证方式；虚线箭头从满足方或验证方指向需求。')

name = os.path.join(HERE, 'requirement')
d.save(name + '.drawio')
d.export(name + '.drawio', name + '.png', scale=d.scale_for(MIN_SIDE))
