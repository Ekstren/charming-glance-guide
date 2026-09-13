import { runOptimizer } from './assets/runtime.js';
const cfg = { cfg: 'test' };
const projected = { level: 120, score: 2000 };
const target = { targetStars: 800 };
async function main() {
  const result = await runOptimizer(cfg, projected, target);
  console.log(result);
}
main().catch(console.error);