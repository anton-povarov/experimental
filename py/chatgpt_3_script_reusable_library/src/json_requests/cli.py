import argparse
import os

from .fetch import fetch

args = argparse.ArgumentParser()
args.add_argument("--url", type=str, required=True, help="URL to fetch")
args.add_argument("--timeout", type=float, required=False, default=None, help="Timeout in seconds")


def main():
    ARGS = args.parse_args()

    env_url = os.getenv("JSON_REQUESTS_URL")
    if env_url:
        ARGS.url = env_url

    env_timeout = os.getenv("JSON_REQUESTS_TIMEOUT")
    if env_timeout:
        ARGS.timeout = float(env_timeout)  # todo: parse float properly

    try:
        json_obj = fetch(ARGS.url, ARGS.timeout)
        print(json_obj)
    except Exception as e:
        print(f"Fetch error: {e}")


if __name__ == "__main__":
    main()
