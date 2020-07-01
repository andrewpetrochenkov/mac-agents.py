#!/usr/bin/env bash
{ set +x; } 2>/dev/null

( set -x; launchctl list | grep .py$ );:
