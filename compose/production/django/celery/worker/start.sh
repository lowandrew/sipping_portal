#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset


celery -A sipping_portal.taskapp worker -l INFO
