"""The peye command line."""
import json
import sys
import threading

HELP = """Usage: peye [OPTION ...] [FILE ...]
Programs are Python; forward rules run to a fixpoint.
  --proof             Print the claims with clause(...) and step(...) records
  --check-proof FILE  Print a C1-C7 check report of a proof (- for stdin)
  --json              Print the check report as JSON instead
  --goal GOAL         Ask a backward goal after forward reasoning; with
                      --check-proof, the goal the proof answers
  --strict-proof      Reject proofs relying on absence or collection
  --unused            List the clauses that make no difference to the conclusions
  --stats             Print reasoning statistics to stderr
  --max-depth N       Bound backward recursion (default 1000000)
  --max-iterations N  Bound forward rounds per stratum (default 1000)
  --max-inferences N  Bound reasoning work (default 1000000)
  --version           Print the version
  --help              Print this help
Source defaults to stdin; multiple files form one program.
Exit codes: 0 success, 1 error, 2 invalid proof, 65 contradiction.
"""

LIMITS = {'--max-depth': 'max_depth', '--max-iterations': 'max_iterations',
          '--max-inferences': 'max_inferences'}


class UsageError(Exception):
    pass


def main(argv, sources=None, stdout=None, stderr=None):
    """Run the command line; returns the exit code.

    sources, when given, is the program already stated by a script run
    directly, and argv then names no program files.
    """
    from . import __version__
    from .engine import run, unused_clauses
    from .program import Program
    from .proof import check_proof, check_report, public_report
    from .terms import PeyeError
    from .dsl import load
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    try:
        files = []
        options = {}
        goals = []
        proof_file = None
        stats = strict = as_json = unused = False
        i = 0
        while i < len(argv):
            arg = argv[i]
            if arg in ('--help', '-h'):
                stdout.write(HELP)
                return 0
            if arg in ('--version', '-v'):
                stdout.write(f'peye v{__version__}\n')
                return 0
            if arg in ('--proof', '-p'):
                options['proof'] = True
            elif arg == '--stats':
                stats = True
            elif arg == '--strict-proof':
                strict = True
            elif arg == '--json':
                as_json = True
            elif arg == '--unused':
                unused = True
            elif arg in ('--check-proof', '--goal', *LIMITS):
                i += 1
                if i >= len(argv):
                    raise UsageError(f'{arg} needs a value')
                value = argv[i]
                if arg == '--check-proof':
                    proof_file = value
                elif arg == '--goal':
                    goals.append(value)
                else:
                    try:
                        number = int(value)
                    except ValueError:
                        number = 0
                    if number < 1:
                        raise UsageError(f'{arg} needs a positive integer')
                    options[LIMITS[arg]] = number
            elif arg.startswith('-') and arg != '-':
                raise UsageError(f'unknown option {arg}')
            else:
                files.append(arg)
            i += 1
        if as_json and proof_file is None:
            raise UsageError('--json requires --check-proof')
        if strict and proof_file is None:
            raise UsageError('--strict-proof requires --check-proof')
        if proof_file is not None and options.get('proof'):
            raise UsageError('--check-proof cannot be combined with --proof')
        if unused and (proof_file is not None or options.get('proof')):
            raise UsageError('--unused cannot be combined with --proof or --check-proof')
        if sources is not None:
            if files:
                raise UsageError('a program run as a script names no other program files')
            program = Program(sources)
        else:
            if proof_file == '-' and (not files or '-' in files):
                raise UsageError('stdin holds the proof; name the program as files')
            if not files:
                files.append('-')
            if files.count('-') > 1:
                raise UsageError('stdin can only be read once')
            program = load(files)
        if proof_file is not None:
            if proof_file == '-':
                document = sys.stdin.read()
            else:
                with open(proof_file, encoding='utf-8') as handle:
                    document = handle.read()
            report = check_proof(program, document, goals=goals, allow_trusted=not strict)
            stdout.write(json.dumps(public_report(report), indent=2) + '\n' if as_json else check_report(report))
            # An invalid proof is a result, not an error: it has its own exit code.
            return 0 if report['valid'] else 2
        if unused:
            stdout.write(unused_clauses(program, goals=goals, **options))
            return 0
        result = run(program, goals=goals, **options)
        stdout.write(result.stdout)
        if stats:
            stderr.write(json.dumps(result.stats) + '\n')
        return result.halt_code or 0
    except (UsageError, PeyeError, OSError) as error:
        stderr.write(f'peye: {error}\n')
        return 1
    except BrokenPipeError:
        return 0


def with_deep_stack(function, *args, **kwargs):
    """Call function in a thread with a deep stack: a few term walks recurse."""
    sys.setrecursionlimit(1_000_000)
    threading.stack_size(512 * 1024 * 1024)
    outcome = {}

    def target():
        try:
            outcome['value'] = function(*args, **kwargs)
        except BaseException as error:  # handed back to the calling thread
            outcome['error'] = error
    thread = threading.Thread(target=target)
    thread.start()
    thread.join()
    if 'error' in outcome:
        raise outcome['error']
    return outcome['value']


def entry():
    code = with_deep_stack(main, sys.argv[1:])
    try:
        sys.stdout.flush()
    except BrokenPipeError:
        pass
    sys.exit(code)
