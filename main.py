import requests
from urllib.parse import urlparse
from dotenv import load_dotenv
import os


def is_shortened_link(token, url):
    parsed_url = urlparse(url)
    key = parsed_url.path.lstrip('/')

    payload = {
        "v": "5.199",
        "access_token": token,
        "key": key,
        "interval": "forever",
        "extended": 0
    }

    response = requests.get('https://api.vk.ru/method/utils.getLinkStats', params=payload)
    response.raise_for_status()
    response_data = response.json()

    if 'error' in response_data:
        if response_data['error']['error_code']:
            return False
        raise Exception(f"API Error: {response_data['error']['error_msg']}")
    return True


def shorten_link(token, url):
    payload = {
        "v": "5.199",
        "access_token": token,
        "url": url,
        "private": 0
    }
    response = requests.get('https://api.vk.ru/method/utils.getShortLink', params=payload)
    response.raise_for_status()
    response_data = response.json()
    if 'error' in response_data:
        raise Exception(f"API Error: {response_data['error']['error_msg']}")
    short_link = response_data['response']['short_url']
    return short_link


def count_clicks(token, short_link):
    key = short_link.split('/')[-1]
    payload = {
        "v": "5.199",
        "access_token": token,
        "key": key,
        "interval": "forever",
        "extended": 0
    }

    response = requests.get('https://api.vk.ru/method/utils.getLinkStats', params=payload)
    response.raise_for_status()
    response_data = response.json()
    if 'error' in response_data:
        raise Exception(f"API Error: {response_data['error']['error_msg']}")
    clicks_count = response_data['response']['stats'][0]['views']
    return clicks_count


def main():
    try:
        load_dotenv()
        token = os.getenv("VK_ACCESS_TOKEN")

        if not token:
            print("Ошибка: Токен VK_ACCESS_TOKEN не найден в переменных окружения.")
            return

        user_input = input("Введите URL для сокращения: ").strip()
        if not user_input:
            print("Ошибка: Введённая строка пуста.")
            return

        if is_shortened_link(token, user_input):
            clicks_count = count_clicks(token, user_input)
            print(f"Количество кликов: {clicks_count}")
        else:
            short_link = shorten_link(token, user_input)
            if short_link:
                print(f"Сокращённая ссылка: {short_link}")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")


if __name__ == "__main__":
    main()
