#!/usr/bin/env python
import mac_agents

for job in mac_agents.jobs():
    print("%s %s %s" % (job.pid, job.status, job.label))
