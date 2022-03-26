import requests
import json
from pprint import pprint
from datetime import datetime
from tqdm import tqdm


TOKEN_VK = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'

TOKEN_YA = ''


def get_largest(size_dict):
    if size_dict['width'] >= size_dict['height']:
        return size_dict['width']
    else:
        return size_dict['height']


def get_data(owner_id=552934290, count=5):
    URL_VK = 'https://api.vk.com/method/photos.get'
    params = {
        'owner_id': owner_id,
        'access_token': TOKEN_VK,
        'v': 5.131,
        'extended': 1,
        'album_id': 'profile',
        'photo_sizes': 1,
        'count': count
    }

    res = requests.get(URL_VK, params=params)
    return json.loads(res.text)['response']['items']


def get_data_forya():
    photos = get_data(owner_id=552934290, count=5)
    list_likes = []
    to_ya_list = []
    for photo in photos:
        sizes = photo['sizes']
        max_size = max(sizes, key=get_largest)['type']
        max_size_url = max(sizes, key=get_largest)['url']
        count_likes = str(photo['likes']['count'])
        filename_data = ''
        if count_likes not in list_likes:
            list_likes.append(count_likes)
        else:
            filename_data = datetime.fromtimestamp(photo['date']).strftime('%d-%m-%Y')

        filename = f'{count_likes}{filename_data}.jpg'
        to_ya_list.append({'url': max_size_url, 'file_name': filename, 'size': max_size, 'likes_count': count_likes})
    return to_ya_list


def get_data_photos():
    photos = get_data(owner_id=552934290, count=5)
    new_list = []
    list_likes = []
    for photo in photos:
        sizes = photo['sizes']
        max_size = max(sizes, key=get_largest)['type']
        count_likes = str(photo['likes']['count'])
        filename_data = ''
        if count_likes not in list_likes:
            list_likes.append(count_likes)
        else:
            filename_data = datetime.fromtimestamp(photo['date']).strftime('%d-%m-%Y')
        filename = f'{count_likes}{filename_data}.jpg'
        new_list.append({'file_name': filename, 'size': max_size})
    return new_list


with open('photo_data.jsn', 'w') as f:
    json.dump(get_data_photos(), f)



class YaUploader:
    def __init__(self, TOKEN_YA: str):
        self.TOKEN_YA = TOKEN_YA

    def upload_photos(self, file_link, disk_file_path):
        upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.TOKEN_YA)
        }
        params = {"url": file_link, "path": disk_file_path, "overwrite": False}
        response = requests.post(url=upload_url, headers=headers, params=params)
        pprint(response.json())
        return response.json()



if __name__ == '__main__':
    pprint(get_data_forya())
    ya = YaUploader(TOKEN_YA=TOKEN_YA)
    index = 0
    name_foto = ''
    for p in tqdm(get_data_forya()):
        n_photo = p['url']
        name_foto = p['file_name']
        path_yandex = f'/vksavephotos/{name_foto}'
        ya.upload_photos(n_photo, path_yandex)
        index += 1