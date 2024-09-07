import requests
from bs4 import BeautifulSoup
import time
import random

# Список сайтов для получения прокси
proxy_sites = [
    'https://www.socks-proxy.net/',
    'https://www.proxy-list.download/SOCKS5',
    'https://spys.one/en/socks-proxy-list/',
    'https://www.proxy-listen.de/Proxy/Proxyliste.html',
    'https://www.my-proxy.com/free-socks-5-proxy.html',
    'https://proxylist.geonode.com/',
    'https://www.free-proxy-list.com/socks5',
    'https://openproxy.space/list/socks5',
    'https://hidemy.name/en/proxy-list/?type=5',
    'https://www.proxydocker.com/en/proxylist/country/SOCKS5',
    'https://www.proxyscan.io/',
    'https://free-proxy-list.net/socks5-proxy.html',
    'https://www.proxyserverlist24.top/',
    'https://www.sslproxies.org/',
    'https://list.proxylistplus.com/SOCKS-List-1',
    'https://proxypedia.org/en/proxy-lists/socks5/',
    'https://www.ipaddress.com/proxy-list/',
    'https://geonode.com/free-proxy-list/',
    'https://www.proxy-listen.de/Proxy/Socks5-Proxy-List.html',
    'https://www.proxynova.com/proxy-server-list/'
]

# Константы
TIMEOUT = 5
MAX_RESPONSE_TIME = 3

# Список User-Agent для случайной выборки
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Mobile Safari/537.36",
    # Добавьте другие User-Agent строки по желанию
]

def get_proxies_from_site(url):
    proxies = []
    try:
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Вызывает исключение для ошибок HTTP
        soup = BeautifulSoup(response.content, 'lxml')

        # Проверяем, откуда получаем прокси
        if "spys.one" in url:
            # Специфичная обработка для spys.one
            proxy_table = soup.find('table', class_='proxy__t')
            if proxy_table:
                for row in proxy_table.find_all('tr')[1:]:  # Пропускаем заголовок таблицы
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        ip = cols[0].text.strip()
                        port = cols[1].text.strip()
                        proxy = f"{ip}:{port}"
                        proxies.append(proxy)
            else:
                print(f"Таблица не найдена на странице: {url}")
        else:
            # Обработка других сайтов
            proxy_table = soup.find('table')
            if not proxy_table:
                print(f"Таблица не найдена на странице: {url}")
                return proxies
            
            for row in proxy_table.tbody.find_all('tr'):
                cols = row.find_all('td')
                if len(cols) >= 2:
                    ip = cols[0].text.strip()
                    port = cols[1].text.strip()
                    proxy = f"{ip}:{port}"
                    proxies.append(proxy)

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении прокси из {url}: {e}")
    
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
    except requests.exceptions.RequestException:
        return False, None

def gather_proxies():
    all_proxies = []
    for site in proxy_sites:
        proxies = get_proxies_from_site(site)
        all_proxies.extend(proxies)
        time.sleep(random.uniform(1, 3))  # Задержка между запросами
        
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
