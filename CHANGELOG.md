# diagram-kit

## 1.0.6

### Patch Changes

- 52d8459: 预检规则改为"该步的备选也没有才停"；drawio 图库里没有对应产品图标时用相似图标并说明，找不到则忽略图标继续画并提示提供图标文件；README 补按系统分的一键安装与验证命令

## 1.0.5

### Patch Changes

- 790604b: 代码绘图的 matplotlib 和 ECharts 明确为等价选项：装了哪个用哪个，两个都没有才提示安装

## 1.0.4

### Patch Changes

- ae52d1f: 预检规则里写明唯一例外（桑基图中文节点缺 echarts 时退回对照表、不问），和出图步骤的固定做法对应

## 1.0.3

### Patch Changes

- 3446d7c: 字体链改写在 Mermaid config 顶层的 `fontFamily`（`--init` 同样），原来放在 themeVariables 里不生效，中文会落到渲染器默认字体
- 3446d7c: 按代码审查修复：看板列色错位、路线图三段深浅、韦恩图改用 style 语句（主题变量不存在）、矩形树图角色改成系列色语义；系列浅调和饼图"其他"块与页面拉开；正文自带的 title 保留、多余 frontmatter 键提示；UTF-8 BOM / 非 UTF-8 正文报错；`roles` 不带图型时提示；灰色槽不再派生出红褐字；`check` 提示被自动加深的连线 / 描边；`render_check` 对未知图型报错并打印失败原因；桑基脚本 Windows 下能找到全局 echarts、跳过 CSV 表头和短行、参数缺值报错；桑基图中文节点的固定规则：优先 ECharts，缺 echarts 用对照表；角色表标出仅 drawio 生效的角色；README 补 mmdc 的 Chrome 安装和 Cursor / Copilot 个人目录
- dee3445: 按行为验证结果调整：中文桑基的固定做法挪到出图步骤并写进 palette.py 的报错提示（先 ECharts、缺 echarts 再对照表）；description 补常见叫法（决策树、BPMN、散点、直方等）；单图 12 节点上限只约束有连线的图，脑图 / 树形 / 时间线 / 甘特 / 看板 / 饼图不受限；-beta 图型默认直接用原生写法并注明，不再要求先确认平台

## 1.0.2

### Patch Changes

- 5c877fc: echarts / playwright 改为全局安装，`sankey_echarts.js` 会到全局 node_modules 找包，skill 目录不再放运行时依赖

## 1.0.1

### Patch Changes

- 91c417f: diagram-design 的配色改为按它的语义角色（paper / ink / accent / series …）映射：`palette.py css` 多输出一组 `--dd-*` 变量，tools.md 写明映射表和 profile 做法

## 1.0.0

### Major Changes

- 首版：48 种图型按角色上色，12 套对所有图型通用的配色方案，输出 Mermaid / draw.io / CSS / 图表代码的配色；缺依赖时不执行、提示安装
