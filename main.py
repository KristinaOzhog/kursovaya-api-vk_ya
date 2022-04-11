import requests
import json
from pprint import pprint
from datetime import datetime
from tqdm import tqdm

vk_id = input('Введите ID владельца фотографии: ')
count_photos = input('Введите количество фото для загрузки: ')

token_vk = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'
token_ya = ''


class VKPhotos:
    def __init__(self, token_vk: str):
        self.token_vk = token_vk

    def get_largest(self, size_dict):
        if size_dict['width'] >= size_dict['height']:
            return size_dict['width']
        else:
            return size_dict['height']

    def get_data(self):
        url_vk = 'https://api.vk.com/method/photos.get'
        params = {
            'owner_id': {vk_id},
            'access_token': token_vk,
            'v': 5.131,
            'extended': 1,
            'album_id': 'profile',
            'photo_sizes': 1,
            'count': {count_photos}
        }

        res = requests.get(url_vk, params=params)
        return json.loads(res.text)['response']['items']

    def get_data_forya(self):
        photos = self.get_data()
        list_likes = []
        to_ya_list = []
        for photo in photos:
            sizes = photo['sizes']
            max_size = max(sizes, key=self.get_largest)['type']
            max_size_url = max(sizes, key=self.get_largest)['url']
            count_likes = str(photo['likes']['count'])
            filename_data = ''
            if count_likes not in list_likes:
                list_likes.append(count_likes)
            else:
                filename_data = datetime.fromtimestamp(photo['date']).strftime('%d-%m-%Y')

            filename = f'{count_likes}{filename_data}.jpg'
            to_ya_list.append({'url': max_size_url, 'file_name': filename, 'size': max_size, 'likes_count': count_likes})
        return to_ya_list

    def get_data_photos(self):
        photos = self.get_data()
        new_list = []
        list_likes = []
        for photo in photos:
            sizes = photo['sizes']
            max_size = max(sizes, key=self.get_largest)['type']
            count_likes = str(photo['likes']['count'])
            filename_data = ''
            if count_likes not in list_likes:
                list_likes.append(count_likes)
            else:
                filename_data = datetime.fromtimestamp(photo['date']).strftime('%d-%m-%Y')
            filename = f'{count_likes}{filename_data}.jpg'
            new_list.append({'file_name': filename, 'size': max_size})
        return new_list


vk = VKPhotos(token_vk=token_vk)
with open('photo_data.json', 'w') as f:
    json.dump(vk.get_data_photos(), f)


class YaUploader:
    def __init__(self, token_ya: str):
        self.token_ya = token_ya

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token_ya)
        }

    def create_folder(self, file_folder):
        url_folder = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = self.get_headers()
        params = {'path': file_folder}
        response_folder = requests.put(url_folder, headers=headers, params=params)
        return response_folder

    def upload_photos(self, file_link, disk_file_path):
        upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = self.get_headers()
        params = {"url": file_link, "path": disk_file_path, "overwrite": False}
        response = requests.post(url=upload_url, headers=headers, params=params)
        pprint(response.json())
        return response.json()


if __name__ == '__main__':
    vk = VKPhotos(token_vk=token_vk)
    pprint(vk.get_data_forya())
    ya = YaUploader(token_ya=token_ya)
    name_folder = input('Введите название папки: ')
    ya.create_folder(f'{name_folder}')
    index = 0
    name_foto = ''
    for p in tqdm(vk.get_data_forya()):
        n_photo = p['url']
        name_foto = p['file_name']
        path_yandex = f'/{name_folder}/{name_foto}'
        ya.upload_photos(n_photo, path_yandex)
        index += 1