import os
import tempfile
import subprocess

def run(data, cmd):
    tmp = tempfile.NamedTemporaryFile()
    tmp.write(data)
    tmp.flush()
    os.fsync(tmp.fileno())

    popenargs = cmd.replace("%filename", tmp.name).split(" ")
    try:
        subprocess.check_call(popenargs, stderr=subprocess.STDOUT)
        data = open(tmp.name, "rb").read()
    finally:
        tmp.close()

    return data

def mkdir(dirname):
    if not os.path.exists(dirname):
        try:
            os.makedirs(dirname)
        except OSError:
            return False

    if not os.access(dirname, os.W_OK):
        return False
    return True

