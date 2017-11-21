#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset
set -o xtrace


celery -A sipping_portal.taskapp worker -l INFO
