#!/usr/bin/env python3
"""思维导图：中心主题用主色胶囊，一级分支按系列色深色实底，二级浅底，待定项灰色虚线。

用到：mindmap、pending 待定项、按 bounds 定位说明区。
运行后在本目录生成 mindmap.drawio 和 mindmap.png。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
from drawio_kit import Diagram  # noqa: E402

MIN_SIDE = int(os.environ.get('DIAGRAM_MIN_SIDE', 4000))

d = Diagram('接手新项目的梳理清单', '接手一个项目要先弄清哪几方面')
d.mindmap('接手新项目', [
    ('业务', ['核心流程', '关键术语', ('历史包袱', [], {'pending': True})]),
    ('代码', ['目录结构', '分层约定', '构建与测试']),
    ('环境', ['本地启动', '发布流程']),
    ('人', ['负责人', '对接方']),
], cx=640, top=130)

y = (d.bounds[3] // 10 + 4) * 10  # 说明区贴在主体下方
d.legend(40, y, [('pending', '待确认')])
d.footer(40, y + 32, '读图：一级分支按颜色区分，二级是浅底；虚线框是还没确认的项。')

name = os.path.join(HERE, 'mindmap')
d.save(name + '.drawio')
d.export(name + '.drawio', name + '.png', scale=d.scale_for(MIN_SIDE))
