#!/usr/bin/env node
/* eslint-disable no-console */
const fs = require("node:fs");
const path = require("node:path");
const { pathToFileURL } = require("node:url");

function parseArgs(argv) {
  const args = {
    storyworld: "",
    outRoot: "D:/storyworld-plays",
    readerHtml: "C:/projects/GPTStoryworld/storyworld_reader.html",
    puppetRoot: "C:/projects/PuppetMaster/PuppetMaster",
  };
  for (let i = 2; i < argv.length; i += 1) {
    const t = argv[i];
    if (t === "--storyworld") args.storyworld = argv[++i];
    else if (t === "--out-root") args.outRoot = argv[++i];
    else if (t === "--reader-html") args.readerHtml = argv[++i];
    else if (t === "--puppet-root") args.puppetRoot = argv[++i];
  }
  return args;
}

function nowTag() {
  return new Date().toISOString().replace(/[:.]/g, "-");
}

function safeName(p) {
  const base = path.basename(p, path.extname(p));
  return base.replace(/[^A-Za-z0-9._-]/g, "_");
}

async function main() {
  const args = parseArgs(process.argv);
  if (!args.storyworld) throw new Error("Missing --storyworld");
  const pwIndex = path.join(args.puppetRoot, "node_modules", "playwright", "index.js");
  if (!fs.existsSync(pwIndex)) throw new Error(`Playwright not found: ${pwIndex}`);
  const ns = await import(pathToFileURL(pwIndex).href);
  const chromium = (ns && ns.chromium) || (ns && ns.default && ns.default.chromium);
  if (!chromium) throw new Error("Unable to resolve Playwright chromium launcher.");

  const runDir = path.join(args.outRoot, `storyworld-reader-${safeName(args.storyworld)}-${nowTag()}`);
  fs.mkdirSync(runDir, { recursive: true });
  const consoleLogs = [];
  const pageErrors = [];

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1720, height: 1080 } });
  page.on("console", (msg) => consoleLogs.push(`[${msg.type()}] ${msg.text()}`));
  page.on("pageerror", (err) => pageErrors.push(String(err)));

  try {
    await page.goto(pathToFileURL(args.readerHtml).href, { waitUntil: "domcontentloaded" });
    await page.waitForSelector("#file-input", { state: "attached" });
    await page.locator("#file-input").setInputFiles(args.storyworld);
    await page.waitForSelector("#game-container.active", { timeout: 30000 });
    await page.waitForTimeout(900);

    await page.screenshot({ path: path.join(runDir, "01-reader-start.png"), fullPage: true });

    const optionCount = await page.locator(".option-btn").count();
    if (optionCount > 0) {
      await page.locator(".option-btn").first().click();
      await page.waitForTimeout(500);
      await page.screenshot({ path: path.join(runDir, "02-after-choice.png"), fullPage: true });
    }

    const continueCount = await page.locator(".continue-btn").count();
    if (continueCount > 0) {
      await page.locator(".continue-btn").first().click();
      await page.waitForTimeout(500);
      await page.screenshot({ path: path.join(runDir, "03-after-continue.png"), fullPage: true });
    }

    await page.locator("#stats-panel").screenshot({ path: path.join(runDir, "04-stats-panel.png") }).catch(() => {});
    await page.locator("#history-section").screenshot({ path: path.join(runDir, "05-history-panel.png") }).catch(() => {});
  } finally {
    await browser.close();
  }

  const manifest = {
    createdAt: new Date().toISOString(),
    storyworld: args.storyworld,
    readerHtml: args.readerHtml,
    screenshots: fs.readdirSync(runDir).filter((x) => x.endsWith(".png")).sort(),
    consoleLogCount: consoleLogs.length,
    pageErrorCount: pageErrors.length,
    consoleLogs: consoleLogs.slice(-200),
    pageErrors,
  };
  fs.writeFileSync(path.join(runDir, "manifest.json"), JSON.stringify(manifest, null, 2), "utf-8");
  console.log(runDir);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
