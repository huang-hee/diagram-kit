---
'diagram-kit': patch
---

echarts / playwright 改为全局安装，`sankey_echarts.js` 会到全局 node_modules 找包，skill 目录不再放运行时依赖
