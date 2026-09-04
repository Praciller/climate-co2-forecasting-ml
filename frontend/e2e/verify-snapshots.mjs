import { execFileSync } from 'node:child_process'
import { existsSync, readdirSync } from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const frontendRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const repositoryRoot = path.resolve(frontendRoot, '..')
const snapshotRoot = path.join(frontendRoot, 'e2e', 'snapshots')

function collectPngs(directory) {
  if (!existsSync(directory)) return []
  return readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const entryPath = path.join(directory, entry.name)
    return entry.isDirectory() ? collectPngs(entryPath) : entry.name.endsWith('.png') ? [entryPath] : []
  })
}

const snapshots = collectPngs(snapshotRoot)
if (snapshots.length === 0) {
  console.error('Visual baseline missing or changed; review and commit canonical Linux baseline.')
  process.exit(1)
}

const status = execFileSync(
  'git',
  ['status', '--porcelain', '--untracked-files=all', '--', 'frontend/e2e/snapshots'],
  { cwd: repositoryRoot, encoding: 'utf8' },
).trim()

if (status) {
  console.error('Visual baseline missing or changed; review and commit canonical Linux baseline.')
  console.error(status)
  process.exit(1)
}

console.log(`Verified ${snapshots.length} committed Playwright visual baselines.`)
