import requests
import json
from datetime import datetime
import sys

class BackUp:
    def __init__(self, access_token, user_id, ya_token, version='5.131'):
        self.token = access_token
        self.id = user_id
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}
        self.ya_token = ya_token

    def users_info(self):
        url = 'https://api.vk.com/method/users.get'
        params = {'user_ids': self.id}
        response = requests.get(url, params={**self.params, **params})

        if response.status_code == 200:
            user_data = response.json()
            if 'error' in user_data:
                print('ПОльзователь не найден')
                sys.exit()
            return user_data
        else:
            print(f'Возникла ошибка {response.status_code}')
            sys.exit()
    
    def get_photos(self):
        user = self.users_info()
        if user:
            url = 'https://api.vk.com/method/photos.get'
            params = {'owner_id': self.id, 'album_id': 'profile', 'extended' : 1}
            response = requests.get(url, params={**self.params, **params})
            return response.json()
    
    def create_disk(self):
        folder_name = input('Как хотите назвать вашу папку ? ')
        url = f'https://cloud-api.yandex.net/v1/disk/resources?path=%2F{folder_name}'
        headers = {
            "Authorization": self.ya_token
        }
        requests.put(url, headers=headers)
        return folder_name
    
    def download(self):
        photos_data = self.get_photos()
        photos = photos_data['response']['items']
        photo_info = []
        likes_count_dict = {}
        destination = self.create_disk()

        headers = {
            "Authorization": self.ya_token
        }

        for photo in photos:
            likes = photo['likes']['count']
            photo_size = photo['sizes'][-1]['type']
            photo_url = photo['sizes'][-1]['url']

            if likes in likes_count_dict:
                date_uploaded = datetime.utcfromtimestamp(photo['date']).strftime('%Y-%m-%d')
                filename = f'{likes}_{date_uploaded}.jpg'
            else:
                filename = f'{likes}.jpg'

            url_disk = f'https://cloud-api.yandex.net/v1/disk/resources/upload?path=%2F{destination}/{filename}'
            response = requests.get(url_disk, headers=headers)

            if response.status_code == 200:
                upload_data = response.json()
                upload_url = upload_data.get('href')

                if upload_url:
                    upload_response = requests.put(upload_url, data=requests.get(photo_url).content)

                    if upload_response.status_code == 201:
                        print(f"Файл {filename} успешно добавлен на Яндекс.Диск")
                    else:
                        print(f"Ошибка при загрузки файла {filename} (ошибка: {upload_response.status_code})")
                else:
                    print("Ошибка при получении URL Яндекс.Диска")
            elif response.status_code == 409:
                print('Ошибка: файл уже существует в папке')
            else:
                print('Ошибка:', response.status_code)

            photo_info.append({
                "file_name": filename,
                "size": photo_size
            })

            likes_count_dict[likes] = likes
        output_file = 'photo_info.json'  # Имя файла для сохранения информации
        with open(output_file, 'w') as json_file:
            json.dump(photo_info, json_file, indent=4)

        print(f'Информация о файлах сохранена в {output_file}')


            

