import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import sqlite3 from 'sqlite3'
import { open } from 'sqlite'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const rootDir = path.resolve(__dirname, '..')
const dataDir = path.join(rootDir, 'data')
const dbFile = path.join(dataDir, 'storyworld.local.db')

let dbPromise

const ensureDataDir = () => {
  if (!fs.existsSync(dataDir)) {
    fs.mkdirSync(dataDir, { recursive: true })
  }
}

const runMigrations = async (db) => {
  await db.exec(`PRAGMA foreign_keys = ON;`)

  await db.exec(`
    CREATE TABLE IF NOT EXISTS storyworlds (
      id TEXT PRIMARY KEY,
      title TEXT NOT NULL,
      description TEXT DEFAULT '',
      num_characters INTEGER NOT NULL DEFAULT 3,
      num_themes INTEGER NOT NULL DEFAULT 2,
      num_variables INTEGER NOT NULL DEFAULT 5,
      encounter_length INTEGER NOT NULL DEFAULT 500,
      custom_prompt TEXT DEFAULT '',
      encounter TEXT NOT NULL,
      system_prompt TEXT DEFAULT '',
      is_public INTEGER NOT NULL DEFAULT 1,
      genre TEXT DEFAULT 'Diplomacy',
      size_tag TEXT DEFAULT 'standard',
      theme_variant TEXT DEFAULT 'midnight',
      cover_image TEXT,
      banner_image TEXT,
      tags TEXT DEFAULT '[]',
      views INTEGER NOT NULL DEFAULT 0,
      likes INTEGER NOT NULL DEFAULT 0,
      fork_count INTEGER NOT NULL DEFAULT 0,
      forked_from TEXT,
      model_used TEXT DEFAULT 'gpt-4.1',
      temperature REAL DEFAULT 0.8,
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      updated_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
  `)

  await db.exec(`
    CREATE TABLE IF NOT EXISTS play_sessions (
      id TEXT PRIMARY KEY,
      storyworld_id TEXT,
      storyworld_title TEXT,
      genre TEXT,
      size_tag TEXT,
      theme_variant TEXT,
      source TEXT DEFAULT 'storyworld-ui',
      status TEXT DEFAULT 'active',
      started_at TEXT NOT NULL DEFAULT (datetime('now')),
      ended_at TEXT,
      meta TEXT DEFAULT '{}',
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      updated_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
  `)

  await db.exec(`
    CREATE TABLE IF NOT EXISTS play_events (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      session_id TEXT NOT NULL,
      seq INTEGER NOT NULL DEFAULT 0,
      ts TEXT NOT NULL DEFAULT (datetime('now')),
      event_type TEXT NOT NULL DEFAULT 'choice',
      encounter_id TEXT,
      next_encounter TEXT,
      choice_index INTEGER,
      choice_text TEXT,
      narrative TEXT,
      options_json TEXT DEFAULT '[]',
      state_json TEXT DEFAULT '{}',
      latency_ms INTEGER,
      meta TEXT DEFAULT '{}',
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      FOREIGN KEY (session_id) REFERENCES play_sessions(id) ON DELETE CASCADE
    );
  `)

  await db.exec(`CREATE INDEX IF NOT EXISTS idx_storyworlds_public ON storyworlds (is_public);`)
  await db.exec(`CREATE INDEX IF NOT EXISTS idx_storyworlds_created ON storyworlds (created_at DESC);`)
  await db.exec(`CREATE INDEX IF NOT EXISTS idx_storyworlds_likes ON storyworlds (likes DESC);`)
  await db.exec(`CREATE INDEX IF NOT EXISTS idx_storyworlds_views ON storyworlds (views DESC);`)
  await db.exec(`CREATE INDEX IF NOT EXISTS idx_storyworlds_genre ON storyworlds (genre);`)
  await db.exec(`CREATE INDEX IF NOT EXISTS idx_storyworlds_size_tag ON storyworlds (size_tag);`)
  await db.exec(`CREATE INDEX IF NOT EXISTS idx_storyworlds_theme_variant ON storyworlds (theme_variant);`)
  await db.exec(`CREATE INDEX IF NOT EXISTS idx_play_sessions_storyworld ON play_sessions (storyworld_id);`)
  await db.exec(`CREATE INDEX IF NOT EXISTS idx_play_sessions_started ON play_sessions (started_at DESC);`)
  await db.exec(`CREATE INDEX IF NOT EXISTS idx_play_events_session_seq ON play_events (session_id, seq);`)
  await db.exec(`CREATE INDEX IF NOT EXISTS idx_play_events_created ON play_events (created_at DESC);`)
}

export const getDb = async () => {
  if (!dbPromise) {
    ensureDataDir()
    dbPromise = open({
      filename: dbFile,
      driver: sqlite3.Database
    }).then(async (db) => {
      await runMigrations(db)
      return db
    })
  }
  return dbPromise
}

export const applyLocalMigration = async () => {
  const db = await getDb()
  await runMigrations(db)
}

export const clearAndSeedDemo = async () => {
  const db = await getDb()
  await db.exec('DELETE FROM storyworlds')
  await db.exec(`
    INSERT INTO storyworlds (
      id,
      title,
      description,
      num_characters,
      num_themes,
      num_variables,
      encounter_length,
      custom_prompt,
      encounter,
      system_prompt,
      is_public,
      genre,
      size_tag,
      theme_variant,
      cover_image,
      banner_image,
      tags,
      views,
      likes,
      fork_count,
      model_used,
      temperature
    ) VALUES
    (
      'seed-1',
      'The Ninth Embassy',
      'A summit city where every promise can become a weapon.',
      4, 3, 8, 640,
      'Diplomatic suspense and faction pressure.',
      '{"encounter":"War-room lights dim as five ambassadors receive a leaked treaty. The room wants signatures in ten minutes, but each clause can destabilize an ally.","choices":["Delay for verification","Push immediate ratification","Privately amend clause seven"]}',
      'You are a strategic diplomacy narrator.',
      1,
      'Diplomacy',
      'standard',
      'midnight',
      'https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?auto=format&fit=crop&w=1100&q=80',
      'https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?auto=format&fit=crop&w=1800&q=80',
      '["diplomacy","council","high-stakes"]',
      1760, 121, 7,
      'gpt-4.1',
      0.8
    ),
    (
      'seed-2',
      'Riftline Charter',
      'Space-lane arbitration between collapsing stations.',
      5, 3, 7, 720,
      'System-level sci-fi governance.',
      '{"encounter":"Orbital station councils deadlock while life-support tariffs spike. The charter hearing can prevent a system-wide shutdown or lock in corporate control.","choices":["Suspend tariffs","Nationalize life-support","Broker rotating governance"]}',
      'You are a space opera political storyteller.',
      1,
      'Sci-Fi',
      'standard',
      'ivory',
      'https://images.unsplash.com/photo-1516414447565-b14be0adf13e?auto=format&fit=crop&w=1100&q=80',
      'https://images.unsplash.com/photo-1516414447565-b14be0adf13e?auto=format&fit=crop&w=1800&q=80',
      '["space","treaty","resource-economy"]',
      932, 78, 4,
      'gpt-4.1',
      0.8
    );
  `)
}
