#!/usr/bin/env bash
set -u
[ -f ANSWER.txt ] || { echo "ANSWER.txt missing"; exit 1; }
# Read-only: only ANSWER.txt may be new/changed.
changed=$(git status --porcelain | grep -v 'ANSWER.txt' | grep -v '__pycache__' || true)
[ -z "$changed" ] || { echo "modified other files: $changed"; exit 1; }
grep -Eq '^max_retries:\s*4\s*$' ANSWER.txt || { echo "wrong max_retries"; exit 1; }
grep -Eq '^retry_on:\s*TransientError\s*$' ANSWER.txt || { echo "wrong retry_on"; exit 1; }
grep -Eq '^delay_before_retry_3:\s*6(\.0+)?\s*$' ANSWER.txt || { echo "wrong delay"; exit 1; }
