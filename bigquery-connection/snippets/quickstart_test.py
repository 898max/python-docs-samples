# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest

from . import quickstart


@pytest.mark.parametrize("transport", ["grpc", "rest"])
def test_quickstart(
    capsys: pytest.CaptureFixture, project_id: str, location: str, transport: str
) -> None:
    quickstart.main(project_id, location, transport)
    out, _ = capsys.readouterr()
    assert "List of connections in project" in outname: Step 0, Welcome

# This step triggers after the learner creates a new repository from the template.
# This workflow updates from step 0 to step 1.

# This will run every time we create push a commit to `main`.
# Reference: https://docs.github.com/en/actions/learn-github-actions/events-that-trigger-workflows
on:
  workflow_dispatch:
  push:
    branches:
      - main

# Reference: https://docs.github.com/en/actions/security-guides/automatic-token-authentication
permissions:
  # Need `contents: read` to checkout the repository.
  # Need `contents: write` to update the step metadata.
  # Need `pull-requests: write` to create a pull request.
  contents: write
  pull-requests: write

jobs:
  # Get the current step to only run the main job when the learner is on the same step.
  get_current_step:
    name: Check current step number
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - id: get_step
        run: |
          echo "current_step=$(cat ./.github/steps/-step.txt)" >> $GITHUB_OUTPUT
    outputs:
      current_step: ${{ steps.get_step.outputs.current_step }}

  on_start:
    name: On start
    needs: get_current_step

    # We will only run this action when:
    # 1. This repository isn't the template repository.
    # 2. The step is currently 0.
    # Reference: https://docs.github.com/en/actions/learn-github-actions/contexts
    # Reference: https://docs.github.com/en/actions/learn-github-actions/expressions
    if: >-
      ${{ !github.event.repository.is_template
          && needs.get_current_step.outputs.current_step == 0 }}

    # We'll run Ubuntu for performance instead of Mac or Windows.
    runs-on: ubuntu-latest

    steps:
      # We'll need to check out the repository so that we can edit the README.
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0 # Let's get all the branches.

      - name: Create my-pages branch, initial Pages files, and pull request
        run: |
          echo "Make sure we are on step 0"
          if [ "$(cat .github/steps/-step.txt)" != 0 ]
          then
            echo "Current step is not 0"
            exit 0
          fi

          echo "Make a branch"
          BRANCH=my-pages
          git checkout -b $BRANCH

          echo "Create config and homepage files"
          touch _config.yml
          printf "%s\n%s\n%s\n\n" "---" "title: Welcome to my blog" "---" > index.md

          echo "Make a commit"
          git config user.name github-actions[bot]
          git config user.email github-actions[bot]@users.noreply.github.com
          git add _config.yml index.md
          git commit --message="Create config and homepages files"

          echo "Push"
          git push --set-upstream origin $BRANCH
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      # In README.md, switch step 0 for step 1.
      - name: Update to step 1
        uses: skills/action-update-step@v2
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          from_step: 0
          to_step: 1
          branch_name: my-pages
