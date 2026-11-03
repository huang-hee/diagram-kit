#!/usr/bin/env python3
"""树形图 / 组织结构图：根用强调色，一级按系列色轮换，二级浅底；总线式肘线；虚线汇报的助理挂在根旁边。

用到：tree_down、虚线 edge 表示虚线汇报、panel、legend、footer。
运行后在本目录生成 org.drawio 和 org.png。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
from drawio_kit import Diagram  # noqa: E402

MIN_SIDE = int(os.environ.get('DIAGRAM_MIN_SIDE', 4000))

d = Diagram('公司组织结构', '各中心向谁汇报，下面分哪些组')
X0, Y0 = 60, 130
root, W, H, (rx, ry, rw, rh) = d.tree_down('总经理', [
    ('技术中心\n研发 · 测试 · 运维', ['前端组', '后端组', '测试组']),
    ('运营中心\n内容 · 活动', ['内容运营', '活动运营']),
], X0, Y0, gap_x=24, gap_y=50, node_h=56)

# 助理：虚线汇报，挂在根右侧
aide = d.box(rx + rw + 110, ry + 8, 150, 40, '总经理助理', role='white', dashed=True, bold=False)
d.edge(root, aide, src='R', dst='L', dashed=True, arrow='none')

y = (Y0 + H) // 10 * 10 + 40
y2 = d.panel(X0, y, 420, '口径', ['按汇报线画，不画项目组这类临时组织', '虚线是行政汇报，不带管理权限'])
d.legend(X0, y2 + 24, [('key', '最高负责人'), (('color', d.t.deep('lav')), '技术线'), (('color', d.t.deep('peach')), '运营线'), ('line-dashed', '虚线汇报')])
d.footer(X0, y2 + 56, '读图：自上而下是汇报关系；一级按颜色区分条线，二级沿用条线色的浅底。')

name = os.path.join(HERE, 'org')
d.save(name + '.drawio')
d.export(name + '.drawio', name + '.png', scale=d.scale_for(MIN_SIDE))
