---
name: diagram-kit
description: 画图与配图：判断图型、按角色取统一配色、出图并校验。覆盖流程、时序、状态、架构、UML、ER、思维导图、甘特、看板、象限、桑基等 48 种图和文档配图。画图、出图、配图、改图的样式或配色时使用。
metadata:
  version: "1.0.0"
---

# diagram-kit

画图分五步：判型 → 选工具 → 取配色 → 出图 → 校验。颜色一律从 `scripts/palette.py` 取，不手写 hex。

- `$SKILL` 指本 skill 所在目录，执行命令前换成加载时给出的绝对路径。
- 命令里的 `python` 在只有 `python3` 的机器上换成 `python3`。
- 某一步需要的工具或依赖不可用（渲染器、draw.io、echarts、playwright、matplotlib、中文字体等）：不执行，不拿别的工具顶替，告诉调用者缺什么、怎么装（安装清单见 README.md），等指令。

## 1. 判型

按"要讲清什么"选 type id。拿不准时读对应参考文件开头的选型表，以及每种图的"用来 / 别用"。

| 类别     | type id                                                                                                                                                                     | 参考文件                      |
| -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------- |
| 思考梳理 | `mindmap` 思维导图、`org` 树形图 / 组织结构图、`fishbone` 鱼骨图、`concept` 概念图、`affinity` 亲和图                                                                       | references/types-thinking.md  |
| 流程行为 | `flowchart` 流程图、`swimlane` 泳道图、`sequence` 时序图、`state` 状态图、`activity` 活动图、`communication` 通信图、`interaction` 交互概览图、`timing` 时间图              | references/types-flow.md      |
| 系统结构 | `c4` C4 模型、`biz_arch` 业务架构、`app_arch` 应用架构、`data_arch` 数据架构、`tech_arch` 技术架构、`deploy_arch` 部署架构、`network` 网络拓扑                              | references/types-structure.md |
| 建模设计 | `class` 类图、`er` ER 图、`usecase` 用例图、`object` 对象图、`component` 组件图、`package` 包图、`uml_deploy` UML 部署图、`composite` 组合结构图、`profile` Profile 图      | references/types-modeling.md  |
| 产品设计 | `journey` 用户旅程图、`requirement` 需求图、`ui_flow` 页面流程图、`wireframe` 线框图 / 原型图、`story_map` 用户故事地图                                                     | references/types-product.md   |
| 计划进度 | `gantt` 甘特图、`timeline` 时间线、`roadmap` 路线图、`kanban` 看板、`gitgraph` Git 分支图                                                                                   | references/types-planning.md  |
| 数据呈现 | `bar_line` 柱状 / 折线、`pie` 饼图、`quadrant` 象限图、`sankey` 桑基图、`radar` 雷达图、`scatter` 散点图、`distribution` 直方图 / 箱线图、`venn` 韦恩图、`treemap` 矩形树图 | references/types-data.md      |

表里没有的叫法，按结构归到最近的类型并沿用它的角色：BPMN → `swimlane`（规范符号用 drawio 的 BPMN 图形库）；数据流图 DFD → `data_arch`；决策树、PERT 图 → `flowchart`；功能结构图、信息架构图、站点地图 → `org`；漏斗图 → `bar_line`（横向）或代码绘图；热力图、旭日图 → 代码绘图，配色取 `distribution` / `treemap`；SWOT、商业画布、矩阵类 → drawio 或 diagram-design，配色取 `quadrant`。

## 2. 选工具

用哪个工具按调用者的指令或项目规则定；没有规则时默认 Mermaid 代码块。各工具怎么接配色、怎么导出见 references/tools.md。

## 3. 取配色

```bash
python $SKILL/scripts/palette.py schemes              # 全部方案，标出默认
python $SKILL/scripts/palette.py roles <type> [方案]   # 这种图每个角色的 填充 / 描边 / 字色
```

- 所有方案对所有图型通用。不指定方案就用默认方案。
- 一篇文档、一批图只用一套方案；文档里已经有图的，沿用已有的方案。
- 调用者描述风格（"商务一点""清新""低饱和"）时，按 references/schemes.md 的"气质"列挑。
- 节点按"角色"上色：每种图有哪些角色（class 名）、对应哪个 token，见参考文件里该图的配色表。颜色表达类型，分组用容器（subgraph / 泳道 / 边界）表达。

## 4. 出图

**Mermaid**

1. 先写正文：拿参考文件里该图的示例当骨架，节点挂上角色 class（`A[锁定库存]:::process`），存成文件。
2. 套配色：`python $SKILL/scripts/palette.py mermaid <type> [方案] --body 正文.mmd`，输出带配色的完整代码（配置 + 图头 + 正文 + classDef）。正文里自己写了图头（如 `flowchart TB`）会保留。
3. 结果放进 md 的 ` ```mermaid ` 代码块（加 `--md` 直接输出带围栏的代码块）。目标平台不认 YAML frontmatter 时加 `--init`，改输出 `%%{init: ...}%%` 写法。

**其他工具**

| 工具                        | 取色命令                          | 用法                                                                                                                                                      |
| --------------------------- | --------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| drawio                      | `palette.py drawio <type> [方案]` | 每个角色、连线、容器、泳道、文字的 style 字符串，建图时直接用；第一行是页面背景色                                                                         |
| diagram-design / HTML / SVG | `palette.py css [方案]`           | CSS 变量；第二组按 diagram-design 的角色命名（paper / ink / accent …），填进它的 profile 或 style-guide                                                    |
| 代码绘图                    | `palette.py chart [方案]`         | JSON：background / text / axis / grid / categorical / sequential / nodes / state；中文节点的桑基图直接用 `node $SKILL/scripts/sankey_echarts.js 数据.csv` |
| 文生图工具（如有）          | `palette.py show [方案]`          | 把主色和 3–5 个系列色的 hex 写进提示词                                                                                                                    |
| Figma                       | `palette.py css [方案]`           | 建成 Figma 颜色变量                                                                                                                                       |

## 5. 校验

- Mermaid：用 Mermaid 渲染工具（MCP 或本地 mmdc）渲染一遍，看图检查：文字有没有截断、连线有没有交叉、颜色是否按角色生效。
- 已知限制：
  - `sankey-beta` 的节点名只能用 ASCII 字符，中文加引号也不行。两种做法：
    - 节点写成 `英文|中文`，加 `--md` 输出代码块和中英对照表。
    - 用 `scripts/sankey_echarts.js` 让图里直接显示中文。
    - 详见 types-data.md 的桑基图一节。
  - `requirementDiagram` 的标识用英文，中文写在 `text` 里。
  - C4 的边界（`Container_Boundary` 等）没有样式宏，只能是 Mermaid 默认的虚线框。
  - 带 `-beta` 的图型（swimlane / usecase / architecture / ishikawa / venn / treemap / radar / xychart / block / sankey）以及 frontmatter 配置，在较旧的渲染器（部分 IDE 插件、文档平台、代码托管平台）上可能不显示。先确认目标平台能渲染；不能就按该图"工具"一栏换写法或换工具。
- 对照 references/design-rules.md 末尾的检查清单过一遍。
- 导出图片和源文件的存放位置按调用者或项目的规则；文档和图里不写工具版本、验证日期这类过程信息。

## 维护配色

方案和每种图的角色表都在 `scripts/palette.py`（`SCHEMES`、`TYPES`、`DEFAULT_SCHEME`）。改完依次运行：

```bash
python $SKILL/scripts/palette.py check     # 结构校验 + 所有角色字对填充的对比度
python $SKILL/scripts/sync_refs.py         # 刷新 references 里的色表和 schemes.md
python $SKILL/scripts/render_check.py      # 用 mmdc 渲染参考文件里的全部示例（--all 渲染每套方案）
```

## 参考文件

- references/tools.md：各工具的配色接法、布局技巧、导出命令和限制
- references/design-rules.md：配色与版式规则、drawio 尺寸、出图检查清单
- references/schemes.md：全部配色方案总表（气质、色值、派生规则）
- references/types-\*.md：每种图的用途、写法、示例和角色色表
