import asyncio
import subprocess
import logging
import random
import aiofiles

# Настройка логирования
logging.basicConfig(filename='scan_results.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Список User-Agent
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
    # Добавьте сюда другие User-Agent
]

# Ограничение одновременных задач (например, 5)
semaphore = asyncio.Semaphore(5)

async def scan_website(url, vulnerable_sites):
    user_agent = random.choice(user_agents)
    async with semaphore:
        try:
            logging.info(f"Starting scan for {url} with User-Agent: {user_agent}")
            
            # Запуск sqlmap
            result = await asyncio.create_subprocess_exec(
                'sqlmap', '-u', url, '--user-agent', user_agent, '--batch',
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            stdout_decoded = stdout.decode()
            stderr_decoded = stderr.decode()
            
            if stdout_decoded:
                logging.info(f"Results for {url}:\n{stdout_decoded}")
                if "vulnerable" in stdout_decoded.lower():
                    vulnerable_sites.append(url)
                    logging.info(f"{url} is vulnerable!")
            
            if stderr_decoded:
                logging.error(f"Errors for {url}:\n{stderr_decoded}")
        
        except Exception as e:
            logging.error(f"An error occurred with {url}: {str(e)}")

async def load_urls_from_file(filename):
    """Функция для асинхронной загрузки URL-адресов из файла"""
    urls = []
    async with aiofiles.open(filename, 'r') as f:
        async for line in f:
            url = line.strip()  # Убираем пробелы и символы новой строки
            if url:  # Игнорируем пустые строки
                urls.append(url)
    return urls

async def main():
    # Загрузка URL из файла
    urls = await load_urls_from_file('websites.txt')
    
    vulnerable_sites = []
    tasks = [scan_website(url, vulnerable_sites) for url in urls]
    await asyncio.gather(*tasks)
    
    # Асинхронная запись уязвимых сайтов в файл
    async with aiofiles.open('vulnerable_sites.txt', 'w') as f:
        for site in vulnerable_sites:
            await f.write(f"{site}\n")

if __name__ == "__main__":
    asyncio.run(main())
