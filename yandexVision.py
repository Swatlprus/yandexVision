# coding: utf-8
from requests import post
import json
import argparse
import base64
import re

# Функция возвращает IAM-токен для аккаунта на Яндексе.
def get_iam_token(iam_url, oauth_token):
    response = post(iam_url, json={"yandexPassportOauthToken": oauth_token})
    json_data = json.loads(response.text)
    if json_data is not None and 'iamToken' in json_data:
        return json_data['iamToken']
    return None

# Функция отправляет на сервер запрос на распознавание изображения и возвращает ответ сервера.
def request_analyze(vision_url, iam_token, folder_id, image_data):
    response = post(vision_url, headers={'Authorization': 'Bearer '+iam_token}, json={
        'folderId': folder_id,
        'analyzeSpecs': [
            {
                'content': image_data, # Тип файла
                'features': [
                    {
                        'type': 'TEXT_DETECTION', # Тип распознавания
                        'textDetectionConfig': {'languageCodes': ['en', 'ru']} # Язык текста
                    }
                ],
            }
        ]})
    return response.text # Возвращает распознанный текст


def main():
    parser = argparse.ArgumentParser() # Берем аргументы
    parser.add_argument('--image-path', required=True) # Аргумент путь к файлу
    args = parser.parse_args()

    folder_id = '' # Folder ID берем с сервиса Yandex Vision
    oauth_token = '' # OAth Token берем с сервиса Yandex Vision

    iam_url = 'https://iam.api.cloud.yandex.net/iam/v1/tokens'
    vision_url = 'https://vision.api.cloud.yandex.net/vision/v1/batchAnalyze'

    iam_token = get_iam_token(iam_url, oauth_token)
    with open(args.image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    response_text = request_analyze(vision_url, iam_token, folder_id, image_data)

    match = re.findall('\"text\":\s\".*\"', response_text) # Находим значения из поля text
    textStr = "".join(match)
    textStr = textStr.replace('"text":', '')
    textStr = textStr.replace('"', '')
    print(textStr)

    with open('text.txt', 'w') as txt_file: # Сохраняем в файл
        txt_file.write(textStr)


if __name__ == '__main__':
    main()