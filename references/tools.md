# 工具

选哪个工具见 SKILL.md 第 2 步；工具或依赖缺失时不执行，提示调用者安装（清单见 README.md）。这里讲每个工具怎么接配色、怎么布局、怎么导出。

## Mermaid

### 配色机制

- 全局：frontmatter 里 `theme: base` + `themeVariables`（背景、字体、连线、便签、各图型的专用变量）。
- 按角色：`classDef 角色 fill:…,stroke:…,color:…`，节点挂 class。未挂 class 的节点是中性的白底，颜色全由 classDef 决定。
- `palette.py mermaid` 已经按图型处理了各自的专用变量：思维导图 / 时间线 / 看板的 `cScale*`、甘特图的 `task*` / `crit*` / `done*`、饼图 `pie1..`、旅程图 `fillType*`、Git 图 `git0..`、象限图 `quadrant*`、柱线图 `xyChart.plotColorPalette`、韦恩图 `venn*`、矩形树图 `cScale*` / `cScalePeer*`、桑基图 `config.sankey.nodeColors`、用例图 `usecase*`、C4 的 `UpdateElementStyle` / `UpdateRelStyle`。

### 各图挂 class 的写法

| 图型                                                                                     | 写法                                                                                                     |
| ---------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| flowchart / swimlane-beta / block-beta                                                   | `A[文字]:::角色`，或 `class A,B 角色`                                                                    |
| stateDiagram-v2                                                                          | `class 状态Id 角色`（写在状态定义之后）                                                                  |
| classDiagram                                                                             | `class 类名:::角色`，或 `cssClass "A,B" 角色`                                                            |
| erDiagram                                                                                | 关系行里 `实体:::角色`                                                                                   |
| usecase-beta                                                                             | `Order("下单"):::角色`、`actor A:::角色`、`systemBoundary` 同理；class 名不能用 `actor` 这类关键字 |
| requirementDiagram                                                                       | `class 元素名 角色`                                                                                      |
| treemap-beta                                                                             | 叶子后加 `:::角色`                                                                                       |
| C4                                                                                       | `UpdateElementStyle(别名, ...)`，用 `--body` 时自动生成；边界没有样式宏，保持默认虚线框                  |
| mindmap / timeline / kanban / gitGraph / pie / journey / radar / venn / xychart / sankey | 按出现顺序自动取色，不用写 class                                                                         |

### 布局技巧

- 方向：`flowchart TB` / `LR`；subgraph 里可以单独写 `direction LR`。
- 拉长连线 `--->`、`---->`；用不可见连线 `A ~~~ B` 调整相对位置。
- 节点内换行：`A["第一行<br>第二行"]`。
- 单独设某条线：`linkStyle 3 stroke:#E35144,stroke-width:2px`（序号从 0 开始，按连线出现顺序）。
- 自动布局超过 12 个节点后可读性急剧下降：拆成"总览 + 子图"，或改用 drawio。

### 渲染与导出

- 有 Mermaid 渲染 MCP 时用它校验并预览。
- 本地命令行需要 `mmdc`（`@mermaid-js/mermaid-cli`）：`mmdc -i 图.mmd -o 图.png -s 2 -b '#FFFFFF'`（`-s 2` 出 @2x，`-b` 背景色用方案的页面背景，`-q` 静默）。没有 mmdc 就提示安装，不临时拉取。
- 配置里的字体链是 `PingFang SC, Microsoft YaHei, Noto Sans CJK SC, Source Han Sans SC, sans-serif`：macOS 落 PingFang，Windows 落微软雅黑，Linux 要装 Noto Sans CJK；一个都没有时中文会出方块。
- frontmatter 不被支持时，用 `palette.py mermaid … --init` 输出 `%%{init: {...}}%%` 指令写法。

## drawio

- 何时用：超过 12 个节点、需要真实产品图标、要交付编辑、正式架构图、UI 线框图 / 低保真原型、Mermaid 画不了的图（时间图、组合结构图、标准 UML / BPMN 符号、多泳道 × 多阶段）。
- 建图和改图按 draw.io 插件或 MCP 自己的工具说明来；MCP 能查官方图标（AWS / 阿里云 / K8s / Cisco 等）。
- 配色：`palette.py drawio <type> [方案]` 输出每个角色、连线、容器、泳道、边界、标题、说明文字的 style 字符串，第一行是页面背景色。产品图标保持官方原色，不要用方案色覆盖。
- 尺寸、间距见 design-rules.md。
- 导出：插件 / MCP 自带导出就用它；否则用 draw.io 桌面版命令行：

  ```bash
  drawio -x -f png -s 2 -b 10 -o 图.png 图.drawio
  # 可执行文件：macOS /Applications/draw.io.app/Contents/MacOS/draw.io
  #            Windows "%ProgramFiles%\draw.io\draw.io.exe"
  #            Linux   drawio
  # 加 -e 会把图的 XML 嵌进 PNG，这张 PNG 也能直接用 draw.io 打开编辑
  ```

- `.drawio` 源文件和导出的 PNG 一起交付，存放位置按调用者或项目的规则。

## diagram-design

- 何时用：发布级排版、要 HTML / SVG 输出、不超过 12 个节点。
- 结构和版式按 diagram-design 自己的规则；颜色用 `palette.py css [方案]` 输出的 CSS 变量替换它的默认色（`--bg`、`--text`、`--line`、`--primary`、`--accent`、`--slot0-fill` … `--series-1` …、`--state-ok` …）。
- `.html` 源文件和导出的 PNG 一起交付。

## 代码绘图（matplotlib / ECharts）

- 何时用：Mermaid 没有的数据图（散点、直方、箱线、热力、旭日、漏斗），节点要显示中文的桑基图，或需要精确坐标轴、多系列堆叠、双轴、交互。
- 依赖：matplotlib，或 echarts（见下）；缺了不执行，提示安装。
- 取色：`palette.py chart [方案]` 输出 JSON：

  | 字段                    | 用途                                                           |
  | ----------------------- | -------------------------------------------------------------- |
  | `background` / `text`   | 画布背景、文字                                                 |
  | `axis` / `grid`         | 坐标轴、网格线                                                 |
  | `primary` / `highlight` | 单系列主色、要突出的那一项                                     |
  | `categorical`           | 分类系列色（按顺序用）                                         |
  | `sequential`            | 由浅到深的渐层（热力、数值映射）                               |
  | `deemphasis`            | 不突出的项（灰）                                               |
  | `state`                 | ok / warn / bad / info / done                                  |
  | `nodes`                 | 分类色加深到和背景拉开的版本，给桑基图节点条、细线这类窄色块用 |

- matplotlib：`dpi=200` 出图约等于 @2x；示例见 types-data.md 的散点图、直方图。中文要有 CJK 字体，装完字体后清掉 matplotlib 的字体缓存。
- ECharts：`color: c.categorical`、`backgroundColor: c.background`、`textStyle: { color: c.text }`、坐标轴 `axisLine.lineStyle.color: c.axis`、`splitLine.lineStyle.color: c.grid`。

### ECharts 服务端出图（Node）

现成脚本：桑基图用 `scripts/sankey_echarts.js`（用法见 types-data.md 的桑基图一节）。其他图照它的写法改 `series` 即可。要点：

- 依赖 echarts，装在 skill 的 `scripts/` 目录；脚本先在 `scripts/` 找，找不到再到当前目录找，都没有就退出并提示安装。
- 渲染：`echarts.init(null, null, { renderer: 'svg', ssr: true, width, height })`，然后 `chart.renderToSVGString()` 得到 SVG。
- 必须设 `animation: false`，否则导出的是动画中间帧，图只画了一半。
- 写完文件后调用 `chart.dispose()` 和 `process.exit(0)`，否则 Node 进程不会退出。
- 要 PNG@2x：用 Playwright 打开 SVG，设 `deviceScaleFactor: 2` 截图，依赖 playwright 和 Chromium；或者交给 Playwright MCP 截图。缺了提示安装。
- 数据文件（CSV / JSON）和 SVG / PNG 一起交付，作为可编辑源文件。

## Figma

- 何时用：高保真交互稿、可演示的原型、需求阶段的 UI 设计，需要协作和演示时。
- 不用来导出图片，除非调用者点名；UI 线框图 / 低保真原型用 drawio。
- 颜色：把 `palette.py css [方案]` 的变量建成 Figma 颜色变量；项目已有设计系统时以设计系统为准。

## 文生图工具（如有）

- 何时用：非结构的配图，比如文章封面、插画、氛围图、概念示意图片。
- 不要用它画带大量文字的结构图（文字会乱），结构图用上面的工具。
- 提示词里写清：主体、构图、风格（扁平插画 / 等距 / 线稿）、比例，以及配色——从 `palette.py show [方案]` 里取主色、3–5 个系列色和背景色的 hex，和文档里其他图保持同一套方案。
