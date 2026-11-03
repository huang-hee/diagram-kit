#!/usr/bin/env python3
"""鱼骨图：鱼头在右，大类上下交替，原因是短横线加右对齐文字。

用到：fishbone、按 bounds 定位说明区。
运行后在本目录生成 fishbone.drawio 和 fishbone.png。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
from drawio_kit import Diagram  # noqa: E402

MIN_SIDE = int(os.environ.get('DIAGRAM_MIN_SIDE', 4000))

d = Diagram('接口 P99 超过 2s 的原因', '从代码、依赖、基础设施、流程四类找原因')
d.fishbone('接口 P99 超过 2s', [
    ('代码', ['N+1 查询', '缺少缓存']),
    ('依赖', ['下游超时', '连接池不够']),
    ('基础设施', ['扩容不及时']),
    ('流程', ['上线前未压测']),
], x=300, y=390, length=900)

y = (d.bounds[3] // 10 + 4) * 10
d.panel(40, y, 560, '已验证', ['N+1 查询：慢查询日志里占 70%', '扩容不及时：高峰期 CPU 持续 90%'])
d.footer(40, y + 110, '读图：右侧鱼头是问题，斜骨是原因大类，横线是具体原因。')

name = os.path.join(HERE, 'fishbone')
d.save(name + '.drawio')
d.export(name + '.drawio', name + '.png', scale=d.scale_for(MIN_SIDE))
