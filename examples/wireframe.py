#!/usr/bin/env python3
"""线框图：灰阶画布，图片占位加对角线，组件区块用真实文案，只有主按钮一个颜色；编号徽标点对应右侧说明列表。

用到：rect 画布与占位块、line 对角线、box 组件区块、badge 标注编号、panel 说明列表、footer。
运行后在本目录生成 wireframe.drawio 和 wireframe.png。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
from drawio_kit import Diagram  # noqa: E402

MIN_SIDE = int(os.environ.get('DIAGRAM_MIN_SIDE', 4000))

d = Diagram('商品详情页线框', '页面分哪几块，主操作是什么，各块放什么内容')
X, Y, W, H = 120, 120, 360, 560
gray, gray_stroke, _ = d.t.roles['ext']
d.rect(X, Y, W, H, d.t.bg, stroke=gray_stroke, extra='rounded=1;arcSize=16;absoluteArcSize=1;')
d.rect(X, Y, W, 40, gray, stroke='none', extra='rounded=1;arcSize=16;absoluteArcSize=1;')
d.text(X + 16, Y + 10, 200, 20, '‹  商品详情', size=13, bold=True)
# 图片占位：灰块加对角线
IX, IY, IW, IH = X + 20, Y + 60, W - 40, 200
d.rect(IX, IY, IW, IH, gray, stroke=gray_stroke)
d.line(IX, IY, IX + IW, IY + IH, color=gray_stroke, width=1)
d.line(IX + IW, IY, IX, IY + IH, color=gray_stroke, width=1)
d.text(IX, IY + IH / 2 - 10, IW, 20, '商品图片 · 轮播', size=12, color=d.t.muted, align='center')
# 组件区块
block = f'spacingLeft=10;strokeColor={gray_stroke};'  # 内容区块灰描边，整页只有主按钮上色
d.box(X + 20, Y + 280, W - 40, 64, '无线降噪耳机 Pro', '¥199 起 · 已售 2.3 万', role='white', align='left', extra=block)
d.box(X + 20, Y + 360, W - 40, 44, '选择规格：黑色 · 标准版', role='white', bold=False, align='left', extra=block)
d.box(X + 20, Y + 420, W - 40, 44, '用户评价 4.9 分 · 1.2 万条', role='white', bold=False, align='left', extra=block)
d.box(X + 20, Y + 490, W - 40, 48, '立即购买', role='key', shape='pill', size=14)
# 标注编号
for n, (bx, by) in enumerate([(IX + IW - 30, IY + 8), (X + W - 50, Y + 290), (X + W - 50, Y + 500)], start=1):
    d.badge(bx, by, n, size=24, role='bad')

y = d.panel(560, Y, 420, '标注说明', ['1  轮播图：最多 5 张，首图为主图', '2  标题与价格：价格取 SKU 最低价', '3  主按钮：常驻底部，未登录点击先登录'])
d.panel(560, y + 20, 420, '不在这张图里', ['规格选择弹层', '评价列表页'], kind='soft')
d.legend(X, Y + H + 30, [('ext', '占位 / 灰阶区块'), (('color', d.t.bg, gray_stroke), '内容区块'), ('key', '主操作'), ('bad', '标注编号')])
d.footer(X, Y + H + 62, '读图：灰阶是布局，只有主按钮上色；编号徽标对应右侧说明。')

name = os.path.join(HERE, 'wireframe')
d.save(name + '.drawio')
d.export(name + '.drawio', name + '.png', scale=d.scale_for(MIN_SIDE))
