#!/usr/bin/env python3
"""组件图（UML）：组件用带插头的组件符号，子系统是分组容器，提供的接口画成棒棒糖，依赖用虚线。

用到：group、box（shape='component'）、port（circle 棒棒糖）、rel（link / depend）、panel、legend、footer。
运行后在本目录生成 component.drawio 和 component.png。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
from drawio_kit import Diagram  # noqa: E402

MIN_SIDE = int(os.environ.get('DIAGRAM_MIN_SIDE', 4000))

d = Diagram('订单子系统组件', '子系统里有哪些组件，通过什么接口依赖谁')
d.group(200, 120, 420, 240, '订单子系统')
c1 = d.box(240, 170, 200, 64, '订单组件', '下单 · 查询', role='lav', shape='component', extra='spacingLeft=16;')
c2 = d.box(240, 270, 200, 64, '支付组件', '收银台 · 回调', role='lav', shape='component', extra='spacingLeft=16;')
iface = d.port(700, 293, 'IPayment', size=18, role='apricot', shape='circle')  # y 让圆心对齐支付组件的中线 302
lib = d.box(240, 440, 200, 56, '公共工具库', '日期 · 金额', role='peach')

d.rel(c2, iface, 'link', src='R', dst='L')
d.rel(c1, iface, 'depend', '调用', src='R', dst='T', points=[(709, 202)])
d.rel(c1, lib, 'depend', src='L', dst='L', points=[(220, 202), (220, 468)])

y = d.panel(860, 120, 320, '约定', ['组件之间只通过接口依赖', '公共工具库不反向依赖任何组件'])
d.panel(860, y + 20, 320, '不在这张图里', ['商品、库存子系统'], kind='soft')
d.legend(200, 540, [('lav', '组件'), ('peach', '库'), ('apricot', '接口'), ('line', '提供接口'), ('edge-dashed-open', '依赖')])
d.footer(200, 572, '读图：浅底框是子系统；圆点是接口，实线一端提供它，虚线一端依赖它。')

name = os.path.join(HERE, 'component')
d.save(name + '.drawio')
d.export(name + '.drawio', name + '.png', scale=d.scale_for(MIN_SIDE))
