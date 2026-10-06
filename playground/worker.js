// Runs programs for the playground in playground/index.html. peye itself runs
// here, in Pyodide, off the page's main thread, so a long search cannot freeze
// the editor, and stopping a run is a matter of terminating this worker.
// Starting Python takes a few seconds, so one worker serves run after run.
importScripts('peye-python.js');

const ready = startPeye({ '/peye/runner.py': 'runner.py' }).then((pyodide) => {
  pyodide.runPython('import runner');
  return pyodide.globals.get('runner').playground_run;
});

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
