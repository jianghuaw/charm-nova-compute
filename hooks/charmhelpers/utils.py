# Copyright (C) 2017 Citrix System.

import subprocess


from charmhelpers.core.hookenv import (
    log,
    DEBUG,
    INFO,
    ERROR,
)


class ExecutionError(Exception):
    pass


class FatalException(Exception):
    pass


def reportError(err):
    log(err, level=ERROR)
    raise FatalException(err)


def detailed_execute(*cmd, **kwargs):
    cmd = map(str, cmd)
    _env = kwargs.get('env')
    env_prefix = ''
    if _env:
        env_prefix = ''.join(['%s=%s ' % (k, _env[k]) for k in _env])

        env = dict(os.environ)
        env.update(_env)
    else:
        env = None
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,  # nosec
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, env=env)

    prompt = kwargs.get('prompt')
    if prompt:
        (out, err) = proc.communicate(prompt)
    else:
        (out, err) = proc.communicate()

    if out:
        # Truncate "\n" if it is the last char
        out = out.strip()
        log(out, level=DEBUG)
    if err:
        log(err, level=INFO)

    if proc.returncode is not None and proc.returncode != 0:
        if proc.returncode in kwargs.get('allowed_return_codes', [0]):
            log('Swallowed acceptable return code of %d' % proc.returncode,
                level=INFO)
        else:
            raise ExecutionError(err)

    return proc.returncode, out, err


def execute(*cmd, **kwargs):
    _, out, _ = detailed_execute(*cmd, **kwargs)
    return out

