import json, subprocess
import matplotlib.pyplot as plt

PALETTE = '$SKILL/scripts/palette.py'  # 换成 skill 的实际目录
SCHEME = 'macaron'  # 和文档里其他图同一套方案
c = json.loads(subprocess.check_output(['python', PALETTE, 'chart', SCHEME]))
plt.rcParams['font.sans-serif'] = ['PingFang SC', 'Microsoft YaHei', 'Noto Sans CJK SC', 'sans-serif']
fig, ax = plt.subplots(figsize=(6, 4), dpi=200)
fig.patch.set_facecolor(c['background']); ax.set_facecolor(c['background'])
groups = {'新用户': ([1, 2, 3, 4], [2.1, 2.9, 3.2, 4.8]), '老用户': ([1.5, 2.5, 3.5], [3.0, 3.6, 4.1])}
for i, (name, (xs, ys)) in enumerate(groups.items()):
    ax.scatter(xs, ys, s=36, color=c['categorical'][i], label=name, alpha=.85, edgecolors='none')
ax.legend(frameon=False, labelcolor=c['text'])
for side in ('top', 'right'):
    ax.spines[side].set_visible(False)
for side in ('left', 'bottom'):
    ax.spines[side].set_color(c['axis'])
ax.tick_params(colors=c['text']); ax.grid(color=c['grid'], linewidth=.6); ax.set_axisbelow(True)
fig.savefig('scatter.png', bbox_inches='tight')
