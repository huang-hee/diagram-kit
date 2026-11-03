#!/usr/bin/env python3
"""放射图：思维导图的单层变体，中心圆用强调色，一圈圆形节点按系列色轮换，直线连到中心。

用到：mindmap(sides='radial')、标签换行、pending 待定项、按 bounds 定位说明区。
运行后在本目录生成 mindmap_radial.drawio 和 mindmap_radial.png。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
from drawio_kit import Diagram  # noqa: E402

MIN_SIDE = int(os.environ.get('DIAGRAM_MIN_SIDE', 4000))

d = Diagram('发布前检查项', '一次发布前要确认的十一件事，每件都要有人签字')
d.mindmap('发布前\n检查', [
    '代码评审', '单元测试', '回归用例', '变更记录', '灰度名单', '回滚脚本',
    '监控告警', '容量评估', '安全扫描', '文档更新', ('压测报告', [], {'pending': True}),
], cx=620, top=130, sides='radial')

y = (d.bounds[3] // 10 + 4) * 10  # 说明区贴在主体下方
d.legend(40, y, [('pending', '待确认')])
d.footer(40, y + 32, '读图：中心是主题，一圈是同一层的检查项，没有先后顺序；虚线圆是还没定下来的项。')

name = os.path.join(HERE, 'mindmap_radial')
d.save(name + '.drawio')
d.export(name + '.drawio', name + '.png', scale=d.scale_for(MIN_SIDE))
