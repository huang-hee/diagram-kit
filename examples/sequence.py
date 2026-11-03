#!/usr/bin/env python3
"""时序图：参与者头卡片等距一行，消息竖向等距，alt 片段用虚线框，说明用 note 卡片。

用到：seq 的 msg（sync / ret / async）、self_msg、note、frag / els / end、groups、finish。
运行后在本目录生成 sequence.drawio 和 sequence.png。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
from drawio_kit import Diagram  # noqa: E402

MIN_SIDE = int(os.environ.get('DIAGRAM_MIN_SIDE', 4000))

d = Diagram('下单与支付回调', '前端、订单服务和支付平台之间的调用顺序')
sq = d.seq([('u', '用户', None, 'actor'), ('fe', '前端', 'React', 'peach'),
            ('o', '订单服务', 'Spring Boot', 'lav'), ('p', '支付平台', '外部', 'ext')],
           x0=60, y0=130, gap=240, groups=[('电商系统', ['fe', 'o'])])
sq.msg('u', 'fe', '点击提交')
sq.msg('fe', 'o', 'POST /orders')
sq.msg('o', 'fe', '订单号', kind='ret')
sq.note('fe', 'o', '同步下单，失败直接提示用户')
sq.msg('fe', 'p', '拉起收银台')
sq.msg('p', 'o', '异步回调', kind='async')
sq.frag('alt', '验签通过', 'o', 'p')
sq.self_msg('o', '置为已支付')
sq.els('验签失败')
sq.self_msg('o', '记录异常，等人工处理')
sq.end()
bottom = sq.finish()

d.legend(60, bottom + 30, [('edge', '同步调用'), ('edge-dashed', '返回'), ('note', '说明'), ('ext', '外部系统')])
d.footer(60, bottom + 62, '读图：自上而下是时间顺序；实线是调用，虚线是返回；alt 框里两段只走一段。')

name = os.path.join(HERE, 'sequence')
d.save(name + '.drawio')
d.export(name + '.drawio', name + '.png', scale=d.scale_for(MIN_SIDE))
