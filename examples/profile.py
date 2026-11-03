#!/usr/bin/env python3
"""Profile 图（UML）：元类、构造型、标记值三种卡片，扩展关系用实线实心三角指向元类。

用到：table（sub 写 «metaclass» / «stereotype»）、rel（inherit / link）、panel、legend、footer。
运行后在本目录生成 profile.drawio 和 profile.png。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
from drawio_kit import Diagram  # noqa: E402

MIN_SIDE = int(os.environ.get('DIAGRAM_MIN_SIDE', 4000))

d = Diagram('Entity 构造型', '用 Profile 给类加上数据库映射：扩展哪个元类、带哪些标记值')
meta = d.table(360, 120, 240, 'Class', [('UML 元模型里的类', 'muted')], role='sage', sub='«metaclass»')
stereo = d.table(360, 280, 240, 'Entity', ['table : String', 'schema : String'], role='apricot', sub='«stereotype»')
tagged = d.table(720, 280, 260, 'Order', ['table = "t_order"', 'schema = "shop"'], role='mint', sub='«Entity» 应用后的标记值')

d.rel(stereo, meta, 'extension', 'extension', src='T', dst='B')
d.rel(stereo, tagged, 'link', '应用到', src='R', dst='L')

y = d.panel(40, 460, 560, '说明', ['构造型 Entity 扩展元类 Class，给类增加 table、schema 两个属性', '标记值是构造型应用到具体类之后填的值'])
d.panel(640, 460, 340, '不在这张图里', ['Profile 的包和导入关系'], kind='soft', h=y - 460)
d.legend(40, y + 24, [('sage', '元类'), ('apricot', '构造型'), ('mint', '标记值'), ('line', '应用')])
d.footer(40, y + 56, '读图：实心三角从构造型指向元类，表示扩展；右侧卡片是构造型用在 Order 类上时填的值。')

name = os.path.join(HERE, 'profile')
d.save(name + '.drawio')
d.export(name + '.drawio', name + '.png', scale=d.scale_for(MIN_SIDE))
