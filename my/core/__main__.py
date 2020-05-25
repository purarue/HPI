import os
from pathlib import Path
import sys
from subprocess import check_call, run, PIPE
import importlib
import traceback

from . import LazyLogger

log = LazyLogger('HPI cli')

class Modes:
    CONFIG  = 'config'
    DOCTOR  = 'doctor'
    MODULES = 'modules'


def run_mypy(pkg):
    from .init import get_mycfg_dir
    mycfg_dir = get_mycfg_dir()
    # todo ugh. not sure how to extract it from pkg?

    # todo dunno maybe use the same mypy config in repository?
    # I'd need to install mypy.ini then??
    env = {**os.environ}
    mpath = env.get('MYPYPATH')
    mpath = str(mycfg_dir) + ('' if mpath is None else f':{mpath}')
    env['MYPYPATH'] = mpath

    mres = run([
        'python3', '-m', 'mypy',
        '--namespace-packages',
        '--color-output', # not sure if works??
        '--pretty',
        '--show-error-codes',
        '--show-error-context',
        '--check-untyped-defs',
        '-p', pkg.__name__,
    ], stderr=PIPE, stdout=PIPE, env=env)
    return mres


def eprint(x: str):
    print(x, file=sys.stderr)

def indent(x: str) -> str:
    return ''.join('   ' + l for l in x.splitlines(keepends=True))

def info(x: str):
    eprint('✅ ' + x)

def error(x: str):
    eprint('❌ ' + x)

def warning(x: str):
    eprint('❗ ' + x) # todo yellow?

def tb(e):
    tb = ''.join(traceback.format_exception(Exception, e, e.__traceback__))
    sys.stderr.write(indent(tb))


class color:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'


def config_check(args):
    try:
        import my.config as cfg
    except Exception as e:
        error("failed to import the config")
        tb(e)
        sys.exit(1)

    info(f"config file: {cfg.__file__}")

    try:
        import mypy
    except ImportError:
        warning("mypy not found, can't check config with it")
    else:
        mres = run_mypy(cfg)
        rc = mres.returncode
        if rc == 0:
            info('mypy check: success')
        else:
            error('mypy check: failed')
            sys.stderr.write(indent(mres.stderr.decode('utf8')))
        sys.stderr.write(indent(mres.stdout.decode('utf8')))


def modules_check(args):
    verbose = args.verbose

    from .util import get_modules
    for m in get_modules():
        try:
            importlib.import_module(m)
        except Exception as e:
            # todo more specific command?
            vw = '' if verbose else '; pass --verbose to print more information'
            warning(f'{color.RED}FAIL{color.RESET}: {m:<30} loading failed{vw}')
            if verbose:
                tb(e)

        else:
            info(f'{color.GREEN}OK{color.RESET}  : {m:<30}')


def list_modules(args):
    # todo with docs/etc?
    from .util import get_modules
    for m in get_modules():
        print(f'- {m}')


# todo check that it finds private modules too?
def doctor(args):
    config_check(args)
    modules_check(args)


def parser():
    from argparse import ArgumentParser
    p = ArgumentParser('Human Programming Interface', epilog='''
Tool for HPI.

Work in progress, will be used for config management, troubleshooting & introspection
''')
    sp = p.add_subparsers(dest='mode')
    dp = sp.add_parser(Modes.DOCTOR, help='Run various checks')
    dp.add_argument('--verbose', action='store_true', help='Print more diagnosic infomration')
    dp.set_defaults(func=doctor)

    cp = sp.add_parser(Modes.CONFIG, help='Work with configuration')
    scp = cp.add_subparsers(dest='mode')
    # if True:
    #     ccp = scp.add_parser('check', help='Check config')
    #     ccp.set_defaults(func=config_check)

    mp = sp.add_parser(Modes.MODULES, help='List available modules')
    mp.set_defaults(func=list_modules)

    return p


def main():
    p = parser()
    args = p.parse_args()

    func = args.func
    if func is None:
        # shouldn't happen.. but just in case
        p.print_usage()
        sys.exit(1)

    import tempfile
    with tempfile.TemporaryDirectory() as td:
        # cd into tmp dir to prevent accidental imports..
        os.chdir(str(td))
        args.func(args)


if __name__ == '__main__':
    main()
