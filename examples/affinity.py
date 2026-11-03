#!/usr/bin/env python3
"""亲和图：每组一个分组容器，组名写成一句结论，组内便签保留用户原话，一组一个系列色。

用到：group、sticky（按系列色轮换）、panel、legend、footer。
运行后在本目录生成 affinity.drawio 和 affinity.png。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
from drawio_kit import Diagram, SERIES  # noqa: E402

MIN_SIDE = int(os.environ.get('DIAGRAM_MIN_SIDE', 4000))

d = Diagram('用户反馈归类', '访谈里零散的抱怨归成了哪几个主题')
GROUPS = [
    ('新用户找不到入口', ['"按钮难找"\n访谈提到 3 次', '"首页信息太多"', '"不知道从哪开始"']),
    ('页面慢', ['"首屏 3 秒"\n低端机更慢', '"滚动卡顿"']),
    ('支付体验差', ['"跳转次数多"', '"失败无提示"', '"不支持花呗"']),
]
X0, GW, GAP, Y0 = 40, 340, 24, 120
for i, (conclusion, notes) in enumerate(GROUPS):
    role = SERIES[i % len(SERIES)]
    x = X0 + i * (GW + GAP)
    d.group(x, Y0, GW, 60 + len(notes) * 80 + 10, conclusion)
    for j, note in enumerate(notes):
        d.sticky(x + 20, Y0 + 50 + j * 80, GW - 40, 62, note, role=role)

y = d.panel(X0, 460, 560, '来源', ['12 位用户的访谈记录，共 24 张便签，图里只放归入这三组的', '组名是归纳出的结论，便签是原话'])
d.legend(X0, y + 24, [('lav', '入口问题'), ('peach', '性能问题'), ('mint', '支付问题')])
d.footer(X0, y + 56, '读图：一个框是一组，框名是结论；便签保留原话，引号里的是用户说的。')

name = os.path.join(HERE, 'affinity')
d.save(name + '.drawio')
d.export(name + '.drawio', name + '.png', scale=d.scale_for(MIN_SIDE))
