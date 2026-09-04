import { spawn } from 'node:child_process'
import { existsSync } from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const scriptDirectory = path.dirname(fileURLToPath(import.meta.url))
const repositoryRoot = path.resolve(scriptDirectory, '..', '..')
const localWindowsPython = path.join(
  repositoryRoot,
  '.venv',
  'Scripts',
  'python.exe',
)
const configuredPython = process.env.PYTHON
const python =
  configuredPython ||
  (process.platform === 'win32' && existsSync(localWindowsPython)
    ? localWindowsPython
    : process.platform === 'win32'
      ? 'python'
      : 'python3')

function run(command, args, options = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, {
      cwd: repositoryRoot,
      stdio: 'inherit',
      ...options,
    })
    child.on('error', reject)
    child.on('exit', (code, signal) => {
      if (code === 0) {
        resolve()
        return
      }
      reject(new Error(`${command} exited with ${code ?? signal}.`))
    })
  })
}

try {
  await run(python, ['-m', 'src.pipeline'])
  const server = spawn(
    python,
    [
      '-m',
      'uvicorn',
      'src.api.main:app',
      '--host',
      '127.0.0.1',
      '--port',
      '8000',
    ],
    { cwd: repositoryRoot, stdio: 'inherit' },
  )

  const shutdown = () => {
    if (!server.killed) server.kill()
  }
  process.on('SIGINT', shutdown)
  process.on('SIGTERM', shutdown)
  server.on('exit', (code) => process.exit(code ?? 1))
} catch (error) {
  console.error(error)
  process.exitCode = 1
}
