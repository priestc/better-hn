#!/usr/bin/env python
# coding: utf-8

import argparse
import sys
from giotto import initialize

try:
    import secrets
except ImportError:
    secrets = None
    print("Warning: no secret.py found.")

try:
    import machine
except ImportError:
    machine = None
    print("Warning: no machine.py found.")

import config
initialize(config, secrets, machine)

from manifest import manifest

args = sys.argv
mock = '--model-mock' in args
if mock:
    # remove the mock argument so the controller doesn't get confused
    args.pop(args.index('--model-mock'))
from giotto.controllers.cmd import CMDController, CMDRequest
request = CMDRequest(sys.argv)
controller = CMDController(request=request, manifest=manifest, model_mock=mock)
controller.get_response()