#!/usr/bin/env python3
# coding: utf-8

__all__ = ["parse_message_webcast"]

from pathlib import Path
from platform import system
from subprocess import run

IS_WIN = system() == "Windows"
curdir = Path(__file__).parent
proto_file = curdir / "douyin.proto"
proto_pyfile = curdir / "douyin_pb2.py"

if not proto_pyfile.exists() or \
        proto_file.stat().st_mtime >= proto_pyfile.stat().st_mtime:
    run(["protoc", "-I", curdir, "--python_out", curdir, "douyin.proto"], shell=IS_WIN)

