import json
import urllib
import urllib.request


def fetch(url: str, timeout: float | None = None):
    """
    Fetch payload from the url and return the parsed object.

    :param url: Url to fetch
    :type url: str
    :param timeout: Optional timeout
    :type timeout: float | None
    """

    with urllib.request.urlopen(url, timeout=timeout) as response:
        data = response.read()
        return json.loads(data)
