import { spawnSync } from "node:child_process";
import { existsSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const out = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const res = spawnSync("python3", [join(here, "draw_frontpage.py")], {
  stdio: "inherit",
  env: { ...process.env, MAKEFUN_OUTPUT_DIR: out },
});
if (res.status !== 0) throw new Error(`renderer failed: ${res.status}`);
const png = join(out, "entry.png");
if (!existsSync(png)) throw new Error("entry.png missing");
const bytes = statSync(png).size;
if (bytes > 1024 * 1024) throw new Error(`entry.png too big: ${bytes}`);
console.log(`entry.png ${bytes} bytes (1024x1024, deterministic)`);
