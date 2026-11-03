#!/usr/bin/env python3
"""流程图：主路径竖排一列，判断的另一出口统一向右落到结果列，依据面板放右侧。

用到：box（pill / diamond / cyl）、带标签和拐点的 edge、`key=True` 粗线、panel（note 和 soft 两种）、legend、footer。
运行后在本目录生成 flowchart.drawio 和 flowchart.png。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
from drawio_kit import Diagram  # noqa: E402

MIN_SIDE = int(os.environ.get('DIAGRAM_MIN_SIDE', 4000))  # 导出 PNG 的长边像素下限

d = Diagram('订单提交流程', '提交订单后在哪里分叉，哪一步是关键路径')
X, RX = 120, 400  # 主路径列、右侧结果列的左边
start = d.box(X + 20, 120, 160, 44, '提交订单', role='peach', shape='pill')
check = d.box(X, 200, 200, 88, '库存充足?', role='apricot', shape='diamond')
lock = d.box(X, 330, 200, 64, '锁定库存', 'Redis 预扣 15 分钟', role='lav')
pay = d.box(X, 440, 200, 64, '发起支付', '拉起收银台', role='key')
end = d.box(X + 20, 550, 160, 44, '结束', role='peach', shape='pill')
oos = d.box(RX, 212, 200, 64, '提示缺货', '库存不足时', role='bad')  # 与判断同一中线
db = d.box(RX, 326, 200, 72, '订单库', 'MySQL · orders', role='mint', shape='cyl')  # 与锁定库存同一中线

d.edge(start, check, src='B', dst='T')
d.edge(check, lock, '是', src='B', dst='T')
d.edge(check, oos, '否', src='R', dst='L')
d.edge(lock, db, '写入', src='R', dst='L')
d.edge(lock, pay, src='B', dst='T', key=True)
d.edge(pay, end, src='B', dst='T', key=True)
d.edge(oos, end, src='R', dst='R', points=[(680, 244), (680, 572)])  # 从外侧通道绕回终点

y = d.panel(740, 120, 400, '依据', ['R3 库存预扣 15 分钟后自动释放', 'R7 支付超时 30 分钟关闭订单'])
d.panel(740, y + 20, 400, '不在这张图里', ['优惠券核销', '发货与物流'], kind='soft')
d.legend(X, 630, [('peach', '起止'), ('apricot', '判断'), ('lav', '处理'), ('key', '关键路径'),
                  ('bad', '异常分支'), ('mint', '数据'), ('edge-key', '关键路径连线')])
d.footer(X, 662, '读图：自上而下是主路径，判断的"否"向右落到结果列；主色卡片和粗线是关键路径。')

name = os.path.join(HERE, 'flowchart')
d.save(name + '.drawio')
d.export(name + '.drawio', name + '.png', scale=d.scale_for(MIN_SIDE))
