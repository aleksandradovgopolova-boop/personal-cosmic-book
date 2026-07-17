import pytest

from api.chart import _digital_root, chart_from_payload


def test_digital_root_keeps_master_numbers():
    assert _digital_root(29, keep_masters=True) == 11
    assert _digital_root(38, keep_masters=False) == 2


def test_chart_from_payload_with_kerykeion():
    pytest.importorskip("kerykeion")

    chart = chart_from_payload(
        {
            "name": "Sofia",
            "date": "1994-10-06",
            "time": "14:30",
            "city": "Moscow",
            "country": "RU",
        }
    )

    assert chart["subject"]["name"] == "Sofia"
    assert chart["sun"]["sign"]
    assert chart["moon"]["sign"]
    assert chart["asc"]["sign"]
    assert chart["numerology"]["life_path"]
    assert len(chart["input_hash"]) == 64
