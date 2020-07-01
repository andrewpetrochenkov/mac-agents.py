#!/usr/bin/env
import mac_agents
import os
import shutil


src = os.path.join(os.path.dirname(__file__), "run.py")
dst = "/tmp/run.py"
shutil.copy(src, dst)
path = mac_agents.create(dst)
print(open(path).read())
