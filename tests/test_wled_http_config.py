# tests/test_wled_http_config.py

from __future__ import annotations

import pytest

from helpers.toolkits.wled_http.config import WledHttpConfig
from helpers.validation import ValidationError


def test_wled_http_config_from_dict_valid() -> None:
    cfg = WledHttpConfig.from_dict(
        {"ip": "192.168.0.80", "http_port": 80, "timeout_s": 2.5},
        path="wled_http",
    )
    assert cfg.ip == "192.168.0.80"
    assert cfg.http_port == 80
    assert cfg.timeout_s == 2.5


def test_wled_http_config_defaults() -> None:
    cfg = WledHttpConfig.from_dict({"ip": "10.0.0.5"}, path="wled_http")
    assert cfg.http_port == 80
    assert cfg.timeout_s == 2.0


def test_wled_http_config_rejects_bad_ip() -> None:
    with pytest.raises(ValidationError):
        WledHttpConfig.from_dict({"ip": "not_an_ip"}, path="wled_http")


def test_wled_http_config_rejects_bad_port() -> None:
    with pytest.raises(ValidationError):
        WledHttpConfig.from_dict({"ip": "192.168.0.80", "http_port": 70000}, path="wled_http")
