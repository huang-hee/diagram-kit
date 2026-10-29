---
'diagram-kit': minor
---

三种工具统一出图风格。

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
