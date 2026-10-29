# diagram-kit 验证记录

| 验证时间         | 验证详情                                                  | 验证资产                       | 场景数                                             | 结果概览                                        |
| ---------------- | --------------------------------------------------------- | ------------------------------ | -------------------------------------------------- | ----------------------------------------------- |
| 2026-10-29 18:20 | [看板](https://claude.ai/artifact/BwzJv89R9kNUeXSzYgUaTu) | diagram-kit（b2be646 + 预检规则、图标缺失规则改后；CLAUDE.md 改为超过 12 节点直接 drawio） | 上轮未通过的 S23 ×3（期望改为 drawio 真执行）、N10 ×1、T01 ×1 | 5/5 |
| 2026-10-29 17:50 | [看板](https://claude.ai/artifact/BwzJv89R9kNUeXSzYgUaTu) | diagram-kit（b2be646 + 预检规则改后） | 工具真执行：T01 drawio、T02 diagram-design、T03 文生图，各 sonnet / opus 一轮 | 5/6（T01 sonnet 因图库无 RDS 官方图标停下来问） |
| 2026-10-29 17:30 | [看板](https://claude.ai/artifact/BwzJv89R9kNUeXSzYgUaTu) | diagram-kit（b2be646 + 预检规则改为"备选也没有才停"） | 回归：S12 / S13 / S15 各 3 轮、R02 / R03 各 3 轮、N04 / N10 各 1 次 | with 17/18，路由 6/6；此前 opus 的"停下来问"查明是临时目录的自动记忆串扰 |
| 2026-10-29 16:40 | [看板](https://claude.ai/artifact/BwzJv89R9kNUeXSzYgUaTu) | diagram-kit（b2be646，v1.0.5） | 补跑 S27（无 / 有 matplotlib 各 3 轮） | with 3/3 + 3/3（无 matplotlib 时自动改走 ECharts） |
| 2026-10-29 15:40 | [看板](https://claude.ai/artifact/BwzJv89R9kNUeXSzYgUaTu) | diagram-kit（35c3d70，v1.0.3） | 补跑 6 个场景（S12 / S13 / S14 / S15 / S18 / S27） | with 13/18，其中 S14、S18 由 1/3、2/3 升到 3/3  |
| 2026-10-29 14:30 | [看板](https://claude.ai/artifact/BwzJv89R9kNUeXSzYgUaTu) | diagram-kit（3446d7c）         | 37 + 6 路由（另 3 个未覆盖）                       | with 97/111，路由 18/18，without 1/39           |
