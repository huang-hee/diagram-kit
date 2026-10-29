# 工具

选哪个工具见 SKILL.md 第 2 步；工具或依赖缺失时不执行，提示调用者安装。这里讲每个工具怎么接配色、怎么布局、怎么导出，以及怎么落地 design-rules.md 的统一风格。三种工具出的图要像一套：同样的标题写法、圆角卡片、等粗正交连线、说明与图例的位置。

## Mermaid

### 统一风格

`palette.py mermaid` 的输出已经带上这几项，不要删：

- 配置：`flowchart.curve: step`（正交折线、转角自带小圆角），`nodeSpacing: 50`，`rankSpacing: 60`，`padding: 12`。
  - Mermaid 12.2 上实测，这一组对流程、状态、类、ER 图都生效；更早版本的渲染端未验证。
  - swimlane-beta 不加这一组：它默认就是正交线，加了 `step` 后箭头会和节点错开。
- 流程图类的 classDef 带 `rx:8,ry:8`，矩形节点圆角 8。
- 正文以 `flowchart` / `graph` 开头时，末尾追加 `linkStyle default stroke-width:1.5px`，全图连线统一 1.5px。swimlane-beta 里 `linkStyle` 不生效。
- 关键路径要单独加粗时，在后面写 `linkStyle 序号 stroke-width:2.5px`。

正文自己要做的：

- 用 frontmatter 的 `title` 写标题，不带图号。副标题（这张图回答的问题）、说明和图例写在 md 里图的下面。
- 节点用两级文字 `A["主名<br><small>说明</small>"]`，主名不超过 12 个汉字。
- 用节点顺序和 `~~~` 不可见连线减少交叉；线上标签 6–8 个字以内。

### 配色机制

- 全局：frontmatter 里 `theme: base` + `themeVariables`（背景、字体、连线、便签、各图型的专用变量）。
- 按角色：`classDef 角色 fill:…,stroke:…,color:…`，节点挂 class。未挂 class 的节点是中性的白底，颜色全由 classDef 决定。
- `palette.py mermaid` 已经按图型处理了各自的专用变量：思维导图 / 时间线 / 看板的 `cScale*`、甘特图的 `task*` / `crit*` / `done*`、饼图 `pie1..`、旅程图 `fillType*`、Git 图 `git0..`、象限图 `quadrant*`、柱线图 `xyChart.plotColorPalette`、韦恩图的 `style` 语句（没有主题变量，`--body` 时按 `set` 顺序生成）、矩形树图 `cScale*` / `cScalePeer*`、桑基图 `config.sankey.nodeColors`、用例图 `usecase*`、C4 的 `UpdateElementStyle` / `UpdateRelStyle`。

### 各图挂 class 的写法

| 图型                                                                                     | 写法                                                                                               |
| ---------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| flowchart / swimlane-beta / block-beta                                                   | `A[文字]:::角色`，或 `class A,B 角色`                                                              |
| stateDiagram-v2                                                                          | `class 状态Id 角色`（写在状态定义之后）                                                            |
| classDiagram                                                                             | `class 类名:::角色`，或 `cssClass "A,B" 角色`                                                      |
| erDiagram                                                                                | 关系行里 `实体:::角色`                                                                             |
| usecase-beta                                                                             | `Order("下单"):::角色`、`actor A:::角色`、`systemBoundary` 同理；class 名不能用 `actor` 这类关键字 |
| requirementDiagram                                                                       | `class 元素名 角色`                                                                                |
| treemap-beta                                                                             | 叶子后加 `:::角色`                                                                                 |
| C4                                                                                       | `UpdateElementStyle(别名, ...)`，用 `--body` 时自动生成；边界没有样式宏，保持默认虚线框            |
| venn-beta                                                                                | `style 集合名 fill:…,stroke:…`，用 `--body` 时自动生成                                              |
| mindmap / timeline / kanban / gitGraph / pie / journey / radar / xychart / sankey        | 按出现顺序自动取色，不用写 class                                                                   |

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
- 图库里没有对应的产品图标：找一个相似度最高的图标用上，在回复里说明换了哪个；相似的也找不到就忽略图标继续往下画，在回复里说明没有找到图标，请调用者提供图标文件。
- 尺寸、间距见 design-rules.md。
- 导出：插件 / MCP 自带导出就用它；否则用 draw.io 桌面版命令行：

  ```bash
  drawio -x -f png -s 2 -b 24 -e -o 图.png 图.drawio
  # 可执行文件：macOS /Applications/draw.io.app/Contents/MacOS/draw.io
  #            Windows "%ProgramFiles%\draw.io\draw.io.exe"
  #            Linux   drawio
  # -e 把图的 XML 嵌进 PNG，这张 PNG 也能直接用 draw.io 打开编辑
  ```

- `.drawio` 源文件和导出的 PNG 一起交付，存放位置按调用者或项目的规则。

### 精修出图：scripts/drawio_kit.py

用 Python 写坐标、由 drawio_kit 生成 `.drawio`，统一风格的令牌（颜色、圆角、线宽、字号、端口、标题区、说明区）都在组件里，不手写样式串。适合正式文档里的整套图；只改一两处颜色时用上面的 `palette.py drawio` 样式串就够。

```python
import sys; sys.path.insert(0, '$SKILL/scripts')
from drawio_kit import Diagram
d = Diagram('应用架构', '五个包各自负责什么、运行时谁调用谁', scheme='macaron')
d.band(40, 120, 1000, 120, '服务进程', '按需启动')
a = d.box(220, 146, 220, 68, 'server', 'HTTP · WebSocket', role='lav')
b = d.box(520, 146, 220, 68, 'core', '入库 · 派生 · 查询', role='key')
d.edge(a, b, '调度', src='R', dst='L')
y = d.panel(40, 270, 640, '依据', ['A16 包结构', 'A21 服务与页面的边界'])
d.legend(40, y + 24, [('lav', '服务进程里的包'), ('key', '焦点'), ('edge', '运行时调用')])
d.footer(40, y + 56, '读图：横带是运行位置，实线是运行时调用。')
d.save('app-arch.drawio'); d.export('app-arch.drawio', 'app-arch.png')
```

| 组件                                                           | 用途                                                                                                                                                  |
| -------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Diagram(标题, 副标题, scheme)`                                | 自动画标题区；副标题写这张图回答的问题                                                                                                                |
| `box`                                                          | 节点：两级文字。`shape` 可选 rect、pill、diamond、cyl、para、circle、doc、hex、note。`role` 取角色色，待定用 `role='pending'`。深色底时传 `sub_color` |
| `band` / `vband` / `group` / `frame`                           | 分层带、右侧贯穿条、分组容器（`dashed=True` 为边界），以及交互概览的 ref / sd 框                                                                      |
| `edge`                                                         | 正交连线。`src` / `dst` 指定端口（R、L、T、B 及 1/4 点）；`points` 是显式拐点；`dashed` 画虚线，`key` 画加粗；`label_offset` 把标签挪离拐角           |
| `line`                                                         | 按坐标画线：坐标轴、生命线、鱼骨，`arrow='block'` 时带箭头                                                                                            |
| `panel` / `legend` / `footer`                                  | 说明面板（高度自动算）、图例一行、读图行                                                                                                              |
| `mindmap`                                                      | 脑图，也当横向树用（`sides='right'`）；`top=120` 贴在标题区下方；节点写成 `(标签, [], {'pending': True})` 为待定                                      |
| `tree_down`                                                    | 自上而下的树 / 组织结构                                                                                                                               |
| `fishbone`                                                     | 鱼骨图                                                                                                                                                |
| `table`                                                        | ER 实体或类卡片：`'pk'` 主键、`'fk'` 外键、`'sep'` 分隔线                                                                                             |
| `dot` / `bar`                                                  | 状态图的起止点；活动图的分叉 / 汇合粗横条                                                                                                             |
| `seq(...)`                                                     | 时序图，返回的对象依次调 `msg` / `note` / `frag` / `els` / `end`，最后调 `finish`                                                                     |
| `chevron` / `badge` / `sticky`                                 | 阶段箭头条、编号徽标、便签                                                                                                                            |
| `path` / `polygon` / `ribbon` / `sector` / `rect` / `squarify` | 数据图的图元：任意路径、多边形、桑基丝带、饼或环扇区、柱、矩形树布局                                                                                  |

- 坐标取 10 的倍数，主体从 y≈120 开始。每画完一张就看一眼导出的 PNG，按 design-rules.md 的检查清单改到没有共线、穿框、交叉，标签不压框。
- 共用的布局规律（三列卡片、交替上下的标签）写成自己脚本里的循环，不要逐个硬写坐标。
- 依赖：Python 3.9+、draw.io 桌面版命令行（导出用）。

## diagram-design

- 何时用：发布级排版、要 HTML / SVG 输出、不超过 12 个节点。
- 结构和版式按 diagram-design 自己的规则。它的颜色模型是"纸 + 墨 + 一个强调色"的语义角色（`paper` / `ink` / `muted` / `soft` / `rule` / `accent` / `accent-tint` / `link` / `series-1…5`），不是四槽角色色，所以只能做到底色、正文、主色、系列色和 Mermaid 同源，节点填充风格仍是它自己的。
- 接法：`palette.py css [方案]` 输出的第二组变量（`--dd-paper`、`--dd-ink` …）就是按它的角色名算好的，映射关系：

  | diagram-design 角色      | 取自方案                                    |
  | ------------------------ | ------------------------------------------- |
  | `paper` / `paper-2`      | `bg` / `bg` 略加深                          |
  | `ink` / `ink-strong`     | `text` / `#111111`                          |
  | `muted` / `soft`         | `text` 向 `bg` 混 45% / 25%，压到对底 4.5:1 |
  | `rule` / `rule-solid`    | `ink` 12% 透明 / `border`                   |
  | `accent` / `accent-tint` | `primary`（压到 4.5:1）/ 它的 8% 透明       |
  | `link`                   | `line`（压到 4.5:1）                        |
  | `series-1…5`             | `series` 前 5 个                            |

- 一个项目只做一次：用这组值跑它的 onboarding 或保存成 profile（`diagram-design:profile`），之后它出的图自动用这套皮；单张图临时换色就把这些值填进它 style-guide 的对应角色。
- `.html` 源文件和导出的 PNG 一起交付。

### 统一风格

要让 diagram-design 的图和 drawio、Mermaid 的图像一套，就用一个以方案命名的 profile（如 `diagram-kit-macaron`）。内容是 diagram-design 当前的 style-guide 正文，按下表改几处后用 `diagram-design:profile` 保存。项目里用 `.diagram-design` 指向它。

| style-guide 的位置 | 改成                                                                                                                                                                                                                                                                      |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Semantic roles 表  | 填 `palette.py css [方案]` 的 `--dd-*` 值，映射见上表                                                                                                                                                                                                                     |
| Font source        | `system`：不请求 Google Fonts，中文走本机字体                                                                                                                                                                                                                             |
| Typography 表      | 一律用无衬线字体链（design-rules.md 的字体链），等宽字体只留给字段、端口、路径这类代码值。`title` 22px 加粗；用 `eyebrow` 放副标题，13px 常规、次要色、不全大写；`node-name` 13px 600；`sublabel` 11px；`arrow-label` 12px；`callout` 改为说明面板正文 12px，不用斜体衬线 |
| Stroke, radius 表  | 节点描边 1；连线 1.5，关键路径 2.5；`radius-md` 8，`radius-lg` 10                                                                                                                                                                                                         |

- 这样改会有意偏离 diagram-design 自带的「衬线 + 无衬线 + 等宽」约束；调用者要它原生的社论风时，用它的 `default` profile，不套这一节。
- 版式按 design-rules.md：标题区、横向分层带、两级文字卡片、说明面板、图例、读图行。
- 连线只用正交路径：SVG `path` 只写 `H` / `V` 段，拐角用小圆角，不用贝塞尔曲线；箭头统一用实心小三角。
- 坐标网格仍按它自己的 4px 硬规则，间距取 40、60 这类同时满足两边的值。

## 代码绘图（matplotlib / ECharts）

- 何时用：Mermaid 没有的数据图（散点、直方、箱线、热力、旭日、漏斗），节点要显示中文的桑基图，或需要精确坐标轴、多系列堆叠、双轴、交互。
- 依赖：matplotlib 或 echarts，二选一，装了哪个用哪个（ECharts 照 `scripts/sankey_echarts.js` 的写法改 `series` 出 SVG，要 PNG 用 Playwright）；两个都没有才停下来提示安装。
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

- 依赖全局安装的 echarts（`npm install -g echarts`）；脚本按 当前目录 → skill 的 `scripts/` → 全局 node_modules 的顺序找，都没有就退出并提示安装。
- 渲染：`echarts.init(null, null, { renderer: 'svg', ssr: true, width, height })`，然后 `chart.renderToSVGString()` 得到 SVG。
- 必须设 `animation: false`，否则导出的是动画中间帧，图只画了一半。
- 写完文件后调用 `chart.dispose()` 和 `process.exit(0)`，否则 Node 进程不会退出。
- 要 PNG@2x：用 Playwright 打开 SVG，设 `deviceScaleFactor: 2` 截图，依赖全局安装的 playwright 和 Chromium（`npm install -g playwright && npx playwright install chromium`）；或者交给 Playwright MCP 截图。缺了提示安装。
- 数据文件（CSV / JSON）和 SVG / PNG 一起交付，作为可编辑源文件。

## Figma

- 何时用：高保真交互稿、可演示的原型、需求阶段的 UI 设计，需要协作和演示时。
- 不用来导出图片，除非调用者点名；UI 线框图 / 低保真原型用 drawio。
- 颜色：把 `palette.py css [方案]` 的变量建成 Figma 颜色变量；项目已有设计系统时以设计系统为准。

## 文生图工具（如有）

- 何时用：非结构的配图，比如文章封面、插画、氛围图、概念示意图片。
- 不要用它画带大量文字的结构图（文字会乱），结构图用上面的工具。
- 提示词里写清：主体、构图、风格（扁平插画 / 等距 / 线稿）、比例，以及配色——从 `palette.py show [方案]` 里取主色、3–5 个系列色和背景色的 hex，和文档里其他图保持同一套方案。
