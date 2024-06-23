#!/usr/bin/env python3

import platform
import subprocess
import sys
from os.path import join

class PatchOps:
    def __init__(self):
        pass

    def list_dynamic_libs(self):
        raise NotImplementedError()

    def list_rpaths(self):
        raise NotImplementedError()

    def add_rpath(self, rpath):
        raise NotImplementedError()

    def remove_rpath(self, rpath):
        raise NotImplementedError()
#
#
#
class DarwinPatcher(PatchOps):

    def __init__(self, path):
        self._path = path
        self._loadcmds = None

    def _parseobj(self):
        if self._loadcmds is not None:
            return self._loadcmds

        res = subprocess.run(['/usr/bin/otool', '-l', self._path], capture_output=True, text=True)

        lines = res.stdout.splitlines()
        lines.pop(0)

        currcmd = [lines.pop(0)]
        loadcmds = []
        while lines != []:
            line = lines.pop(0)
            if line.startswith('Load command '):
                loadcmds.append(currcmd)
                currcmd = []
            currcmd.append(line)
        if currcmd != []:
            loadcmds.append(currcmd)

        self._loadcmds = loadcmds
        #import pprint; pprint.pprint(self._loadcmds)
        return self._loadcmds

    def _parse_lc_load_lib(self, loadcmd):
        if loadcmd[1].strip() == 'cmd LC_LOAD_DYLIB':
            return loadcmd[3].strip().split()[1]
        return None

    def _parse_lc_rpath(self, loadcmd):
        if loadcmd[1].strip() == 'cmd LC_RPATH':
            return loadcmd[3].strip().split()[1]
        return None

    def list_dynamic_libs(self):
        loadcmds = self._parseobj()
        libs = []
        for currcmd in loadcmds:
            lib = self._parse_lc_load_lib(currcmd)
            if lib is not None:
                libs.append(lib)
        return libs

    def list_rpaths(self):
        loadcmds = self._parseobj()
        rpaths = []
        for currcmd in loadcmds:
            rpath = self._parse_lc_rpath(currcmd)
            if rpath is not None:
                rpaths.append(rpath)
        return rpaths

    def add_rpath(self, rpath):
        res = subprocess.run(['/usr/bin/install_name_tool', '-add_rpath', rpath, self._path], capture_output=True, text=True)
        res.check_returncode()

    def remove_rpath(self, rpath):
        res = subprocess.run(['/usr/bin/install_name_tool', '-delete_rpath', rpath, self._path], capture_output=True, text=True)
        res.check_returncode()


def make_patcher(shared_library_path):
    """
    Constructs an instance of PatchOps for the specified shared_library_path.
    """

    system = platform.system()

    if system == 'Darwin':
        return DarwinPatcher(shared_library_path)
    if system == 'Linux':
        raise NotImplementedError()

    raise RuntimeError("unknown platform " + system)
