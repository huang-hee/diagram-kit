import json
import os
import sys

import matplotlib.pyplot as plt

sys.path.insert(0, '$SKILL/scripts')  # 换成 skill 的实际目录
import palette as P  # noqa: E402

SCHEME = 'macaron'  # 和文档里其他图同一套方案
c = json.loads(P.emitChart(SCHEME))
plt.rcParams['font.sans-serif'] = ['PingFang SC', 'Microsoft YaHei', 'Noto Sans CJK SC', 'sans-serif']
MIN_SIDE = int(os.environ.get('DIAGRAM_MIN_SIDE', 4000))
fig, ax = plt.subplots(figsize=(10, 6.25), dpi=MIN_SIDE // 10, layout='constrained')  # 宽 10 英寸，长边 = MIN_SIDE
fig.patch.set_facecolor(c['background'])
ax.set_facecolor(c['background'])
# 标题区：标题加粗、副标题写这张图回答的问题
fig.suptitle('月访问次数与客单价', x=0.02, ha='left', fontsize=16, fontweight='bold', color=c['text'])
ax.set_title('新老用户的客单价是否都随访问次数上升', loc='left', fontsize=11, color=c['axis'], pad=12)
groups = {'新用户': ([1, 2, 3, 4], [2.1, 2.9, 3.2, 4.8]), '老用户': ([1.5, 2.5, 3.5], [3.0, 3.6, 4.1])}
for i, (name, (xs, ys)) in enumerate(groups.items()):
    ax.scatter(xs, ys, s=70, color=c['categorical'][i], label=name, alpha=.85, edgecolors='none')
ax.set_xlabel('月访问次数', color=c['text'])
ax.set_ylabel('客单价（百元）', color=c['text'])
ax.legend(frameon=False, labelcolor=c['text'])
for side in ('top', 'right'):
    ax.spines[side].set_visible(False)
for side in ('left', 'bottom'):
    ax.spines[side].set_color(c['axis'])
ax.tick_params(colors=c['text'])
ax.grid(color=c['grid'], linewidth=.6)
ax.set_axisbelow(True)
fig.savefig('scatter.png')
