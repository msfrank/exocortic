#!/usr/bin/env python3

import typing

import os.path
import platform
import subprocess

from pathlib import Path

class PatchOps:

    def list_dynamic_libs(self) -> list[str]:
        raise NotImplementedError()

    def get_absolute_path_for_lib(self, lib: str, exe: typing.Union[str,None]) -> str:
        raise NotImplementedError()

    def list_rpaths(self) -> list[str]:
        raise NotImplementedError()

    def add_rpath(self, rpath: str):
        raise NotImplementedError()

    def remove_rpath(self, rpath: str):
        raise NotImplementedError()

    def set_rpath(self, rpath: str):
        raise NotImplementedError()


class DarwinPatcher(PatchOps):
    """
    """

    def __init__(self, path: Path):
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

    def is_executable(self) -> bool:
        loadcmds = self._parseobj()
        for currcmd in loadcmds:
            if currcmd[1].strip() == 'cmd LC_MAIN':
                return True
        return False

    def list_dynamic_libs(self) -> list[str]:
        loadcmds = self._parseobj()
        libs = []
        for currcmd in loadcmds:
            lib = self._parse_lc_load_lib(currcmd)
            if lib is not None:
                libs.append(lib)
        return libs

    def _resolve_rpath(self, rpath: str, exe: typing.Union[str,None]) -> str:
        if os.path.isabs(rpath):
            return rpath
        parts = Path(rpath).parts
        if parts[0] == '@executable_path':
            if exe is None:
                raise Exception(f"failed to resolve rpath {rpath}: tried to resolve @executable_path but no exe specified")
            executable_path = os.path.dirname(exe)
            full_path = os.path.join(executable_path, *parts[1:])
            if not os.path.isdir(full_path):
                raise Exception(f"failed to resolve rpath {rpath}: directory {full_path} is missing")
            return full_path
        elif parts[0] == '@loader_path':
            loader_path = os.path.dirname(self._path)
            full_path = os.path.join(loader_path, *parts[1:])
            if not os.path.isdir(full_path):
                raise Exception(f"failed to resolve rpath {rpath}: directory {full_path} is missing")
            return full_path
        else:
            raise Exception(f"failed to resolve rpath {rpath} (loader: {self._path}, exe: {exe}")

    def get_absolute_path_for_lib(self, lib: str, exe: typing.Union[str,None]) -> str:
        if os.path.isabs(lib):
            return lib
        parts = Path(lib).parts
        if parts[0] == '@executable_path':
            if exe is None:
                raise Exception(f"failed to determine path for {lib}: tried to resolve @executable_path but no exe specified")
            executable_path = os.path.dirname(exe)
            full_path = os.path.join(executable_path, *parts[1:])
            if not os.path.isfile(full_path):
                raise Exception(f"failed to determine path for {lib}: no library found at @executable_path")
            return full_path
        elif parts[0] == '@loader_path':
            loader_path = os.path.dirname(self._path)
            full_path = os.path.join(loader_path, *parts[1:])
            if not os.path.isfile(full_path):
                raise Exception(f"failed to determine path for {lib}: no library found at @loader_path")
            return full_path
        elif parts[0] == '@rpath':
            for rpath in self.list_rpaths():
                resolved_rpath = self._resolve_rpath(rpath, exe)
                full_path = os.path.join(resolved_rpath, *parts[1:])
                if os.path.isfile(full_path):
                    return full_path
            raise Exception(f"failed to determine path for {lib}: no library found in any @rpath")
        else:
            raise Exception(f"failed to determine path for {lib}")

    def list_rpaths(self) -> list[str]:
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

    def set_rpath(self, rpath):
        for curr in self.list_rpaths():
            self.remove_rpath(curr)
        self.add_rpath(rpath)


def make_patcher(shared_library_path: Path) -> PatchOps:
    """
    Constructs an instance of PatchOps for the specified shared_library_path.
    """

    system = platform.system()

    if system == 'Darwin':
        return DarwinPatcher(shared_library_path)
    if system == 'Linux':
        raise NotImplementedError()

    raise RuntimeError("unknown platform " + system)
