#!/usr/bin/env node
/**
 * 节点名可以是中文（任意 Unicode）的桑基图，由 ECharts 在服务端渲染。
 * Mermaid 的桑基图词法只认 ASCII 节点名，要在图里显示中文时用这个脚本。
 *
 * 用法：
 *   node sankey_echarts.js <data.csv> [方案] [--out assets/名字] [--width 720] [--height 360] [--png]
 *
 *   data.csv   每行一条流向：source,target,value。节点名可以直接写中文；写成 英文|中文 时显示中文部分。
 *              空行、%% 注释和 "sankey" 图头会跳过。
 *   方案       palette.py 的方案 id（默认用全局默认方案）
 *   --out      输出路径，不带扩展名（默认：和 CSV 同目录同名）
 *   --png      同时用 Playwright 输出 <out>.png（2 倍）
 *
 * 依赖：echarts；--png 还要 playwright 和 Chromium。缺了不执行，提示安装。
 */
const fs = require('node:fs')
const path = require('node:path')
const { execFileSync } = require('node:child_process')

/**
 * 从 scripts 目录或当前目录加载依赖，找不到就退出并提示安装
 * @param {string} name 包名
 * @param {string} hint 安装提示
 * @returns {any} 模块
 */
function loadDependency(name, hint) {
  // 先在脚本目录找，再在当前目录找
  for (const base of [__dirname, process.cwd()]) {
    try {
      return require(require.resolve(name, { paths: [base] }))
    } catch (e) {
      if (e.code !== 'MODULE_NOT_FOUND') throw e
    }
  }
  console.error(`缺少依赖 ${name}，不执行。${hint}`)
  process.exit(1)
}

/**
 * 解析一行 CSV，支持双引号包裹和 "" 转义
 * @param {string} line 一行文本
 * @returns {string[]} 各字段（已去首尾空白）
 */
function parseCsvLine(line) {
  const fields = []
  let current = ''
  let quoted = false
  for (let i = 0; i < line.length; i++) {
    const ch = line[i]
    if (quoted) {
      if (ch === '"' && line[i + 1] === '"') {
        current += '"'
        i++
      } else if (ch === '"') quoted = false
      else current += ch
    } else if (ch === '"') quoted = true
    else if (ch === ',') {
      fields.push(current)
      current = ''
    } else current += ch
  }
  fields.push(current)
  return fields.map((s) => s.trim())
}

/**
 * 调 palette.py 取图表色表，python 不在 PATH 时退回 python3
 * @param {string} scheme 方案 id
 * @returns {object} chart 命令输出的 JSON
 */
function loadPalette(scheme) {
  const script = path.join(__dirname, 'palette.py')
  const script_args = scheme ? ['chart', scheme] : ['chart']
  let last_error = null
  // 按顺序试两个命令名
  for (const python of ['python', 'python3']) {
    try {
      return JSON.parse(execFileSync(python, [script, ...script_args], { encoding: 'utf8' }))
    } catch (e) {
      last_error = e
      if (e.code !== 'ENOENT') break
    }
  }
  console.error(`调不到 palette.py：${last_error && last_error.message}`)
  process.exit(1)
}

/**
 * 读 CSV 并整理成 ECharts 的 nodes / links
 * @param {string} csv_path CSV 路径
 * @returns {{nodes: string[], links: {source: string, target: string, value: number}[]}}
 */
function readLinks(csv_path) {
  const rows = fs
    .readFileSync(csv_path, 'utf8')
    .split(/\r?\n/)
    .map((raw) => raw.trim())
    .filter((line) => line && !line.startsWith('%%') && !/^sankey(-beta)?$/i.test(line))
    .map(parseCsvLine)
  // 英文|中文 可能只在节点第一次出现时写，后面裸英文名要映射到同一个节点
  const zh_names = {}
  for (const [a, b] of rows) {
    for (const n of [a, b]) {
      if (n.includes('|')) {
        const [en, cn] = n.split('|').map((s) => s.trim())
        if (!(en in zh_names)) zh_names[en] = cn
      }
    }
  }
  // 显示名：有中文映射用中文，否则用原名
  const displayName = (n) => {
    const en = n.includes('|') ? n.split('|')[0].trim() : n
    return zh_names[en] || (n.includes('|') ? n.split('|')[1].trim() : n)
  }
  const nodes = []
  const links = []
  for (const [a, b, v] of rows) {
    const [source, target] = [displayName(a), displayName(b)]
    for (const n of [source, target]) if (!nodes.includes(n)) nodes.push(n)
    links.push({ source, target, value: Number(v) })
  }
  return { nodes, links }
}

/**
 * 用 ECharts 服务端渲染出 SVG 字符串
 * @param {object} echarts echarts 模块
 * @param {object} colors palette.py chart 的色表
 * @param {string[]} nodes 节点名
 * @param {object[]} links 流向
 * @param {number} width 宽
 * @param {number} height 高
 * @returns {string} SVG
 */
function renderSvg(echarts, colors, nodes, links, width, height) {
  const chart = echarts.init(null, null, { renderer: 'svg', ssr: true, width, height })
  chart.setOption({
    animation: false, // 服务端渲染开着动画会截到中间帧
    backgroundColor: colors.background,
    textStyle: {
      color: colors.text,
      fontFamily: 'PingFang SC, Microsoft YaHei, Noto Sans CJK SC, Source Han Sans SC, sans-serif',
    },
    series: [
      {
        type: 'sankey',
        left: 16,
        top: 16,
        bottom: 16,
        right: 96,
        nodeWidth: 14,
        nodeGap: 14,
        draggable: false,
        lineStyle: { color: 'source', opacity: 0.45, curveness: 0.5 },
        label: { color: colors.text, fontSize: 13, formatter: '{b}  {c}' }, // 名字 + 合计，和 Mermaid 默认一致
        data: nodes.map((name, i) => ({
          name,
          itemStyle: { color: colors.nodes[i % colors.nodes.length], borderWidth: 0 },
        })),
        links,
      },
    ],
  })
  const svg = chart.renderToSVGString()
  chart.dispose()
  return svg
}

/**
 * 用 Playwright 把 SVG 截成 2 倍 PNG
 * @param {string} svg SVG 字符串
 * @param {string} png_path 输出路径
 */
async function writePng(svg, png_path) {
  const { chromium } = loadDependency('playwright', '请先安装：npm i playwright && npx playwright install chromium')
  const browser = await chromium.launch()
  const page = await browser.newPage({ deviceScaleFactor: 2 })
  await page.setContent(`<html><body style="margin:0">${svg}</body></html>`)
  await page.locator('svg').first().screenshot({ path: png_path })
  await browser.close()
}

/**
 * 入口：解析参数、取色、渲染、写文件
 */
async function main() {
  const args = process.argv.slice(2)
  const option = (flag, fallback) => (args.includes(flag) ? args[args.indexOf(flag) + 1] : fallback)
  const value_flags = ['--out', '--width', '--height']
  const positional = args.filter((a, i) => !a.startsWith('--') && !value_flags.includes(args[i - 1]))
  if (!positional.length) {
    console.error('用法：node sankey_echarts.js <data.csv> [方案] [--out assets/名字] [--png]')
    process.exit(1)
  }
  const csv_path = positional[0]
  const scheme = positional[1] || ''
  const out_base = option('--out', csv_path.replace(/\.[^./\\]+$/, ''))
  const width = Number(option('--width', 720))
  const height = Number(option('--height', 360))
  // 依赖缺失时先停下来
  const echarts = loadDependency('echarts', `请先安装：cd "${__dirname}" && npm i echarts`)
  // 取色、读数据、渲染
  const colors = loadPalette(scheme)
  const { nodes, links } = readLinks(csv_path)
  const svg = renderSvg(echarts, colors, nodes, links, width, height)
  // 写 SVG
  fs.mkdirSync(path.dirname(path.resolve(out_base)), { recursive: true })
  fs.writeFileSync(`${out_base}.svg`, svg)
  console.log(`${out_base}.svg`)
  // 可选写 PNG
  if (args.includes('--png')) {
    await writePng(svg, `${out_base}.png`)
    console.log(`${out_base}.png`)
  }
  process.exit(0) // ECharts 会留着定时器，要显式退出
}

main()
