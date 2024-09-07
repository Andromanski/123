import requests
import time
import random
from concurrent.futures import ThreadPoolExecutor

# Константы
TIMEOUT = 5
MAX_RESPONSE_TIME = 3
INPUT_FILE = 'proxies.txt'
OUTPUT_FILE = 'good_socks5_proxies.txt'

# Список User-Agent для случайной выборки
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:89.0) Gecko/20100101 Firefox/89.0"
]

def read_proxies_from_file(file_path):
    with open(file_path, 'r') as file:
        proxies = [line.strip() for line in file if line.strip()]
    return proxies

def check_proxy_socks5(proxy):
    try:
        proxies = {
            'http': f'socks5://{proxy}',
            'https': f'socks5://{proxy}'
        }
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        start_time = time.time()
        response = requests.get('https://httpbin.org/ip', proxies=proxies, headers=headers, timeout=TIMEOUT)
        response_time = time.time() - start_time

        if response.status_code == 200 and response_time <= MAX_RESPONSE_TIME:
            return proxy, response_time
        else:
            return None, response_time
    except requests.exceptions.RequestException:
        return None, None

def save_proxies_to_file(proxies, filename):
    with open(filename, 'w') as file:
        for proxy in proxies:
            file.write(f"{proxy}\n")

def main():
    proxies = read_proxies_from_file(INPUT_FILE)
    good_proxies = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(check_proxy_socks5, proxies)

    for proxy, response_time in results:
        if proxy:
            good_proxies.append(proxy)
            print(f"Valid proxy: {proxy} with response time: {response_time:.2f} seconds")

    if good_proxies:
        save_proxies_to_file(good_proxies, OUTPUT_FILE)
        print(f"Найдено {len(good_proxies)} хороших прокси.")
    else:
        print("Не найдено хороших прокси.")

if __name__ == "__main__":
    main()
