#!/usr/bin/env python3
"""部署架构图：边界嵌套（可用区 VPC → K8s 集群），流量自上而下，安全设备用失败色。

用到：group（dashed 的 VPC 边界、浅底的集群）、box（cyl）、bad 安全设备、ext 公网、panel、legend、footer。
运行后在本目录生成 deploy_arch.drawio 和 deploy_arch.png。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
from drawio_kit import Diagram  # noqa: E402

MIN_SIDE = int(os.environ.get('DIAGRAM_MIN_SIDE', 4000))

d = Diagram('华东生产环境部署', '服务跑在哪个可用区和集群里，流量从哪进来，各有几个副本')
X = 300  # 主列左边
net = d.box(X, 120, 220, 44, '互联网', '用户流量', role='ext', shape='pill')
waf = d.box(X, 200, 220, 56, 'WAF', '边界防护', role='bad')
d.group(200, 290, 420, 520, '华东可用区 VPC', dashed=True)
lb = d.box(X, 330, 220, 56, '负载均衡 SLB', '公网入口', role='lav')
d.group(230, 420, 360, 230, 'K8s 集群', fill=d.t.soft)
gw = d.box(X, 460, 220, 56, '网关', '2 副本', role='peach')
od = d.box(X, 560, 220, 56, '订单服务', '3 副本', role='key')
db = d.box(X, 690, 220, 70, 'MySQL', '一主一从', role='mint', shape='cyl')

d.edge(net, waf, src='B', dst='T')
d.edge(waf, lb, src='B', dst='T')
d.edge(lb, gw, src='B', dst='T')
d.edge(gw, od, src='B', dst='T')
d.edge(od, db, src='B', dst='T')

y = d.panel(700, 290, 420, '实例与容量', ['网关 2 副本、订单服务 3 副本，按 HPA 弹性扩到 6', 'MySQL 一主一从，从库只读'])
y = d.panel(700, y + 20, 420, '不在这张图里', ['灾备可用区', '日志与监控采集'], kind='soft')
d.legend(200, 840, [('ext', '公网'), ('bad', '安全设备'), ('lav', '接入'), ('peach', '网关'), ('key', '业务服务'), ('mint', '存储'), ('edge', '流量方向')])
d.footer(200, 872, '读图：虚线框是 VPC，浅底框是 K8s 集群；流量自上而下，副本数写在卡片说明里。')

name = os.path.join(HERE, 'deploy_arch')
d.save(name + '.drawio')
d.export(name + '.drawio', name + '.png', scale=d.scale_for(MIN_SIDE))
