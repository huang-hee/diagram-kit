"""思维导图（drawio_kit）：中心主题用主色胶囊，一级分支左右均分、深色实底白字，二级浅底，连线是分支色的正交肘线。"""
import os
import sys

sys.path.insert(0, '$SKILL/scripts')
from drawio_kit import Diagram  # noqa: E402

MIN_SIDE = int(os.environ.get('DIAGRAM_MIN_SIDE', 4000))

d = Diagram('接手新项目', '接手一个项目要先弄清哪几方面')
d.mindmap('接手新项目', [
    ('业务', ['核心流程', '关键术语']),
    ('代码', ['目录结构', '分层约定']),
    ('环境', ['本地启动', '发布流程']),
    ('人', ['负责人', '对接方']),
], cx=520, top=130)
d.footer(40, (d.bounds[3] // 10 + 4) * 10, '读图：中心是主题，四个一级分支各一种颜色，二级节点沿用分支色。')

d.save('mindmap.drawio')
d.export('mindmap.drawio', 'mindmap.png', scale=d.scale_for(MIN_SIDE))
