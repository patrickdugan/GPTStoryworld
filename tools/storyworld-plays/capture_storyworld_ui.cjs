#!/usr/bin/env node
/* eslint-disable no-console */
const fs = require("node:fs");
const path = require("node:path");
const { spawn, spawnSync } = require("node:child_process");
const { pathToFileURL } = require("node:url");

function parseArgs(argv) {
  const args = {
    sweepDir: "C:/projects/sweepweave-ts/sweepweave-ts",
    puppetRoot: "C:/projects/PuppetMaster/PuppetMaster",
    outRoot: "D:/storyworld-plays",
    port: 5173,
    files: [],
  };
  for (let i = 2; i < argv.length; i += 1) {
    const token = argv[i];
    if (token === "--sweep-dir") {
      args.sweepDir = argv[++i];
    } else if (token === "--puppet-root") {
      args.puppetRoot = argv[++i];
    } else if (token === "--out-root") {
      args.outRoot = argv[++i];
    } else if (token === "--port") {
      args.port = Number(argv[++i]);
    } else if (token === "--files") {
      i += 1;
      while (i < argv.length && !argv[i].startsWith("--")) {
        args.files.push(argv[i]);
        i += 1;
      }
      i -= 1;
    }
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

async function waitForServer(url, timeoutMs = 60000) {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    try {
      const res = await fetch(url);
      if (res.ok) return;
    } catch (err) {
      // Retry until timeout.
    }
    await new Promise((resolve) => setTimeout(resolve, 700));
  }
  throw new Error(`Timed out waiting for ${url}`);
}

function startVite(sweepDir, port) {
  const args = ["run", "dev", "--", "--host", "127.0.0.1", "--port", String(port)];
  if (process.platform === "win32") {
    return spawn("cmd.exe", ["/d", "/s", "/c", "npm", ...args], {
      cwd: sweepDir,
      shell: false,
      stdio: ["ignore", "pipe", "pipe"],
    });
  }
  return spawn("npm", args, {
    cwd: sweepDir,
    shell: false,
    stdio: ["ignore", "pipe", "pipe"],
  });
}

function killProcessTree(pid) {
  if (!pid) return;
  if (process.platform === "win32") {
    spawnSync("taskkill", ["/pid", String(pid), "/T", "/F"], { stdio: "ignore" });
  } else {
    process.kill(pid, "SIGTERM");
  }
}

async function loadStoryworld(page, baseUrl, filePath) {
  await page.goto(baseUrl, { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(500);
  const [chooser] = await Promise.all([
    page.waitForEvent("filechooser"),
    page.locator('button:has-text("File")').click(),
    page.locator('button:has-text("Load JSON")').click(),
  ]);
  await chooser.setFiles(filePath);
  await page.waitForTimeout(1300);
}

async function takeTabShot(page, tabLabel, shotPath) {
  await page.locator(`button:has-text("${tabLabel}")`).click();
  await page.waitForTimeout(350);
  await page.screenshot({ path: shotPath, fullPage: true });
}

async function main() {
  const args = parseArgs(process.argv);
  if (!args.files.length) {
    console.error("No storyworld files provided. Use --files <path1> <path2> ...");
    process.exit(2);
  }

  const pwIndex = path.join(args.puppetRoot, "node_modules", "playwright", "index.js");
  if (!fs.existsSync(pwIndex)) {
    console.error(`Playwright not found at ${pwIndex}`);
    process.exit(2);
  }
  const playwrightNs = await import(pathToFileURL(pwIndex).href);
  const chromium =
    (playwrightNs && playwrightNs.chromium) ||
    (playwrightNs && playwrightNs.default && playwrightNs.default.chromium);
  if (!chromium) {
    throw new Error("Unable to resolve Playwright chromium launcher.");
  }

  const sessionRoot = path.join(args.outRoot, `sweepweave-ui-${nowTag()}`);
  fs.mkdirSync(sessionRoot, { recursive: true });

  const baseUrl = `http://127.0.0.1:${args.port}/`;
  const vite = startVite(args.sweepDir, args.port);
  const viteLogs = [];
  vite.stdout.on("data", (buf) => viteLogs.push(String(buf)));
  vite.stderr.on("data", (buf) => viteLogs.push(String(buf)));

  const manifest = {
    createdAt: new Date().toISOString(),
    sweepDir: args.sweepDir,
    baseUrl,
    outRoot: sessionRoot,
    files: [],
  };

  try {
    await waitForServer(baseUrl);
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage({ viewport: { width: 1600, height: 1000 } });

    for (const filePath of args.files) {
      const worldName = safeName(filePath);
      const worldDir = path.join(sessionRoot, worldName);
      fs.mkdirSync(worldDir, { recursive: true });
      const item = {
        filePath,
        worldDir,
        screenshots: [],
      };
      try {
        await loadStoryworld(page, baseUrl, filePath);
        const shots = [
          ["Overview", "01-overview.png"],
          ["Encounters", "02-encounters.png"],
          ["Rehearsal", "03-rehearsal.png"],
          ["Notable Outcome Index", "04-notable-outcomes.png"],
        ];
        for (const [tab, name] of shots) {
          const shotPath = path.join(worldDir, name);
          await takeTabShot(page, tab, shotPath);
          item.screenshots.push(shotPath);
        }
      } catch (err) {
        item.error = String(err);
      }
      manifest.files.push(item);
    }

    await browser.close();
  } finally {
    manifest.viteLogTail = viteLogs.slice(-60);
    fs.writeFileSync(path.join(sessionRoot, "manifest.json"), JSON.stringify(manifest, null, 2), "utf-8");
    killProcessTree(vite.pid);
  }

  console.log(sessionRoot);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
