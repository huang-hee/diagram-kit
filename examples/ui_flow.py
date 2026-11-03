#!/usr/bin/env python3
"""页面流程图：主路径自左向右一条线，页面是卡片、用户操作是平行四边形、判断是菱形，返回用虚线，交互说明用便签。

用到：box（pill / para / diamond）、dashed 回退 edge、sticky 交互说明、panel、legend、footer。
运行后在本目录生成 ui_flow.drawio 和 ui_flow.png。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
from drawio_kit import Diagram  # noqa: E402

MIN_SIDE = int(os.environ.get('DIAGRAM_MIN_SIDE', 4000))

d = Diagram('购买路径的页面流转', '从打开 App 到支付完成经过哪些页面，没登录时怎么回来')
Y = 160
entry = d.box(40, Y + 10, 140, 44, '打开 App', role='peach', shape='pill')
home = d.box(220, Y, 180, 64, '首页', '推荐位', role='lav')
tap = d.box(440, Y + 4, 160, 56, '点击商品', '用户操作', role='apricot', shape='para')
detail = d.box(640, Y, 180, 64, '商品详情', 'SKU · 价格', role='lav')
dec = d.box(860, Y - 12, 180, 88, '已登录?', role='apricot', shape='diamond')
confirm = d.box(1080, Y, 180, 64, '确认订单', '地址 · 优惠', role='key')
done = d.box(1300, Y + 10, 140, 44, '支付完成', role='peach', shape='pill')
login = d.box(860, 330, 180, 64, '登录页', '手机号 · 验证码', role='lav')
note = d.sticky(1080, 330, 220, 64, '登录后回到原商品，不回首页', role='note')

d.edge(entry, home, src='R', dst='L')
d.edge(home, tap, src='R', dst='L')
d.edge(tap, detail, src='R', dst='L')
d.edge(detail, dec, src='R', dst='L')
d.edge(dec, confirm, '是', src='R', dst='L', label_offset=-0.3)
d.edge(confirm, done, src='R', dst='L')
d.edge(dec, login, '否', src='B', dst='T', label_offset=-0.3)
d.edge(login, detail, '登录成功', src='L', dst='B', dashed=True, points=[(730, 362)], label_offset=-0.5)
d.edge(note, login, src='L', dst='R', dashed=True, arrow='none')

y = d.panel(40, 450, 560, '规则', ['未登录只拦在下单前，浏览不需要登录', '页面名和线上埋点的页面名一致'])
d.panel(640, 450, 560, '不在这张图里', ['支付失败的重试', '优惠券选择弹层'], kind='soft', h=y - 450)
d.legend(40, y + 24, [('peach', '入口 / 出口'), ('lav', '页面'), ('apricot', '操作 / 判断'), ('key', '关键页面'), ('note', '交互说明'), ('edge-dashed', '返回')])
d.footer(40, y + 56, '读图：从左到右是主路径，向下是分支；虚线是返回原页面。')

name = os.path.join(HERE, 'ui_flow')
d.save(name + '.drawio')
d.export(name + '.drawio', name + '.png', scale=d.scale_for(MIN_SIDE))
