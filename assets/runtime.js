// Season 2 optimizer runtime

// ------------ Constants (S2 specific) ------------
const S2_START_LEVEL = 106;           // first level to use in S2 planning
const S2_SCORE_FLOOR = 130;          // score floor for season‑power
const S2_RELIC_FLOOR = 13;           // relic level floor for S2

// ------------ Cache (in‑memory) ------------
// Simple LRU‑like cache for optimizer results keyed by JSON string of state
const optimizerCache = new Map();
const MAX_CACHE_ENTRIES = 100;

function cacheKey(cfg, projected, target) {
  // use JSON string; order of keys must be deterministic
  const keyObj = { cfg, projected, target };
  return JSON.stringify(keyObj);
}

function addToCache(key, result) {
  if (optimizerCache.size >= MAX_CACHE_ENTRIES) {
    // evict first entry
    const firstKey = optimizerCache.keys().next().value;
    optimizerCache.delete(firstKey);
  }
  optimizerCache.set(key, result);
}

// ------------ Optimizer entry point ------------
// In the real implementation this would perform heavy combinatorics
export async function runOptimizer(cfg, projected, target) {
  const key = cacheKey(cfg, projected, target);
  if (optimizerCache.has(key)) {
    console.log('Returning cached optimizer result for', key);
    return optimizerCache.get(key);
  }

  // Dummy implementation – replace with real algorithm
  // Simulate heavy async work with a timeout
  await new Promise(r => setTimeout(r, 200));
  const result = {
    best: {},
    targetStars: target.targetStars,
    // Example of additional data
    projectedLevel: projected.level,
    projectedScore: projected.score
  };

  addToCache(key, result);
  return result;
}

// ------------ Worker integration ------------
// Instantiate a single worker that forwards requests to runOptimizer
const optimizerWorker = new Worker('assets/optimizer.worker.js');

// Forward any messages from the worker to the main thread (e.g. progress)
optimizerWorker.onmessage = e => {
  // The worker posts messages like { type: 'result', data: ... }
  // Forward them to a global handler if needed
  if (typeof window.onOptimizerMessage === 'function') {
    window.onOptimizerMessage(e.data);
  }
};

console.log('Season 2 optimizer runtime initialized');
