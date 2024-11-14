import random
import requests
from security import safe_requests


def check_if_work(proxy):
    try:
        print(proxy)
        response = safe_requests.get(
            "https://www.google.com", proxies={"http": proxy}, timeout=5
        )
        return response.status_code == 200
    except requests.RequestException:
        return False


def get_proxy():
    with open("proxies.txt", "r") as f:
        proxies = f.read().splitlines()
        random.shuffle(proxies)
        for proxy in proxies:
            if check_if_work("http://" + proxy):
                return "http://" + proxy
    return None
