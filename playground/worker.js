// Runs programs for the playground in playground/index.html. peye itself runs
// here, in Pyodide, off the page's main thread, so a long search cannot freeze
// the editor, and stopping a run is a matter of terminating this worker.
// Starting Python takes a few seconds, so one worker serves run after run.
// Pyodide 0.27 runs Python 3.12. From 0.28 on, Python 3.13 frees a long
// chain of objects, such as a deep search's frames, recursively, and in a
// browser that overflows the stack before code is optimized: a first run of
// deep-taxonomy-10000 fails there.
const PYODIDE = 'https://cdn.jsdelivr.net/pyodide/v0.27.7/full/';
const MODULES = ['__init__', 'arith', 'builtins', 'cli', 'common', 'dsl', 'engine', 'functions',
  'program', 'proof', 'reader', 'terms', 'writer'];

importScripts(`${PYODIDE}pyodide.js`);

async function fetchText(url) {
  const response = await fetch(url, { cache: 'no-store' });
  if (!response.ok) throw new Error(`${url}: ${response.status} ${response.statusText}`);
  return response.text();
}

const ready = (async () => {
  const pyodide = await loadPyodide({ indexURL: PYODIDE });
  pyodide.FS.mkdirTree('/peye/peye');
  const base = new URL('../peye/', self.location.href);
  await Promise.all(MODULES.map(async (name) => {
    pyodide.FS.writeFile(`/peye/peye/${name}.py`, await fetchText(new URL(`${name}.py`, base)));
  }));
  pyodide.FS.writeFile('/peye/runner.py', await fetchText(new URL('runner.py', self.location.href)));
  pyodide.runPython("import sys; sys.path.insert(0, '/peye'); import runner");
  return pyodide.globals.get('runner').playground_run;
})();

ready.then((playgroundRun) => {
  self.postMessage({ type: 'ready' });
  self.onmessage = ({ data }) => {
    const started = performance.now();
    try {
      const result = JSON.parse(playgroundRun(JSON.stringify(data)));
      self.postMessage({ ...result, milliseconds: performance.now() - started });
    } catch (error) {
      self.postMessage({ ok: false, error: error?.message ?? String(error), milliseconds: performance.now() - started });
    }
  };
}, (error) => self.postMessage({ type: 'failed', error: error?.message ?? String(error) }));
