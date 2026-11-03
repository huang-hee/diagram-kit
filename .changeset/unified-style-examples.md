---
'diagram-kit': minor
---

示例按统一风格重做，并补上整图示例

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
