#!/usr/bin/env bash
{ set +x; } 2>/dev/null

( set -x; find ~/Library/LaunchAgents -name "*.py.plist" | xargs launchctl load -w )
