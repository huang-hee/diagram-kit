# diagram-kit

给 AI agent 用的画图与配图 skill。agent 拿到"画一张 ××图"的要求后，按它走五步：判断图型 → 选工具 → 按角色取配色 → 出图 → 校验。

- 48 种图，分 7 类：思考梳理、流程行为、系统结构、建模设计、产品设计、计划进度、数据呈现。每种图定义了"角色"（开始 / 处理 / 判断、实体 / 核心实体、普通任务 / 进行中……），节点按角色上色。
- 12 套配色方案，对所有图型通用，一篇文档一套。颜色全部由 `scripts/palette.py` 派生输出（Mermaid 主题变量和 classDef、draw.io style、CSS 变量、图表 JSON），agent 不手写 hex。
- 文字对比度、强调色是否独立有脚本校验；连线、描边、容器对页面的对比度在派生时强制达标。

## 安装

### 1. 放进 skill 目录

**用 skills CLI 装（推荐）**，一条命令装到一个或多个 agent（需要 Node.js 22.20+）：

```bash
# 装到个人目录，Claude Code 和 Codex 都能用
npx skills add huang-hee/diagram-kit -g -a claude-code codex -y

# 只装到当前项目（去掉 -g），或者换别的 agent（cursor、gemini-cli、github-copilot …）
npx skills add huang-hee/diagram-kit -a cursor -y
```

它会把 skill 放到各 agent 的目录（Claude Code `~/.claude/skills/`，Codex `~/.agents/skills/`），默认用软链指向同一份；以后 `npx skills update` 更新，`npx skills remove diagram-kit` 删除。

**手动装**：把整个 `diagram-kit/` 目录复制（或软链）到 agent 平台的 skill 目录，目录名保持 `diagram-kit`：

| 平台                 | 个人级目录                       | 项目级目录                                |
| -------------------- | -------------------------------- | ----------------------------------------- |
| Claude Code          | `~/.claude/skills/`              | `.claude/skills/`                         |
| Codex                | `~/.agents/skills/`              | `.agents/skills/`（从当前目录逐层向上找） |
| Cursor               | `~/.cursor/skills/`、`~/.agents/skills/` | `.agents/skills/`、`.cursor/skills/`、`.claude/skills/` |
| GitHub Copilot CLI   | `~/.copilot/skills/`、`~/.agents/skills/` | `.github/skills/`、`.agents/skills/`、`.claude/skills/` |
| 其他                 | 以该平台文档为准                 | 多数平台认 `.agents/skills/`              |

`SKILL.md` 的 frontmatter 只用了 `name` 和 `description`，各平台都能加载；`agents/openai.yaml` 是给 Codex / ChatGPT 桌面端用的展示名和调用策略，其他平台会忽略它。Codex 里也可以直接让内置的 `$skill-installer` 从这个仓库装。

### 2. 按要用的工具装依赖

**一键装**（按系统整段复制执行；只用 Mermaid 的话装到 mermaid-cli 那行就够）：

```bash
# macOS
brew install node python-matplotlib
brew install --cask drawio                                     # 要 draw.io 桌面版时
npm install -g --allow-scripts=puppeteer @mermaid-js/mermaid-cli echarts
# 渲染报 Could not find chrome-headless-shell 时，补下浏览器：
cd "$(npm root -g)/@mermaid-js/mermaid-cli" && npx puppeteer browsers install chrome-headless-shell
```

```powershell
# Windows（先装 Node.js 和 Python，包名以 winget search 为准）
winget install OpenJS.NodeJS.LTS Python.Python.3 JGraph.Draw
pip install matplotlib
npm install -g --allow-scripts=puppeteer @mermaid-js/mermaid-cli echarts
```

```bash
# Linux（Debian / Ubuntu）
sudo apt install -y nodejs npm python3-matplotlib fonts-noto-cjk
npm install -g --allow-scripts=puppeteer @mermaid-js/mermaid-cli echarts
```

装完验证：

```bash
mmdc --version && node -e "require('$(npm root -g)/echarts')" && python -c "import matplotlib" && echo OK
```

skill 运行时不会自动安装任何东西：缺什么，agent 会停下来提示装什么（唯一例外：中文节点的桑基图缺 echarts 时直接退回 Mermaid + 对照表）。按下表装需要的部分。

| 组件                                | 用途                                                                 | 安装                                                                                                      |
| ----------------------------------- | -------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| Python 3.8+                         | `palette.py`（取色）、`sync_refs.py`、`render_check.py`，无第三方依赖 | python.org 或系统包管理器。命令名是 `python`，只有 `python3` 的机器把文档里的命令换成 `python3`           |
| Mermaid 渲染                        | 校验和预览 Mermaid 代码                                              | 二选一：Mermaid 的 MCP server（按平台的 MCP 配置方式接入）；或本地 `npm install -g --allow-scripts=puppeteer @mermaid-js/mermaid-cli`（提供 `mmdc`；`--allow-scripts` 让 puppeteer 把 Chrome 一起下下来，漏了就到 `$(npm root -g)/@mermaid-js/mermaid-cli` 下执行 `npx puppeteer browsers install chrome-headless-shell`，或设 `PUPPETEER_EXECUTABLE_PATH` 指向已有的 Chrome） |
| Node.js 18+                         | `scripts/sankey_echarts.js`（中文节点的桑基图）                        | nodejs.org                                                                                                |
| echarts                             | 同上                                                                 | `npm install -g echarts`（脚本会去全局 node_modules 找）                                                   |
| playwright + Chromium               | 桑基图脚本的 `--png`                                                 | `npm install -g playwright && npx playwright install chromium`                                            |
| matplotlib                          | 散点、直方、箱线等代码绘图                                           | `pip install matplotlib`；装完中文字体后清掉 `~/.cache/matplotlib`                                        |
| draw.io 桌面版                      | 超过 12 个节点、真实产品图标、要交给别人编辑的图；命令行导出 PNG      | https://www.drawio.com/ ；有 draw.io 的插件或 MCP 时 agent 会优先用它们建图                               |
| 中文字体                            | 所有本地渲染（mmdc、matplotlib、ECharts、draw.io）                   | macOS 自带苹方；Windows 自带微软雅黑；Linux 装 Noto Sans CJK（Debian / Ubuntu：`fonts-noto-cjk`）         |
| diagram-design、Figma、文生图工具   | 可选；会话里有对应的 skill / MCP 时 agent 才会用                     | 各自的安装方式                                                                                            |

### 3. 在全局指令里写工具选择规则

skill 本身不规定"什么场景用什么工具"，由用户指令或项目规则决定，没有规则时默认 Mermaid 代码块。建议在 `CLAUDE.md` / `AGENTS.md` 里写一段，例如：

```markdown
## 画图与配图

按顺序匹配，命中第一行就停：
1. 没有节点和连线的配图（插画、封面）→ 文生图工具
2. 高保真 UI 稿 → Figma
3. 超过 12 个节点、要真实产品图标、要交给别人编辑 → drawio
4. 其余有结构的图 → mermaid 代码块

命中后按 diagram-kit 执行：判型、取配色、出图、校验。
导出的图片放文档同级 assets/，源文件也放进去。
```

## agent 怎么用

1. **判型**：按 `SKILL.md` 的表选 type id（如 `flowchart`、`er`、`gantt`），细节看 `references/types-*.md`。
2. **取配色**：`python <skill 目录>/scripts/palette.py roles <type> [方案]` 列出每个角色的填充 / 描边 / 字色。不指定方案用默认 `macaron`。
3. **出图**：写好 Mermaid 正文、节点挂上角色 class，`palette.py mermaid <type> [方案] --body 正文.mmd` 输出带配色的完整代码；draw.io / CSS / 图表代码分别用 `drawio` / `css` / `chart` 子命令取色。
4. **校验**：渲染一遍，对照 `references/design-rules.md` 的清单检查。

命令速查：

```bash
python scripts/palette.py schemes                     # 12 套方案，标出默认
python scripts/palette.py types                       # 48 种图
python scripts/palette.py roles flowchart              # 角色 -> 颜色
python scripts/palette.py mermaid er latte --body er.mmd --md   # 带配色的 Mermaid 代码块
python scripts/palette.py drawio deploy_arch           # draw.io style 字符串
python scripts/palette.py css sage                     # CSS 变量
python scripts/palette.py chart                        # 图表代码用的 JSON 色表
node scripts/sankey_echarts.js data.csv --png          # 中文节点的桑基图
```

## 配色方案

| 方案      | 名称     | 气质                                   |
| --------- | -------- | -------------------------------------- |
| `macaron` | 马卡龙   | 薰衣草 / 蜜桃 / 薄荷 / 杏，宝蓝强调（默认） |
| `cotton`  | 棉糖     | 粉蓝 / 粉红 / 粉绿 / 鹅黄，灰线        |
| `mist`    | 薄雾     | 淡蓝 / 淡绿 / 杏 / 淡紫，青蓝强调      |
| `morandi` | 莫兰迪   | 灰绿 / 杏 / 淡紫 / 淡青，橄榄强调      |
| `cream`   | 奶油     | 奶油 / 卡其 / 淡绿，橄榄棕强调         |
| `pebble`  | 鹅卵石   | 蓝灰 / 藕粉 / 浅灰，石墨强调，冷灰底   |
| `sage`    | 鼠尾草   | 鼠尾草绿四阶，大地色系列               |
| `candy`   | 糖果     | 薰衣草 / 长春花 / 青 / 粉红，靛蓝强调  |
| `slate`   | 石板珊瑚 | 石板蓝 + 珊瑚红，暖白底                |
| `moss`    | 苔藓     | 苔绿 / 灰绿 / 奶黄，深苔强调           |
| `latte`   | 拿铁     | 杏黄 / 薄荷 / 琥珀，炭灰强调           |
| `blush`   | 胭脂     | 粉 / 珊瑚 / 米粉，灰紫强调，暖粉底     |

每套方案由 4 个槽色、1 个主色和页面底色 / 正文色 / 连线色定义，描边、字色、容器色、系列色、渐层按同一套规则派生，所以同一方案下流程图、ER 图、饼图、甘特图看起来是一家人。完整色值见 `references/schemes.md`。

## 目录

```text
diagram-kit/
├── SKILL.md                  # agent 读的入口：五步流程、图型表、命令
├── agents/openai.yaml        # Codex / ChatGPT 桌面端的展示名与调用策略
├── references/
│   ├── tools.md              # 各工具怎么接配色、导出
│   ├── design-rules.md       # 配色与版式规则、检查清单
│   ├── schemes.md            # 配色总表（生成）
│   └── types-*.md            # 每种图的用途、写法、示例、角色色表
└── scripts/
    ├── palette.py            # 配色方案、角色表、各工具的输出
    ├── sync_refs.py          # 从 palette.py 重新生成 references 里的色表
    ├── render_check.py       # 用 mmdc 渲染全部示例，抓语法和主题问题
    └── sankey_echarts.js     # ECharts 服务端渲染桑基图
```

## 改配色

方案、角色、默认方案都在 `scripts/palette.py` 的 `SCHEMES`、`TYPES`、`DEFAULT_SCHEME`。改完依次跑：

```bash
python scripts/palette.py check      # 结构校验 + 文字对比度
python scripts/sync_refs.py          # 重新生成 references 里的色表
python scripts/render_check.py --all # 渲染全部示例 × 全部方案（需要 mmdc）
```

## 版本与发版

版本号在 `SKILL.md` frontmatter 的 `metadata.version`，和 `package.json` 保持一致，由 changesets 管理。改动了 `SKILL.md`、`references/`、`scripts/`、`agents/` 这些运行时文件时：

```bash
npx changeset              # 写一条 changeset：配色值、角色、命令变了选 minor，文档措辞选 patch
npm run version            # 消费 changeset：升版本、写 CHANGELOG.md、同步到 SKILL.md
git commit -am "chore: 发布 vX.Y.Z" && npx changeset git-tag && git push --follow-tags
```

`npx skills add` 装的是仓库 HEAD；要固定某个版本，用 GitHub Release 的 zip 地址装，或者 `git clone` 后切到对应的 tag 再软链。

## 许可证

MIT
