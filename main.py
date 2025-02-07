import requests
from urllib.parse import urlparse
from dotenv import load_dotenv
import os


load_dotenv()


def is_shortened_link(url):
    try:
        result = urlparse(url)
        if not all([result.netloc]):
            return False
        return url.startswith("https://vk.cc/")
    except ValueError:
        return False


def shorten_link(token, url):
    payload = {
        "v": "5.199",
        "access_token": token,
        "url": url,
        "private": 0
    }
    try:
        response = requests.get('https://api.vk.ru/method/utils.getShortLink', params=payload)
        response.raise_for_status()
        data = response.json()
        if 'error' in data:
            raise Exception(f"API Error: {data['error']['error_msg']}")
        short_link = data['response']['short_url']
        return short_link
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")


def count_clicks(token, short_link):
    if not short_link.startswith("https://vk.cc/"):
        print("Ошибка: Неверный формат сокращённой ссылки.")
        return None

    key = short_link.split('/')[-1]

    payload = {
        "v": "5.199",
        "access_token": token,
        "key": key,
        "interval": "forever",
        "extended": 0
    }
    try:
        response = requests.get('https://api.vk.ru/method/utils.getLinkStats', params=payload)
        response.raise_for_status()
        data = response.json()
        if 'error' in data:
            raise Exception(f"API Error: {data['error']['error_msg']}")
        clicks_count = sum(item['views'] for item in data['response']['stats'])
        return clicks_count
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")


def main():
    token = os.getenv("VK_ACCESS_TOKEN")
    if not token:
        print("Ошибка: Токен VK_ACCESS_TOKEN не найден в переменных окружения.")
        return

    user_input = input("Введите URL для сокращения: ").strip()
    if not user_input:
        print("Ошибка: Введённая строка пуста.")
        return

    if is_shortened_link(user_input):
        print("Ссылка уже сокращена.")
        clicks_count = count_clicks(token, user_input)
        if clicks_count is not None:
            print(f"Количество кликов: {clicks_count}")
        else:
            print("Не удалось получить статистику кликов.")
    else:
        short_link = shorten_link(token, user_input)
        if short_link:
            print(f"Сокращённая ссылка: {short_link}")
            clicks_count = count_clicks(token, short_link)
            if clicks_count is not None:
                print(f"Количество кликов: {clicks_count}")
            else:
                print("Не удалось получить статистику кликов.")
        else:
            print("Не удалось получить сокращённую ссылку.")


if __name__ == "__main__":
    main()
