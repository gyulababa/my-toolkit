<!-- helpers/vision/drivers/README.md -->
# helpers/vision/drivers

## Purpose
Capture sources ("drivers") for the vision pipeline. Each driver implements `FrameSource` and returns `Frame` objects.

Drivers are intentionally:
- UI-agnostic
- minimal
- optional-dependency friendly (import inside driver)

## Belongs here
- FrameSource implementations (screen capture, cameras, etc.)
- A registry/factory for config-driven instantiation

## Does not belong here
- Transform pipelines (see `helpers/vision/transforms`)
- GUI preview windows
- Persistence (saving frames)

## Public API (flat list)
### Sources
- `ScreenMssSource` (driver name: `"screen_mss"`)
- `UvcOpenCvSource` (driver name: `"uvc_opencv"`)

### Registry
- `make_source(driver: str, params: dict|None) -> FrameSource`
- `list_driver_names() -> list[str]`
