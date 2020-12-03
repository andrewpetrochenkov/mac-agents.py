<!--
https://readme42.com
-->


[![](https://img.shields.io/pypi/v/mac-agents.svg?maxAge=3600)](https://pypi.org/project/mac-agents/)
[![](https://img.shields.io/badge/License-Unlicense-blue.svg?longCache=True)](https://unlicense.org/)
[![](https://github.com/andrewp-as-is/mac-agents.py/workflows/tests42/badge.svg)](https://github.com/andrewp-as-is/mac-agents.py/actions)

### Installation
```bash
$ [sudo] pip install mac-agents
```

#### Examples
`~/Library/LaunchAgents/file.py`
```python
import mac_agents

class Agent(mac_agents.Agent):
    StartInterval = 5  # capital letter

    def run(self):
        pass

if __name__ == "__main__":
    Agent().run()
```

```bash
$ find ~/Library/LaunchAgents -name "*.py" | xargs python -m mac_agents.create "$@"
$ find ~/Library/LaunchAgents -name "*.plist" | xargs launchctl load # or launchctl unload
$ launchctl list | grep .py$ | awk '{print $3}' | xargs -I '{}' launchctl remove {}
$ find ~/Library/LaunchAgents -name "*.py.plist" -exec rm {} +
```

#### Links
+   [launchd.plist](https://www.real-world-systems.com/docs/launchd.plist.5.html)

<p align="center">
    <a href="https://readme42.com/">readme42.com</a>
</p>
