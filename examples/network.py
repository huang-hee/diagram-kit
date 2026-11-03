#!/usr/bin/env python3
"""网络拓扑图：分区用横向分层带（DMZ 警告底、内网浅底），设备卡片带 draw.io 自带的 Cisco 线性图标，安全设备在边界上。

用到：band（tint 换底色）、box（icon 传 mxgraph 样式串）、bad 安全设备、ext 外网、panel、legend、footer。
运行后在本目录生成 network.drawio 和 network.png。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
from drawio_kit import Diagram  # noqa: E402

MIN_SIDE = int(os.environ.get('DIAGRAM_MIN_SIDE', 4000))

d = Diagram('网络分区与链路', '外网、DMZ、内网怎么分区，流量经过哪些设备')


def cisco(name, color):
    """draw.io 自带的 Cisco 19 线性图标（离线可用），颜色改成卡片字色。"""
    return f'shape=mxgraph.cisco19.rect;prIcon={name};fillColor=none;strokeColor={color};'


W = 1000
d.band(40, 120, W, 110, '外网', '不可信', tint=d.t.fill('ext'))
d.band(40, 250, W, 110, 'DMZ 区', '对外服务', tint=d.t.fill('apricot'))
d.band(40, 380, W, 110, '内网区', '可信', tint=d.t.soft)

net = d.box(200, 140, 220, 70, '互联网', '公网用户', role='ext', icon=cisco('cloud', d.t.font('ext')))
fw = d.box(520, 140, 220, 70, '防火墙', '边界 ACL', role='bad', icon=cisco('firewall', d.t.font('bad')))
waf = d.box(200, 270, 220, 70, 'WAF', '应用层防护', role='bad', icon=cisco('firewall', d.t.font('bad')))
ng = d.box(520, 270, 220, 70, 'Nginx', '反向代理', role='peach', icon=cisco('server', d.t.font('peach')))
sw = d.box(200, 400, 220, 70, '核心交换机', '三层交换', role='lav', icon=cisco('l3_switch', d.t.font('lav')))
app = d.box(520, 400, 220, 70, '应用服务器', '业务应用', role='peach', icon=cisco('server', d.t.font('peach')))

d.edge(net, fw, src='R', dst='L')
d.edge(fw, waf, src='B', dst='T', points=[(630, 240), (310, 240)])
d.edge(waf, ng, src='R', dst='L')
d.edge(ng, sw, src='B', dst='T', points=[(630, 370), (310, 370)])
d.edge(sw, app, src='R', dst='L')

y = d.panel(40, 530, 560, '安全边界', ['防火墙在外网与 DMZ 之间，只放行 80 / 443', 'DMZ 到内网只允许 Nginx 访问应用端口'])
d.panel(640, 530, 400, '不在这张图里', ['办公网与 VPN', '带外管理网'], kind='soft', h=y - 530)
d.legend(40, y + 24, [('ext', '外网'), ('bad', '安全设备'), ('peach', '服务器'), ('lav', '网络设备'), ('edge', '流量方向')])
d.footer(40, y + 56, '读图：横带是分区，颜色表示可信程度；安全设备在各分区入口，流量从外网经 DMZ 进内网。')

name = os.path.join(HERE, 'network')
d.save(name + '.drawio')
d.export(name + '.drawio', name + '.png', scale=d.scale_for(MIN_SIDE))
