# helpers/toolkits/ddp/ddp.py
from __future__ import annotations

"""
DDP (Distributed Display Protocol) sender (minimal).

WLED DDP (RGB) expectations (common setup):
- UDP port: typically 4048
- Header: 10 bytes
- flags: PUSH + version 1 => 0x41 (critical for WLED realtime takeover)
- data_type: 0x01 => RGB
- destination: usually 0x00
- data_offset: byte offset into destination buffer (usually 0)
- length: byte length of pixel payload
"""

import socket
import struct
from typing import Tuple


def build_ddp_packet(sequence: int, pixel_data: bytes, data_offset: int = 0) -> bytes:
    """
    Build a single DDP packet for RGB pixel data.

    Args:
        sequence: 0..255 (wraps), used by receivers to detect ordering
        pixel_data: packed RGB bytes (3 bytes per pixel)
        data_offset: byte offset into destination buffer (usually 0)

    Returns:
        bytes: header + pixel payload
    """
    if not isinstance(pixel_data, (bytes, bytearray, memoryview)):
        raise TypeError(f"pixel_data must be bytes-like, got {type(pixel_data).__name__}")

    flags = 0x41        # PUSH + DDP version 1  (IMPORTANT for WLED realtime)
    data_type = 0x01    # RGB
    destination = 0x00
    length = len(pixel_data)

    # Network byte order: !BBBBLH => 1,1,1,1,4,2 = 10 bytes
    header = struct.pack(
        "!BBBBLH",
        flags,
        sequence & 0xFF,
        data_type,
        destination,
        int(data_offset),
        int(length),
    )
    return header + bytes(pixel_data)


class DdpSender:
    """
    Minimal UDP sender for DDP RGB frames.

    Notes:
    - Not thread-safe by itself; caller should serialize send_frame per sender.
    - Sequence wraps at 256.
    """

    def __init__(self, ip: str, port: int = 4048) -> None:
        self._addr: Tuple[str, int] = (ip, int(port))
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._seq = 0

    def send_frame(self, pixel_data: bytes) -> None:
        packet = build_ddp_packet(self._seq, pixel_data, data_offset=0)
        self._sock.sendto(packet, self._addr)
        self._seq = (self._seq + 1) % 256

    def close(self) -> None:
        try:
            self._sock.close()
        except Exception:
            pass
