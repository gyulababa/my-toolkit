# services/vision/preview_session.py
# Config-driven capture preview session: builds FrameSource from VisionConfig, runs SourceRunner, exposes latest RGB frames.

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional

import numpy as np

from helpers.validation import ValidationError
from helpers.vision.buffer import LatestFrameBuffer
from helpers.vision.runner import SourceRunner

from helpers.vision.transforms.colors import ensure_rgb8
from helpers.vision.transforms.crop import crop_rect_norm
from helpers.vision.transforms.resize import resize_max

@dataclass
class PreviewStats:
    """Snapshot of runtime stats for UI display."""
    frames_in: int = 0
    frames_out: int = 0
    last_error: Optional[str] = None
    fps_smooth: float = 0.0


class VisionPreviewSession:
    """
    VisionPreviewSession

    Owns:
      - config path
      - FrameSource built from config
      - LatestFrameBuffer
      - SourceRunner (config-driven transforms)
      - pause/running flags
      - fps smoothing state
    """

    def __init__(
        self,
        *,
        config_path: Path,
        runner_fps: Optional[float] = 30.0,
        load_config: Callable[[Path], Any],
        capture_config: Callable[[Any], Any],
        build_source: Callable[[Any], Any],
    ) -> None:
        self.config_path = Path(config_path)
        self.runner_fps = runner_fps if (runner_fps and runner_fps > 0) else None
        self._load_config = load_config
        self._capture_config = capture_config
        self._build_source = build_source

        self.buf = LatestFrameBuffer()

        self._runner: Optional[SourceRunner] = None
        self._driver_name: str = "unknown"
        self._running: bool = False
        self._paused: bool = False

        self._last_seq: int = self.buf.seq()
        self._last_ts: Optional[float] = None
        self._fps_smooth: float = 0.0
        self._fps_alpha: float = 0.15

        self._rebuild_runner()

    @property
    def running(self) -> bool:
        return self._running

    @property
    def paused(self) -> bool:
        return self._paused

    @property
    def driver(self) -> str:
        return self._driver_name

    def info_line(self, *, w: Optional[int] = None, h: Optional[int] = None) -> str:
        wh = f"{w}x{h}" if (w and h) else "?"
        return f"Driver: {self.driver} | {wh} | FPS~{self._fps_smooth:.1f} | Running: {self.running} | Paused: {self.paused}"

    def stats(self) -> PreviewStats:
        r = self._require_runner()
        last_err = r.stats.last_error
        return PreviewStats(
            frames_in=r.stats.frames_in,
            frames_out=r.stats.frames_out,
            last_error=str(last_err) if last_err else None,
            fps_smooth=self._fps_smooth,
        )

    def start(self) -> None:
        if self._running:
            return
        r = self._require_runner()
        r.start()
        self._running = True
        self._paused = False
        self._reset_fps()

    def stop(self) -> None:
        if not self._running:
            return
        r = self._require_runner()
        r.stop()
        self._running = False

    def toggle_pause(self) -> None:
        self._paused = not self._paused

    def reload(self) -> None:
        was_running = self._running
        if was_running:
            self.stop()

        self._paused = False
        self._rebuild_runner()

        if was_running:
            self.start()

    def poll_rgb(self) -> Optional[np.ndarray]:
        if not self._running or self._paused:
            return None

        seq, frame = self.buf.wait_next(self._last_seq, timeout_s=0.0)
        if seq == self._last_seq or frame is None:
            return None

        self._last_seq = seq

        rgb = frame.image
        if not (isinstance(rgb, np.ndarray) and rgb.ndim == 3 and rgb.shape[2] == 3):
            return None
        if rgb.dtype != np.uint8:
            rgb = rgb.astype(np.uint8, copy=False)

        self._update_fps(frame.ts_monotonic)
        return rgb

    def shutdown(self) -> None:
        try:
            self.stop()
        except Exception:
            pass

    # -------------------------
    # Internals
    # -------------------------
    def _reset_fps(self) -> None:
        self._last_ts = None
        self._fps_smooth = 0.0
        self._last_seq = self.buf.seq()

    def _update_fps(self, ts: float) -> None:
        if self._last_ts is not None:
            dt = float(ts - self._last_ts)
            if dt > 0:
                fps_now = 1.0 / dt
                self._fps_smooth = (1.0 - self._fps_alpha) * self._fps_smooth + self._fps_alpha * fps_now
        self._last_ts = ts

    def _require_runner(self) -> SourceRunner:
        if self._runner is None:
            raise ValidationError("VisionPreviewSession: runner not initialized")
        return self._runner

    def _build_transforms_from_cfg(self, cfg) -> list[Callable]:
        """
        Build transform callables from VisionConfig.pipeline.transforms.

        Supported:
          - ensure_rgb8
          - crop_rect_norm  (params.rect_norm=[x,y,w,h] in normalized space)
          - resize_max      (params.max_w / params.max_h)
        """
        out: list[Callable] = []
        has_ensure = False

        transforms = getattr(getattr(cfg, "pipeline", None), "transforms", None) or []
        for t in transforms:
            name = getattr(t, "name", None)
            params = getattr(t, "params", None) or {}

            if name == "ensure_rgb8":
                out.append(ensure_rgb8)
                has_ensure = True

            elif name == "crop_rect_norm":
                rect = params.get("rect_norm")
                if not (isinstance(rect, (list, tuple)) and len(rect) == 4):
                    raise ValidationError("crop_rect_norm requires params.rect_norm=[x,y,w,h]")
                r = tuple(float(x) for x in rect)
                # capture r by value
                out.append(lambda fr, r=r: crop_rect_norm(fr, xyxy_norm=r))

            elif name == "resize_max":
                max_w = params.get("max_w")
                max_h = params.get("max_h")
                if max_w is None and max_h is None:
                    raise ValidationError("resize_max requires params.max_w and/or params.max_h")
                mw = int(max_w) if max_w is not None else None
                mh = int(max_h) if max_h is not None else None

                # helpers/vision/transforms/resize.py signature is resize_max(frame, *, max_w, max_h)
                # so if one is None, substitute a very large number to keep "only constrain one side".
                if mw is None:
                    mw = 10**9
                if mh is None:
                    mh = 10**9

                out.append(lambda fr, mw=mw, mh=mh: resize_max(fr, max_w=mw, max_h=mh))

            else:
                raise ValidationError(f"Unknown transform: {name!r}")

        # Ensure UI gets RGB frames even if config forgot it.
        if not has_ensure:
            out.append(ensure_rgb8)

        return out

    def _rebuild_runner(self) -> None:
        cfg = self._load_config(self.config_path)
        cap = self._capture_config(cfg)

        source = self._build_source(cap)
        self._driver_name = cap.driver

        transforms = self._build_transforms_from_cfg(cfg)

        self._runner = SourceRunner(
            source,
            self.buf,
            target_fps=self.runner_fps,
            transforms=transforms,
            name=f"PreviewRunner({cap.driver})",
        )

        self._running = False
        self._reset_fps()
