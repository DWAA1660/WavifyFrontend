import random
import requests

def check_if_work(proxy):
    try:
        print(proxy)
        # You can use a website like https://www.google.com to test if the proxy works
        response = requests.get("https://www.google.com", proxies={"http": proxy}, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def get_proxy():
    with open('proxies.txt', 'r') as f:
        proxies = f.read().splitlines()  # Read all proxy lines into a list
        random.shuffle(proxies)  # Shuffle the list to randomize proxy selection
        for proxy in proxies:
            if check_if_work("http://" + proxy):
                return "http://" + proxy
    return None  # No working proxy found