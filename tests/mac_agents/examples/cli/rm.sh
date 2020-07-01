#!/usr/bin/env bash
{ set +x; } 2>/dev/null

( set -x; find ~/Library/LaunchAgents -type f -name "*.py.plist" -exec rm {} + )
