# Framework Agent Rules

This repository implements a local test-orchestration framework. These rules apply to every agent working in it.

## Safety

- Never apply a generated repair patch unless the controlling Multica Issue contains an explicit human `accept` comment.
- Do not connect to production systems, use production credentials, or run destructive database commands.
- Keep repair proposals as minimal unified diffs and record their confidence, target agent, and affected files.
- Do not create commits, push branches, or open pull requests unless the Issue explicitly requests it.

## Validation

- Preserve the test-case dependency graph when changing the loop controller.
- Run `python -m unittest discover -s tests -v` after changing Python source or tests.
- Keep external integrations behind the protocols in `src/auto_test_healer/contracts.py`.

## Collaboration

- Use the Multica Issue comments as the source of truth for evidence, delegation, approval, and final report links.
- A squad leader routes work and evaluates results; it does not implement the repair itself.
