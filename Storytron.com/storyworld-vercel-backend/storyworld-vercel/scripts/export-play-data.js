import { getDb } from '../local/db.js'
import { exportHarnessDatasets } from '../local/researchExport.js'

const readArg = (name) => {
  const token = process.argv.find((entry) => entry.startsWith(`${name}=`))
  if (!token) return ''
  return token.slice(name.length + 1).trim()
}

const maxSessionsArg = Number.parseInt(readArg('--max-sessions'), 10)
const maxSessions = Number.isNaN(maxSessionsArg) ? 5000 : Math.min(100000, Math.max(1, maxSessionsArg))
const trmRoot = readArg('--trm-root')
const hrmRoot = readArg('--hrm-root')

const db = await getDb()
const manifest = await exportHarnessDatasets(db, {
  maxSessions,
  trmRoot,
  hrmRoot,
  backendRoot: process.cwd()
})

console.log(JSON.stringify(manifest, null, 2))
