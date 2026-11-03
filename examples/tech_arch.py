#!/usr/bin/env python3
"""技术架构图：左列是层名，右侧是该层选用的技术组件，白底卡片；横切能力单独放最下一行（和指南第 3 节的 Mermaid 示例一致，
不用 design-rules 里分层架构的右侧贯穿条）；本次引入的组件用主色。

用到：band、box（white / key）、panel、legend、footer。
运行后在本目录生成 tech_arch.drawio 和 tech_arch.png。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
from drawio_kit import Diagram  # noqa: E402

MIN_SIDE = int(os.environ.get('DIAGRAM_MIN_SIDE', 4000))

d = Diagram('技术栈全景', '每一层用了什么技术，本次选型新增了什么')
BW, X0, CW, GAP = 1060, 200, 280, 20
LAYERS = [
    ('接入', 120, [('CDN', '静态加速', 'white'), ('Nginx', '反向代理', 'white')]),
    ('服务', 230, [('Spring Boot', '应用框架', 'white'), ('Spring Cloud', '服务治理', 'white'), ('Dubbo', 'RPC', 'white')]),
    ('数据', 340, [('MySQL', '业务库', 'white'), ('Redis', '本次引入 · 缓存', 'key'), ('Elasticsearch', '搜索', 'white')]),
    ('运维 · 横切', 450, [('日志', 'ELK', 'sage'), ('监控告警', 'Prometheus', 'sage'), ('CI/CD', 'GitLab CI', 'sage')]),
]
for label, y, cards in LAYERS:
    d.band(40, y, BW, 90, label)
    for i, (title, sub, role) in enumerate(cards):
        d.box(X0 + i * (CW + GAP), y + 10, CW, 70, title, sub, role=role)

y = d.panel(40, 570, 560, '选型说明', ['Redis 本次引入，承接商品详情缓存', '横切能力所有层都接入'])
d.panel(640, 570, 460, '不在这张图里', ['版本号和实例规格', '第三方 SaaS'], kind='soft', h=y - 570)
d.legend(40, y + 24, [('white', '现有组件'), ('key', '本次引入'), ('sage', '横切能力')])
d.footer(40, y + 56, '读图：左列是层，右侧是该层的技术；主色卡片是本次新增，最下一行横切所有层。')

name = os.path.join(HERE, 'tech_arch')
d.save(name + '.drawio')
d.export(name + '.drawio', name + '.png', scale=d.scale_for(MIN_SIDE))
