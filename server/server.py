import sys
import os
import threading
import subprocess
import time

from optparse import OptionParser

server_process = None
pid = None


class Checker(threading.Thread):

    def __init__(self, delta):
        threading.Thread.__init__(self)
        self.delta = delta
        self.die = False

    def run(self):
        while not self.die:
            self._check()
            time.sleep(self.delta)
        server_process.terminate()

    def _check(self):
        try:
            global pid
            os.kill(int(pid), 0)
        except OSError:
            self.die = True

if __name__ == '__main__':
    opt_parser = OptionParser(usage=(
        'usage: %prog <sublime_pid> <port> <solution_file> '
    ))

    options, args = opt_parser.parse_args()
    if len(args) != 3:
        opt_parser.error('please pass all arguments')

    pid = args[0]
    port = args[1]
    solution_file = args[2]

    mono_dir_candidate_paths = os.environ['PATH'].split(':')
    mono_dir_candidate_paths += [
        '/usr/local/bin',
        '/opt/usr/local/bin',
        '/opt/usr/bin',
    ]
    mono_exe_candidate_paths = [os.path.join(mono_dir_path, 'mono') 
            for mono_dir_path in mono_dir_candidate_paths]
    mono_exe_paths = [mono_exe_candidate_path 
            for mono_exe_candidate_path in mono_exe_candidate_paths 
            if os.access(mono_exe_candidate_path, os.R_OK)]

    if not mono_exe_paths:
        sys.stderr.write('Check your mono executable path.\n')
        sys.stderr.write(repr(e) + '\n')
        sys.stderr.write(repr(os.environ))
        sys.exit(-1)

    mono_exe_path = mono_exe_paths[0]

    omnisharp_server_path = os.path.join(
        os.path.dirname(__file__),
        '../OmniSharpServer/OmniSharp/bin/Debug/OmniSharp.exe')
    args = [
        mono_exe_path, 
        omnisharp_server_path, 
        '-p', port,
        '-s', solution_file
    ]

    try:
        server_process = subprocess.Popen(args)
    except Exception as e:
        sys.stderr.write(
                'Check your solution file, OmniSharpServer'
                ' and mono environment.\n')
        sys.stderr.write(repr(e) + '\n')

        sys.exit(-1)

    checker = Checker(5)
    checker.start()

    server_process.wait()
