import requests
import json
from datetime import datetime

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
        return response.json()
    
    def get_photos(self):
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

        for index, photo in enumerate(photos):
            likes = photo['likes']['count']
            photo_size = photo['sizes'][-1]['type']
            photo_url = photo['sizes'][-1]['url']

            if likes in likes_count_dict:
                date_uploaded = datetime.utcfromtimestamp(photo['date']).strftime('%Y-%m-%d')
                filename = f'{likes}_{date_uploaded}.jpg'
            else:
                filename = f'{likes}.jpg'
            
            response = requests.get(photo_url)

            if 200 <= response.status_code < 300:
                with open(filename, 'wb') as file:
                    file.write(response.content)
                
                photo_info.append({
                    "file_name": filename,
                    "size": photo_size
                })
            likes_count_dict[likes] = likes

        with open('info.json', 'wt') as json_file:
            json.dump(photo_info, json_file, indent=4)
        

        return photo_info 

    def upload(self):
        destination = self.create_disk()
        photos = self.download()
        headers = {
            "Authorization": self.ya_token
        }
        
        
        for photo in photos:
            filename = photo['file_name']
            file_path = f'./{filename}'
            url = f'https://cloud-api.yandex.net/v1/disk/resources/upload?path={destination}/{filename}&overwrite=true'    

            with open(file_path, 'rb') as file:
                response = requests.get(url, headers=headers)
                upload_url = response.json()['href']

                upload_response = requests.put(upload_url, data=file)

                if upload_response.status_code == 201:
                    print(f"Файл {filename} успешно загружен на Яндекс.Диск в папку")
            

