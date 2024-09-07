import requests
from bs4 import BeautifulSoup
import time
import random

# Константы
TIMEOUT = 5
MAX_RESPONSE_TIME = 3

# Список User-Agent для случайной выборки
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:89.0) Gecko/20100101 Firefox/89.0"
]

def get_proxies_from_spys_one():
    proxies = []
    url = "https://spys.one/en/free-proxy-list/"
    
    try:
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Ищем таблицу с прокси
        proxy_table = soup.find('table', class_='proxy__t')
        if proxy_table:
            for row in proxy_table.find_all('tr')[1:]:  # Пропускаем заголовок
                cols = row.find_all('td')
                if len(cols) >= 2:
                    ip = cols[0].text.strip()
                    port = cols[1].text.strip()
                    proxy = f"{ip}:{port}"
                    proxies.append(proxy)
        else:
            print("Таблица с прокси не найдена.")

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении прокси: {e}")
    except Exception as e:
        print(f"Ошибка при парсинге HTML: {e}")

    return proxies

def check_proxy_socks5(proxy):
    try:
        proxies = {
            'http': f'socks5://{proxy}',
            'https': f'socks5://{proxy}'
        }
        start_time = time.time()
        response = requests.get('https://httpbin.org/ip', proxies=proxies, timeout=TIMEOUT)
        response_time = time.time() - start_time

        if response.status_code == 200 and response_time <= MAX_RESPONSE_TIME:
            return True, response_time
        else:
            return False, response_time
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при проверке прокси {proxy}: {e}")
        return False, None

def gather_proxies():
    all_proxies = get_proxies_from_spys_one()
    good_proxies = []
    for proxy in all_proxies:
        is_good, response_time = check_proxy_socks5(proxy)
        if is_good:
            good_proxies.append(proxy)

    return good_proxies

def save_proxies_to_file(proxies, filename='good_socks5_proxies.txt'):
    with open(filename, 'w') as file:
        for proxy in proxies:
            file.write(f"{proxy}\n")

if __name__ == "__main__":
    good_proxies = gather_proxies()
    if good_proxies:
        save_proxies_to_file(good_proxies)
        print(f"Найдено {len(good_proxies)} хороших прокси.")
    else:
        print("Не найдено хороших прокси.")
