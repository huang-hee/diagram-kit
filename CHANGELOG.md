# diagram-kit

## 1.2.0

### Minor Changes

- 7744b34: 示例按统一风格重做，并补上整图示例
  
  - references 里的 Mermaid 示例骨架改成统一风格写法：标题位、两级文字、分层架构用横向带；docs/画图指南.md 的 48 张示例图按此重新生成，每张图下加"回答的问题 / 读图"
  - 新增 examples/：用 drawio_kit 画的四十二张整图示例（脚本 + .drawio + PNG），流程图按规则改成竖排、分支向右
  - 补齐 27 种图型的 drawio 整图示例（组织结构、C4、部署架构、网络拓扑、类图、用例图、看板、故事地图、概念图、亲和图、活动图、通信图、交互概览、时间图、业务 / 数据 / 技术架构、对象图、Profile、组件图、包图、UML 部署图、组合结构、需求图、页面流程、线框图、甘特图）；drawio_kit 新增 `actor`、`port`、`rel`（UML 关系线）和 cube / component / package 三种节点形状
  - drawio_kit 的 mindmap 新增放射变体 `sides='radial'`（单层，中心圆 + 一圈圆），design-rules 补了放射版式的做法
  - 思维导图的示例图改由 drawio_kit 生成（docs/assets/mindmap.py）：Mermaid 的 mindmap 是放射布局、斜线，达不到统一风格；文档里的推荐工具改为 drawio
  - palette.py 的 flowchart 配置加 `wrappingWidth: 300`，两级文字不再折成三行；`mermaid` 子命令加 `--curve`，渲染端 Mermaid 低于 12 时用 basis
  - 选工具默认改为 drawio：要出图的结构图走 drawio_kit，Mermaid 代码块只在点名要源码展示时用，数据图走代码绘图（SKILL.md、tools.md、design-rules 同步）
  - build_docs.py 默认长边改为 2000（仓库示例图），`--min-side 4000` 出规则要求的尺寸
  - 新增 scripts/build_guide_html.py：把画图指南生成为带目录和搜索的单页 HTML（在线版）
  - drawio_kit 的 box 加 `icon=` 参数，新增 `icon()`：draw.io 自带线性图标、MCP 查到的样式串、emoji 三种写法
  - 新增 scripts/build_docs.py：从 references 示例生成指南的示例图并回填源码块
  - drawio_kit 加 `scale_for`，sankey_echarts.js 加 `--scale`，导出图片可按长边像素控制

## 1.1.0

### Minor Changes

- f1bfd73: 三种工具统一出图风格。
  
  - design-rules.md 重写为跨工具规则：
    - 标题区写一句话副标题；
    - 两级文字的圆角卡片，圆角固定 8px；
    - 横向分层带与贯穿条；
    - 连线 1.5px、正交带圆角，端口与布线有约束；
    - 说明面板、图例和读图行；
    - 每种图型的版式做法。
  - 新增 scripts/drawio_kit.py，按这套规则生成 draw.io 图，覆盖节点、分层、连线、脑图、树、鱼骨、ER 表、时序、数据图图元。
  - palette.py：
    - Mermaid 配置加 `flowchart.curve: step` 与统一间距，流程图类 classDef 加 8px 圆角，连线统一 1.5px；swimlane-beta 不加这组配置。
    - drawio 样式串改为绝对圆角 8、字体链、连线 1.5px，新增分层带、说明面板、标题竖条、副标题的样式。
  - tools.md 写明 Mermaid、drawio、diagram-design 怎么落地统一风格；diagram-design 要改 profile 里的字体、线宽和圆角。

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
