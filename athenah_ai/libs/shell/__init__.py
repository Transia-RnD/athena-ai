#!/usr/bin/env python
# coding: utf-8

import logging
import os
from typing import List
from subprocess import PIPE, run, Popen

logger = logging.getLogger("app")


class ShellClient(object):
    tag: str = ""

    def __init__(self) -> None:
        pass

    # command = ["docker", "cp"]
    def run_with_args(
        self, path: str, command: List[str], args: List[str] = []
    ) -> bool:
        command.extend(args)
        # return self.do_run(command)
        return self.do_run(path, command)

    def do_run(self, path: str, command: List[str]) -> bool:
        try:
            debugcommand = " - {0}".format(" ".join(command))
            print(debugcommand)
            os.makedirs(path, exist_ok=True)
            os.chdir(path)
            return run(
                command, shell=True, stdout=PIPE, stderr=PIPE, universal_newlines=True
            )
        except Exception as e:
            logger.error(f"Error happened {e}")
            raise e

    def do_subprocess(self, command: List[str]) -> bool:
        try:
            debugcommand = " - {0}".format(" ".join(command))
            print(debugcommand)
            p = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
            stdout, stderr = p.communicate()
            print(f"STD RESPONSE: {p.returncode}")
            print(f"STD OUT: {stdout}")
            print(f"STD ERR: {stderr}")

            if stderr != "":
                raise ValueError(stderr)

            return True
        except Exception as e:
            logger.error(f"Error happened {e}")
            return False
