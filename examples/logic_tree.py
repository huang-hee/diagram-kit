#!/usr/bin/env python3
"""右展开逻辑树：根在左，一级分支按系列色深色实底，二级浅底，三级白底描边，正交肘线。

用到：mindmap(sides='right') 当横向树、三层嵌套、pending 待定项、按 bounds 定位说明区。
运行后在本目录生成 logic_tree.drawio 和 logic_tree.png。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
from drawio_kit import Diagram  # noqa: E402

MIN_SIDE = int(os.environ.get('DIAGRAM_MIN_SIDE', 4000))

d = Diagram('技术方案评审清单', '评审一份技术方案要从哪几方面看、各看什么')
d.mindmap('方案评审', [
    ('需求与范围', [('目标是否可衡量', ['有指标', '有基线']), '边界写清不做什么', ('历史兼容', [], {'pending': True})]),
    ('架构与依赖', [('服务拆分', ['按业务域', '无循环依赖']), ('外部依赖', ['超时与降级', '限流']), '单点与容灾']),
    ('数据与接口', [('表设计', ['主键与索引', '扩展字段']), ('接口契约', ['幂等', '版本兼容']), '数据迁移']),
    ('非功能', [('性能', ['容量估算', '压测计划']), '安全与权限', '可观测性']),
    ('发布与回滚', ['灰度策略', '回滚步骤', ('开关与配置', [], {'pending': True})]),
], cx=130, top=130, sides='right')

y = (d.bounds[3] // 10 + 4) * 10
d.legend(40, y, [('pending', '待确认')])
d.footer(40, y + 32, '读图：从左向右展开，一级分支按颜色区分，二级浅底、三级白底；虚线框是还没确认的项。')

name = os.path.join(HERE, 'logic_tree')
d.save(name + '.drawio')
d.export(name + '.drawio', name + '.png', scale=d.scale_for(MIN_SIDE))
