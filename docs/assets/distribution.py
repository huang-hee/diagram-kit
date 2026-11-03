import json
import random
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
fig.suptitle('接口耗时分布', x=0.02, ha='left', fontsize=16, fontweight='bold', color=c['text'])
ax.set_title('500 次调用的耗时集中在哪个区间，中位数在哪', loc='left', fontsize=11, color=c['axis'], pad=12)
random.seed(7)  # 示例数据，固定种子保证每次出图一致
data = [random.gauss(120, 30) for _ in range(500)]
ax.hist(data, bins=24, color=c['primary'], edgecolor=c['background'], linewidth=.5)
median = sorted(data)[len(data) // 2]
ax.axvline(median, color=c['text'], linestyle='--', linewidth=1)
ax.annotate(f'中位数 {median:.0f} ms', (median, ax.get_ylim()[1] * .95), xytext=(8, 0),
            textcoords='offset points', color=c['text'], fontsize=10, va='top')
ax.set_xlabel('耗时（ms）', color=c['text'])
ax.set_ylabel('次数', color=c['text'])
for side in ('top', 'right'):
    ax.spines[side].set_visible(False)
for side in ('left', 'bottom'):
    ax.spines[side].set_color(c['axis'])
ax.tick_params(colors=c['text'])
ax.grid(color=c['grid'], linewidth=.6)
ax.set_axisbelow(True)
fig.savefig('distribution.png')
