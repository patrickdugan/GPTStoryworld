import { applyLocalMigration } from '../local/db.js'

await applyLocalMigration()
console.log('Local SQLite migration complete.')
