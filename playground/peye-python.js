// Starting peye in Pyodide, for the playground's workers: worker.js runs
// programs for index.html, conformance-worker.js the suite for
// conformance.html. Each loads this with importScripts and calls startPeye.
//
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

// Pyodide with the peye package importable, and extra files written to the
// paths given, as { '/path/in/python': 'url relative to this worker' }.
async function startPeye(extra = {}) {
  const pyodide = await loadPyodide({ indexURL: PYODIDE });
  pyodide.FS.mkdirTree('/peye/peye');
  const base = new URL('../peye/', self.location.href);
  await Promise.all(MODULES.map(async (name) => {
    pyodide.FS.writeFile(`/peye/peye/${name}.py`, await fetchText(new URL(`${name}.py`, base)));
  }));
  await Promise.all(Object.entries(extra).map(async ([path, url]) => {
    pyodide.FS.mkdirTree(path.slice(0, path.lastIndexOf('/')) || '/');
    pyodide.FS.writeFile(path, await fetchText(new URL(url, self.location.href)));
  }));
  pyodide.runPython("import sys; sys.path.insert(0, '/peye')");
  return pyodide;
}
