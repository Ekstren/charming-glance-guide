// Optimizer worker for Season 2
importScripts('assets/runtime.js');

self.onmessage = function(e) {
  const { cfg, projected, target } = e.data;
  // call the async optimizer and post the result
  runOptimizer(cfg, projected, target)
    .then(result => {
      self.postMessage({ type: 'result', data: result });
    })
    .catch(err => {
      self.postMessage({ type: 'error', error: err.message || String(err) });
    });
};
