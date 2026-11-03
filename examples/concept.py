#!/usr/bin/env python3
"""概念图：核心概念用主色圆形放在左侧，一级概念围绕它，每条线都写关系动词，例子用虚线。

用到：box（circle）、带关系词的 edge、dashed 例子线、panel、legend、footer。
运行后在本目录生成 concept.drawio 和 concept.png。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
from drawio_kit import Diagram  # noqa: E402

MIN_SIDE = int(os.environ.get('DIAGRAM_MIN_SIDE', 4000))

d = Diagram('Spring IoC 核心概念', '容器、Bean、注解、AOP 之间是什么关系')
ioc = d.box(80, 237, 130, 130, 'IoC 容器', '核心', role='key', shape='circle', size=15)  # 圆心和 Bean 的中线对齐在 302
ann = d.box(420, 130, 200, 56, '注解', '@Component 等', role='lav')
bean = d.box(420, 270, 200, 64, 'Bean', '容器托管的对象', role='lav')
aop = d.box(420, 410, 200, 56, 'AOP', '切面', role='lav')
dep = d.box(760, 270, 200, 64, '其他 Bean', '被注入的依赖', role='white')
ex = d.box(760, 130, 200, 56, '@Service', '例子', role='mint')

d.edge(ioc, bean, '创建并管理', src='R', dst='L')
d.edge(ann, bean, '声明', src='B', dst='T')
d.edge(aop, bean, '代理增强', src='T', dst='B')
d.edge(bean, dep, '依赖注入', src='R', dst='L')
d.edge(ann, ex, '例如', src='R', dst='L', dashed=True, arrow='open')

y = d.panel(40, 520, 560, '读法', ['先看主色圆：IoC 容器是一切的起点', '沿着线上的动词读：容器创建 Bean，注解声明 Bean，AOP 增强 Bean'])
d.panel(640, 520, 420, '不在这张图里', ['Bean 的生命周期回调', 'XML 配置方式'], kind='soft', h=y - 520)
d.legend(40, y + 24, [('key', '核心概念'), ('lav', '一级概念'), ('white', '次级概念'), ('mint', '例子'), ('edge', '关系，动词在线上'), ('edge-dashed-open', '例如')])
d.footer(40, y + 56, '读图：没有固定方向，每条线连同动词读成一句话；虚线指向例子。')

name = os.path.join(HERE, 'concept')
d.save(name + '.drawio')
d.export(name + '.drawio', name + '.png', scale=d.scale_for(MIN_SIDE))
