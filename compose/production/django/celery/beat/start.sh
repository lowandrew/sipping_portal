#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset


celery -A sipping_portal.taskapp beat -l INFO
