import json, subprocess
import matplotlib.pyplot as plt

PALETTE = '$SKILL/scripts/palette.py'  # 换成 skill 的实际目录
SCHEME = 'macaron'  # 和文档里其他图同一套方案
c = json.loads(subprocess.check_output(['python', PALETTE, 'chart', SCHEME]))
plt.rcParams['font.sans-serif'] = ['PingFang SC', 'Microsoft YaHei', 'Noto Sans CJK SC', 'sans-serif']
fig, ax = plt.subplots(figsize=(6, 4), dpi=200)
fig.patch.set_facecolor(c['background']); ax.set_facecolor(c['background'])
import random
data = [random.gauss(120, 30) for _ in range(500)]
ax.hist(data, bins=24, color=c['primary'], edgecolor=c['background'], linewidth=.5)
ax.axvline(sorted(data)[len(data) // 2], color=c['text'], linestyle='--', linewidth=1)
for side in ('top', 'right'):
    ax.spines[side].set_visible(False)
for side in ('left', 'bottom'):
    ax.spines[side].set_color(c['axis'])
ax.tick_params(colors=c['text']); ax.grid(color=c['grid'], linewidth=.6); ax.set_axisbelow(True)
fig.savefig('distribution.png', bbox_inches='tight')
