#!/usr/bin/env python3
"""组合结构图（UML）：类元是带边框的大框，部件写成"名称 : 类型"放在里面，端口是边框上的小方块，连接件是无箭头实线。

用到：group（带描边的类元框）、box 部件、port（square 端口）、rel（link）、panel、legend、footer。
运行后在本目录生成 composite.drawio 和 composite.png。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
from drawio_kit import Diagram  # noqa: E402

MIN_SIDE = int(os.environ.get('DIAGRAM_MIN_SIDE', 4000))

d = Diagram('Car 的内部结构', 'Car 由哪些部件组成，通过哪个端口和外部交互')
d.group(200, 120, 560, 170, 'Car', fill=d.t.bg, stroke=d.t.border)
engine = d.box(280, 190, 180, 60, 'engine', ': Engine', role='lav')
wheels = d.box(520, 190, 180, 60, 'wheels', ': Wheel [4]', role='lav')
p = d.port(190, 210, size=20, role='apricot')  # 跨在类元框的左边框上，中线和 engine 对齐
d.text(150, 200, 40, 20, 'p', size=12, bold=True, align='center')
d.text(150, 220, 40, 18, '端口', size=11, color=d.t.muted, align='center')

d.rel(engine, wheels, 'link', '驱动', src='R', dst='L')
d.rel(p, engine, 'link', src='R', dst='L')

y = d.panel(200, 340, 560, '说明', ['部件只在 Car 内部存在，随 Car 创建和销毁', '端口 p 是外部启动引擎的唯一入口'])
d.legend(200, y + 24, [('lav', '部件'), ('apricot', '端口'), ('line', '连接件')])
d.footer(200, y + 56, '读图：大框是类元，框里是它的部件；框边上的小方块是端口，实线是部件之间的连接。')

name = os.path.join(HERE, 'composite')
d.save(name + '.drawio')
d.export(name + '.drawio', name + '.png', scale=d.scale_for(MIN_SIDE))
