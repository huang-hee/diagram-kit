#!/usr/bin/env node
// 把 package.json 的版本号同步进 SKILL.md frontmatter 的 metadata.version。
// changesets 只改 package.json，使用者看到的是 SKILL.md，所以 npm run version 在 changeset version 之后接着跑本脚本。
// 只替换 version 的值，不重写整个文件，保留 frontmatter 其他字段和正文。
import { readFileSync, writeFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

// 仓库根：本脚本在 .scripts/ 下，往上一级
const repo = join(dirname(fileURLToPath(import.meta.url)), '..')
const skill_path = join(repo, 'SKILL.md')

// 取 package.json 的版本
const { version } = JSON.parse(readFileSync(join(repo, 'package.json'), 'utf8'))
const source = readFileSync(skill_path, 'utf8')

// 只在开头的 frontmatter 块里找 metadata 下的 version 行：缩进两格、值带引号（单双引号都认，Prettier 会改成单引号）；LF / CRLF 都认
const frontmatter = /^---\r?\n[\s\S]*?\r?\n---/
const version_line = /(\r?\n {2}version:\s*)(["'])[^"'\r\n]*\2/
const matched = source.match(frontmatter)
if (!matched || !version_line.test(matched[0])) {
  console.error('✘ SKILL.md：frontmatter 里没有 metadata.version，请先手动加上再跑')
  process.exitCode = 1
} else {
  // 只改块内这一行，保留原引号和换行风格；用函数做替换，避免 "$1" 和版本号开头的数字连成 "$10"
  const next_block = matched[0].replace(version_line, (_, head, quote) => `${head}${quote}${version}${quote}`)
  // 外层替换也用函数，frontmatter 里出现 $& 这类模式串时不会被展开
  writeFileSync(skill_path, source.replace(matched[0], () => next_block))
  console.log(`✔ SKILL.md 的 metadata.version 已同步为 ${version}`)
}
