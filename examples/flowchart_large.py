#!/usr/bin/env python3
"""超过 12 个节点的流程图：主路径竖排一列，产出文档用虚线挂在右侧文档列，回退路径走左侧通道，依据面板在右。

用到：按中线循环摆主路径、doc 形状、dashed 虚线、显式拐点的回退线、1/4 端口避免同一边多线重叠。
运行后在本目录生成 flowchart_large.drawio 和 flowchart_large.png。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
from drawio_kit import Diagram  # noqa: E402

MIN_SIDE = int(os.environ.get('DIAGRAM_MIN_SIDE', 4000))

d = Diagram('项目交付流程', '从需求到上线经过哪些步骤，哪里会回退，各步产出什么文档')
X, DX, W = 360, 660, 200  # 主路径列、文档列的左边，节点宽
PITCH = 100  # 相邻节点中线间距


def cy(i):
    return 142 + i * PITCH


# 主路径：('节点', 类型, 右侧文档)
STEPS = [('项目启动', 'pill', None), ('需求调研', 'box', '调研报告'), ('需求评审通过?', 'diamond', None),
         ('UI 设计', 'box', '设计稿'), ('开发计划', 'box', '开发计划表'), ('编码开发', 'box', None),
         ('自测通过?', 'diamond', None), ('功能测试', 'box', '测试报告'), ('测试通过?', 'diamond', None),
         ('部署上线', 'box', '上线通知'), ('线上验证', 'box', None), ('项目总结', 'pill', None)]
ids = []
for i, (label, kind, doc) in enumerate(STEPS):
    c = cy(i)
    if kind == 'pill':
        nid = d.box(X + 20, c - 22, 160, 44, label, role='peach', shape='pill')
    elif kind == 'diamond':
        nid = d.box(X, c - 44, W, 88, label, role='apricot', shape='diamond')
    else:
        nid = d.box(X, c - 28, W, 56, label, role='lav')
    ids.append(nid)
    if doc:
        did = d.box(DX, c - 28, 180, 56, doc, role='mint', shape='doc')
        d.edge(nid, did, src='R', dst='L', dashed=True, arrow='open')

# 主路径连线：判断的"是"向下
for i in range(len(STEPS) - 1):
    label = '是' if STEPS[i][1] == 'diamond' else None
    d.edge(ids[i], ids[i + 1], label, src='B', dst='T', label_offset=-0.3 if label else None)
# 回退：判断的"否"从左侧通道绕回去；两条回到同一节点时用不同的 1/4 端口和通道
d.edge(ids[2], ids[1], '否', src='L', dst='L', points=[(280, cy(2)), (280, cy(1))], dashed=True)
d.edge(ids[6], ids[5], '否', src='L', dst='LB', points=[(280, cy(6)), (280, cy(5) + 14)], dashed=True)
d.edge(ids[8], ids[5], '否', src='L', dst='LT', points=[(200, cy(8)), (200, cy(5) - 14)], dashed=True)

y = d.panel(900, 120, 360, '依据', ['P-07 项目交付规范', '评审不通过回到调研，自测或测试不通过回到编码'])
d.panel(900, y + 20, 360, '不在这张图里', ['需求变更流程', '事故复盘'], kind='soft')
d.legend(200, cy(len(STEPS) - 1) + 60, [('peach', '起止'), ('lav', '步骤'), ('apricot', '判断'), ('mint', '产出文档'),
                                         ('edge', '顺序'), ('edge-dashed', '回退 / 产出')])
d.footer(200, cy(len(STEPS) - 1) + 92, '读图：自上而下是主路径，右侧是每步的产出文档，左侧虚线是不通过时回退到哪一步。')

name = os.path.join(HERE, 'flowchart_large')
d.save(name + '.drawio')
d.export(name + '.drawio', name + '.png', scale=d.scale_for(MIN_SIDE))
