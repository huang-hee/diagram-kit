#!/usr/bin/env python3
"""数据架构图：从左到右按数据流向分成采集、计算、存储、消费四列，存储用圆柱，四个环节四种颜色。

用到：group 当列、box（cyl）、edge、panel、legend、footer。
运行后在本目录生成 data_arch.drawio 和 data_arch.png。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
from drawio_kit import Diagram  # noqa: E402

MIN_SIDE = int(os.environ.get('DIAGRAM_MIN_SIDE', 4000))

d = Diagram('实时数据链路', '数据从哪里来、在哪算、分几层存、给谁用')
COLS = [('数据源', 40), ('实时计算', 340), ('分层存储', 640), ('消费', 940)]
for label, x in COLS:
    d.group(x, 120, 260, 320, label)
src1 = d.box(70, 170, 200, 64, '业务库 binlog', 'Canal 采集', role='lav')
src2 = d.box(70, 330, 200, 64, '埋点日志', '客户端上报', role='lav')
flink = d.box(370, 250, 200, 64, 'Flink 实时计算', '清洗 · 聚合', role='peach')
ods = d.box(670, 170, 200, 70, '数仓', 'ODS / DWD', role='mint', shape='cyl')
ads = d.box(670, 330, 200, 70, 'ADS 指标', '面向应用', role='mint', shape='cyl')
bi = d.box(970, 333, 200, 64, 'BI 报表', '运营看板', role='apricot')  # y 和 ADS 圆柱的中线对齐

d.edge(src1, flink, src='R', dst='LT')
d.edge(src2, flink, src='R', dst='LB')
d.edge(flink, ods, src='R', dst='L')
d.edge(ods, ads, '汇总', src='B', dst='T')
d.edge(ads, bi, src='R', dst='L')

y = d.panel(40, 480, 560, '口径', ['实时链路延迟目标 5 秒内', '离线链路另有一张图'])
d.panel(640, 480, 560, '不在这张图里', ['数据质量校验', '权限与脱敏'], kind='soft', h=y - 480)
d.legend(40, y + 24, [('lav', '数据源'), ('peach', '计算'), ('mint', '存储'), ('apricot', '消费'), ('edge', '数据流向')])
d.footer(40, y + 56, '读图：从左到右是数据流向，一列一个环节；圆柱是存储，颜色对应环节。')

name = os.path.join(HERE, 'data_arch')
d.save(name + '.drawio')
d.export(name + '.drawio', name + '.png', scale=d.scale_for(MIN_SIDE))
