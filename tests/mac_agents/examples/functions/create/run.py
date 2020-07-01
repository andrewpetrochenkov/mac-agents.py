#!/usr/bin/env python
import mac_agents


class Agent(mac_agents.Agent):
    RunAtLoad = True

    def run(self):
        pass


if __name__ == "__main__":
    Agent().create()
