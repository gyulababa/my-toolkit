<!-- helpers/threading/README.md -->
# helpers/threading

## Purpose
Small runtime/threading helpers used by background loops across projects:
- rate limiting (FPS/Hz pacing)

## Belongs here
- simple timing primitives (monotonic clocks, pacing)
- lightweight loop helpers that are UI-agnostic and dependency-free

## Does not belong here
- thread pools / executors / async frameworks
- IPC, queues beyond stdlib
- application-specific scheduling logic

## Public API (flat list)
- `RateLimiter`
  - `sleep_if_needed()`
  - `tick()`
  - `reset()`
