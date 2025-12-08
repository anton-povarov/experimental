import json
from unittest.mock import MagicMock, patch
from json_requests.fetch import fetch


def test_fetch_parses_json():
    mock_data = json.dumps({"status": "ok"}).encode("utf-8")

    mock_response = MagicMock()
    mock_response.read.return_value = mock_data

    # MagicMock used as context manager must implement __enter__/__exit__
    mock_response.__enter__.return_value = mock_response
    mock_response.__exit__.return_value = None

    with patch("urllib.request.urlopen", return_value=mock_response):
        data = fetch("http://antoxa.name", timeout=1.0)
        assert data == {"status": "ok"}
