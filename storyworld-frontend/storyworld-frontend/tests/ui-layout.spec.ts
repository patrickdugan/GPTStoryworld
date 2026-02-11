import { expect, test } from '@playwright/test'
import fs from 'node:fs'

test('renders hero, carousel rows, and captures screenshot', async ({ page }) => {
  const visualAIToken = process.env.VISUAL_AI_TOKEN || 'TODO_SET_VISUAL_AI_TOKEN'

  fs.mkdirSync('tests/artifacts', { recursive: true })

  await page.setViewportSize({ width: 1440, height: 900 })
  await page.goto('/')
  await page.waitForLoadState('networkidle')

  const hero = page.locator('[data-testid="hero-banner"]')
  const rows = page.locator('[data-testid="carousel-row"]')
  const cards = page.locator('[data-testid="story-card"]')
  const genreTabs = page.locator('[data-testid="genre-tabs"]')
  const sizeTabs = page.locator('[data-testid="size-tabs"]')
  const readerPanel = page.locator('[data-testid="reader-panel"]')
  const readerTemplate = page.locator('[data-testid="reader-template"]')

  await expect(hero).toBeVisible()
  await expect(rows.first()).toBeVisible()
  await expect(genreTabs).toBeVisible()
  await expect(sizeTabs).toBeVisible()
  await expect(readerPanel).toBeVisible()
  await expect(readerTemplate).toBeVisible()
  expect(await cards.count()).toBeGreaterThanOrEqual(5)

  await page.screenshot({
    path: 'tests/artifacts/storyworld-home-desktop.png',
    fullPage: false
  })

  await page.setViewportSize({ width: 390, height: 844 })
  await page.goto('/')
  await page.waitForLoadState('networkidle')

  await expect(hero).toBeVisible()
  await expect(rows.first()).toBeVisible()
  await page.screenshot({
    path: 'tests/artifacts/storyworld-home-mobile.png',
    fullPage: false
  })

  // TODO: Forward this token to PuppetMaster vision loop once integrated.
  console.log(`visualAIToken=${visualAIToken}`)
})
