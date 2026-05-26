#!/usr/bin/env bash
set -euo pipefail

pdm run migrate
pdm run exercises
