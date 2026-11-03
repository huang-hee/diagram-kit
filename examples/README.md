# 整图示例

每个 `.py` 用 `scripts/drawio_kit.py` 按 references/design-rules.md 的统一风格画一张完整的图：标题区、分层带、两级文字卡片、正交等粗连线、说明面板、图例、读图行。运行后在本目录生成同名 `.drawio`（可编辑）和 `.png`。

写新图时挑结构最接近的示例当骨架改，坐标取 10 的倍数，主体从 y≈120 开始。

| 示例                 | 图型                | 用到的组件                                                                                                              |
| -------------------- | ------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `flowchart.py`       | 流程图              | 主路径竖排一列、判断向右落到结果列；box（pill / diamond / cyl）、`key=True` 粗线、panel（note 和 soft）、legend、footer |
| `flowchart_large.py` | 流程图（>12 节点）  | 按中线循环摆主路径、doc 形状的产出文档用虚线挂右侧、回退线走左侧通道、1/4 端口（LT / LB）避免同边多线                   |
| `swimlane.py`        | 泳道图              | band 当泳道、跨泳道的 L 形 edge（`points`）、key 交接点、卡片图标（`icon=`）                                            |
| `app_arch.py`        | 应用架构            | band 分层、vband 横切关注点、ext 外部系统、1/4 端口（TL / TR / BL / BR）、dashed 异步线                                 |
| `sequence.py`        | 时序图              | seq：msg（sync / ret / async）、self_msg、note、frag / els / end、groups、finish                                        |
| `state.py`           | 状态图              | dot 起止、状态色 ok / bad、回环拐点                                                                                     |
| `er.py`              | ER 图               | table（pk / fk / sep / muted）、ER 鸟足箭头（`arrow` / `start_arrow`）                                                  |
| `mindmap.py`         | 思维导图            | mindmap 左右均分、`{'pending': True}` 待定项、按 `d.bounds` 定位说明区                                                  |
| `mindmap_radial.py`  | 放射图              | `mindmap(sides='radial')` 单层变体、标签里 `\n` 换行、pending 待定项                                                    |
| `logic_tree.py`      | 右展开逻辑树        | `mindmap(sides='right')` 当横向树、三层嵌套                                                                             |
| `fishbone.py`        | 鱼骨图              | fishbone                                                                                                                |
| `journey.py`         | 用户旅程            | chevron 阶段条、band 维度行、按列循环摆卡片、带图标的触点、badge 分值点 + line 情绪折线、note 机会点                    |
| `timeline.py`        | 时间线              | rect 轴段、带图标的圆（box circle + icon）、上下交替的文字块、`text(html=True)`                                         |
| `roadmap.py`         | 路线图              | chevron 阶段条、band 主题行、white / pending 卡片、按列循环摆位                                                         |
| `quadrant.py`        | 象限图              | rect 象限底（主色渐层 `P.paint(d.t.s, 'ramp:n')`）、line 坐标轴、badge 编号点、右侧两块 panel                           |
| `org.py`             | 树形图 / 组织结构图 | tree_down、虚线 edge 表示虚线汇报、按返回的总高定位说明区                                                               |
| `concept.py`         | 概念图              | box（circle 核心概念）、带关系词的 edge、dashed 例子线                                                                  |
| `affinity.py`        | 亲和图              | group 当组、sticky 按系列色轮换                                                                                         |
| `activity.py`        | 活动图（UML）       | dot、bar 分叉 / 汇合、box（diamond / para）、按比例端口对准并行分支                                                     |
| `communication.py`   | 通信图（UML）       | actor、box、带编号标签的 edge、用 points 把标签放到水平段上                                                             |
| `interaction.py`     | 交互概览图（UML）   | dot、frame（ref / sd 标签）、box（diamond）、带拐点的回退 edge                                                          |
| `timing.py`          | 时间图（UML）       | band 生命线行、rect 状态段、line 刻度轴与超时线                                                                         |
| `c4.py`              | C4 容器图           | actor、group（dashed 边界）、box（cyl）、ext 外部系统、带"动词 · 协议"标签的 edge                                       |
| `biz_arch.py`        | 业务架构图          | band 四层、box 网格（不足一行时居中）                                                                                   |
| `data_arch.py`       | 数据架构图          | group 当列、box（cyl）、1/4 端口汇入计算节点                                                                            |
| `tech_arch.py`       | 技术架构图          | band、box（white / key / sage）                                                                                         |
| `deploy_arch.py`     | 部署架构图          | group 嵌套（dashed VPC、浅底集群）、box（cyl）、bad 安全设备、ext 公网                                                  |
| `network.py`         | 网络拓扑图          | band（tint 换底色）、box（icon 传 mxgraph.cisco19 样式串）、bad 安全设备                                                |
| `class.py`           | 类图                | table（sep、sub 写构造型）、rel（inherit / assoc / depend）                                                             |
| `usecase.py`         | 用例图              | actor、group（dashed 边界）、box（pill）、小人用不同比例端口避免共线                                                    |
| `object.py`          | 对象图（UML）       | table、rel（assoc 带字段名）                                                                                            |
| `component.py`       | 组件图（UML）       | group、box（shape='component'）、port（circle 棒棒糖）、rel（link / depend）                                            |
| `package.py`         | 包图（UML）         | group 嵌套（外层浅底、内层白底描边）、box（shape='package'）、rel（depend）                                             |
| `uml_deploy.py`      | 部署图（UML）       | group（dashed 网络边界）、box（shape='cube' / 'doc'）嵌套、edge 标协议                                                  |
| `composite.py`       | 组合结构图（UML）   | group（带描边的类元框）、port（square 端口）、rel（link）                                                               |
| `profile.py`         | Profile 图（UML）   | table（sub 写 «metaclass» / «stereotype»）、rel（extension / link）                                                       |
| `requirement.py`     | 需求图              | table（sub 写 «requirement» 等构造型）、rel（depend 带关系词）                                                          |
| `ui_flow.py`         | 页面流程图          | box（pill / para / diamond）、dashed 回退 edge、sticky 交互说明                                                         |
| `wireframe.py`       | 线框图              | rect 画布与占位块、line 对角线、box 组件区块、badge 标注编号、panel 说明列表                                            |
| `story_map.py`       | 用户故事地图        | chevron 活动条、box 任务卡、sticky 故事卡、line 版本切线、pending 待定卡                                                |
| `gantt.py`           | 甘特图              | band 阶段行、rect 时间条、line 刻度与今日线、box（diamond）里程碑                                                       |
| `kanban.py`          | 看板                | rect 列底、box 列头（深色）与卡片（white）、badge 优先级                                                                |

UML 关系线用 `rel(a, b, kind)`：assoc / inherit / implement / depend / compose / aggregate / link；小人用 `actor()`，端口和接口棒棒糖用 `port()`；`box` 的 shape 另有 cube（设备）、component（组件）、package（文件夹包）。

图标：`box(..., icon='ios7:user')` 在卡片左侧放 draw.io 自带的线性图标（离线可用，常用名见 drawio_kit 的 `icon()` 注释）；要产品图标时用 drawio MCP 的 search_shapes 查到样式串整个传给 `icon=`；也可以直接传 emoji。深色底的卡片传 `icon_color=d.t.bg`。

运行单个：`python $SKILL/examples/flowchart.py`。需要 draw.io 桌面版命令行；环境变量 `DIAGRAM_MIN_SIDE` 控制导出 PNG 的长边像素（默认 4000，只要 2 倍图时设成 1）。
全部重跑：`python $SKILL/scripts/build_docs.py --examples`（仓库里的示例图按它的默认长边 2000 生成，`--min-side 4000` 可出规则要求的尺寸）。

每张图导出后看 PNG，对照 design-rules.md 末尾的检查清单：没有共线、穿框、交叉，标签不压框，面板没有大片空白。
