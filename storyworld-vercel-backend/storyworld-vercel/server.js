import cors from 'cors'
import express from 'express'
import { applyLocalMigration } from './local/db.js'
import { registerLocalRoutes } from './local/routes.js'

const app = express()
const port = Number.parseInt(process.env.PORT || '3000', 10)

app.use(
  cors({
    origin: ['http://127.0.0.1:4173', 'http://localhost:4173', 'http://127.0.0.1:5173', 'http://localhost:5173']
  })
)
app.use(express.json({ limit: '3mb' }))

registerLocalRoutes(app)

app.use((err, _req, res, _next) => {
  console.error('Unhandled server error:', err)
  res.status(500).json({ error: 'Internal server error' })
})

const start = async () => {
  await applyLocalMigration()
  app.listen(port, () => {
    console.log(`Storyworld local backend running on http://127.0.0.1:${port}`)
  })
}

start().catch((error) => {
  console.error('Failed to start local backend:', error)
  process.exit(1)
})
