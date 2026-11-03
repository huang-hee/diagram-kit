#!/usr/bin/env python3
"""部署图（UML）：设备节点用立方体，执行环境和制品依次嵌套在里面，网络边界用虚线框，节点之间标通信协议。

用到：group（dashed 网络边界）、box（shape='cube' / 'doc'）嵌套、edge（label 协议）、panel、legend、footer。
运行后在本目录生成 uml_deploy.drawio 和 uml_deploy.png。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
from drawio_kit import Diagram  # noqa: E402

MIN_SIDE = int(os.environ.get('DIAGRAM_MIN_SIDE', 4000))

d = Diagram('订单服务部署图', '订单服务的制品跑在哪台设备的哪个执行环境里，和数据库怎么通信')
d.group(120, 120, 420, 340, '机房网络', dashed=True)
n1 = d.box(160, 170, 340, 250, '应用服务器', '«device»', role='lav', shape='cube', extra='verticalAlign=top;spacingTop=14;')
d.box(200, 240, 260, 150, 'JVM', '«executionEnvironment»', role='peach', extra='verticalAlign=top;spacingTop=8;')
d.box(230, 310, 200, 60, 'order.jar', '«artifact»', role='mint', shape='doc')
n2 = d.box(680, 235, 300, 120, '数据库服务器', '«device» · MySQL 8', role='lav', shape='cube')

d.edge(n1, n2, 'JDBC', src='R', dst='L')  # 两个节点中线都在 295，JDBC 线是直线

y = d.panel(120, 500, 560, '约定', ['一台设备一个立方体，里面从外到内是执行环境、制品', '设备之间的线写通信协议'])
d.panel(720, 500, 260, '对照', ['云上全景见部署架构图'], kind='soft', h=y - 500)
d.legend(120, y + 24, [('lav', '设备'), ('peach', '执行环境'), ('mint', '制品'), ('edge', '通信')])
d.footer(120, y + 56, '读图：立方体是物理或虚拟设备，嵌套表示"跑在里面"；虚线框是网络边界。')

name = os.path.join(HERE, 'uml_deploy')
d.save(name + '.drawio')
d.export(name + '.drawio', name + '.png', scale=d.scale_for(MIN_SIDE))
