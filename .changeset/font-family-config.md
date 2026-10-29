---
'diagram-kit': patch
---

字体链改写在 Mermaid config 顶层的 `fontFamily`（`--init` 同样），原来放在 themeVariables 里不生效，中文会落到渲染器默认字体
