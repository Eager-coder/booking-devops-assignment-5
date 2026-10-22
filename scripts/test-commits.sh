#!/bin/sh
# Polling can group pushes: validate every new commit, not only the newest one.
set -eu
if [ -n "${GIT_PREVIOUS_SUCCESSFUL_COMMIT:-}" ] && git cat-file -e "$GIT_PREVIOUS_SUCCESSFUL_COMMIT" 2>/dev/null; then
    commits=$(git rev-list --reverse "$GIT_PREVIOUS_SUCCESSFUL_COMMIT..$GIT_COMMIT")
else
    commits=$GIT_COMMIT
fi
[ -n "$commits" ] || commits=$GIT_COMMIT
for commit in $commits; do
    echo "Testing commit $commit"
    runner=$(docker create -w /work "$PYTHON_IMAGE" python -m unittest discover -s tests -v)
    trap 'docker rm -f "$runner" >/dev/null 2>&1 || true' EXIT HUP INT TERM
    git archive "$commit" | docker cp - "$runner:/work"
    docker start -a "$runner"
    code=$(docker inspect -f '{{.State.ExitCode}}' "$runner")
    docker rm "$runner" >/dev/null
    trap - EXIT HUP INT TERM
    [ "$code" = 0 ] || exit "$code"
done
