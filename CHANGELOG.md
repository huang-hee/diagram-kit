# diagram-kit

## 1.0.1

### Patch Changes

- 91c417f: diagram-design 的配色改为按它的语义角色（paper / ink / accent / series …）映射：`palette.py css` 多输出一组 `--dd-*` 变量，tools.md 写明映射表和 profile 做法

## 1.0.0

### Major Changes

- 首版：48 种图型按角色上色，12 套对所有图型通用的配色方案，输出 Mermaid / draw.io / CSS / 图表代码的配色；缺依赖时不执行、提示安装
