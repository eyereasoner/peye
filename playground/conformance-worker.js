// Runs the conformance suite for playground/conformance.html: the suite's
// own runner, conformance/run.py, runs each case against peye in Pyodide,
// one case per message, so the page can show progress as it goes.
importScripts('peye-python.js');

const ready = startPeye({
  '/peye/conformance/run.py': '../conformance/run.py',
  '/peye/conformance_runner.py': 'conformance_runner.py',
}).then((pyodide) => {
  pyodide.runPython('import conformance_runner');
  return pyodide.globals.get('conformance_runner');
});

ready.then((runner) => {
  self.postMessage({ type: 'ready' });
  self.onmessage = ({ data }) => {
    try {
      if (data.type === 'load') {
        self.postMessage({ type: 'loaded', ...JSON.parse(runner.load(JSON.stringify(data.files))) });
      } else if (data.type === 'run') {
        self.postMessage({ type: 'result', index: data.index, ...JSON.parse(runner.run(data.index)) });
      }
    } catch (error) {
      self.postMessage({ type: 'failed', error: error?.message ?? String(error) });
    }
  };
}, (error) => self.postMessage({ type: 'failed', error: error?.message ?? String(error) }));
