"""The playground's side of peye: run one request and describe the outcome."""
import json
import re
import sys
import traceback

from peye import PeyeError, __version__, check_proof, check_report, load_text, run
from peye.proof import strict

sys.setrecursionlimit(5000)
PROGRAM = '<program>'


def _line(error):
    """The editor line an error points at, when it points at one."""
    if isinstance(error, SyntaxError) and error.filename == PROGRAM:
        return error.lineno
    for frame in reversed(traceback.extract_tb(error.__traceback__)):
        if frame.filename == PROGRAM:
            return frame.lineno
    match = re.match(r'line (\d+):', str(error))
    return int(match.group(1)) if match else None


# The last program loaded, by its source text. Running the same program
# again with another goal or other options then skips loading it, which for
# a large program is much of the work. A Program keeps no state between runs.
_last = {'source': None, 'program': None}


def _program(source):
    if _last['source'] != source:
        # Forget the old program first, so a failed load leaves nothing cached.
        _last['source'] = _last['program'] = None
        _last['program'] = load_text(source, PROGRAM)
        _last['source'] = source
    return _last['program']


def playground_run(request):
    request = json.loads(request)
    try:
        program = _program(request['source'])
        goals = [request['goal']] if request.get('goal') else []
        limits = {name: value for name, value in request.get('limits', {}).items() if value}
        # Checking needs a certificate even when the proof itself is not shown.
        result = run(program, goals=goals, proof=bool(request.get('proof') or request.get('check')), **limits)
        report = None
        if request.get('check') and result.answers:
            # A generated proof is already checked once; a strict check is a
            # different question, so it gets its own run of the checker.
            verdict = result.proof_report
            if request.get('strict'):
                verdict = strict(verdict) or check_proof(program, result.proof, goals=goals, allow_trusted=False)
            report = {'text': check_report(verdict), 'valid': verdict['valid'], 'trusted': len(verdict['trusted'])}
        answers = ''.join(f'{answer}\n' for answer in result.answers)
        return json.dumps({
            'ok': True, 'output': result.proof if request.get('proof') else answers,
            'answers': len(result.answers), 'report': report, 'stats': result.stats,
            'haltCode': result.halt_code, 'version': __version__,
        })
    except Exception as error:  # every failure is reported to the page
        message = str(error) if isinstance(error, PeyeError) else f'{type(error).__name__}: {error}'
        return json.dumps({'ok': False, 'error': message, 'line': _line(error)})
