#!/usr/bin/env python3
"""包图（UML）：外层包和子包用分组容器嵌套，越往里越浅；叶子包用文件夹形状；依赖是虚线开放箭头。

用到：group 嵌套、box（shape='package'）、rel（depend）、panel、legend、footer。
运行后在本目录生成 package.drawio 和 package.png。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
from drawio_kit import Diagram  # noqa: E402

MIN_SIDE = int(os.environ.get('DIAGRAM_MIN_SIDE', 4000))

d = Diagram('包依赖', 'order 包依赖 user 包的哪一层，有没有反向依赖')
d.group(120, 120, 800, 320, 'com.shop', fill=d.t.soft)
d.group(160, 170, 340, 240, 'order', fill=d.t.bg, stroke=d.t.border)
d.group(540, 170, 340, 240, 'user', fill=d.t.bg, stroke=d.t.border)
o_ctrl = d.box(190, 230, 130, 70, 'controller', role='lav', shape='package', extra='verticalAlign=bottom;spacingBottom=10;')
o_svc = d.box(350, 230, 130, 70, 'service', '关注的包', role='key', shape='package', extra='verticalAlign=bottom;spacingBottom=6;')
u_svc = d.box(610, 230, 130, 70, 'service', role='lav', shape='package', extra='verticalAlign=bottom;spacingBottom=10;')
u_repo = d.box(610, 320, 130, 70, 'repository', role='lav', shape='package', extra='verticalAlign=bottom;spacingBottom=10;')

d.rel(o_ctrl, o_svc, 'depend', src='R', dst='L')
d.rel(o_svc, u_svc, 'depend', src='R', dst='L')
d.rel(u_svc, u_repo, 'depend', src='B', dst='T')

y = d.panel(120, 480, 560, '规则', ['跨包只能依赖对方的 service，不能直接依赖 repository', 'user 不依赖 order，避免循环'])
d.panel(720, 480, 200, '对照', ['类的细节见类图'], kind='soft', h=y - 480)
d.legend(120, y + 24, [('lav', '包'), ('key', '关注的包'), ('edge-dashed-open', '依赖')])
d.footer(120, y + 56, '读图：外层框是顶层包，里面的框是子包；虚线箭头从依赖方指向被依赖方。')

name = os.path.join(HERE, 'package')
d.save(name + '.drawio')
d.export(name + '.drawio', name + '.png', scale=d.scale_for(MIN_SIDE))
