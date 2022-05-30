import requests
from datetime import datetime


class Vk:
    def __init__(self, token):
        self.token = token
        self.adress = 'https://api.vk.com/method/'

    def _connect(self, id_user):
        metod = 'photos.get'
        params = {'owner_id': id_user,
                  'album_id': 'profile',
                  'rev': 0,
                  'extended': 1,
                  'count': 1000,
                  'photo_sizes': 1,
                  'v': 5.131}
        url = f'{self.adress}{metod}'
        response = requests.get(url=url, params={**params, 'access_token': self.token}, timeout=5)
        return response

    def get_photos(self, id_user, n=5) -> list:
        response = self._connect(id_user=id_user)
        if response and 'error' not in response.json():
            all_photos = []
            res = response.json()['response']['items']
            for photos in res:
                likes_photo = photos['likes']['count']
                date_photo = photos['date']
                photo = photos['sizes'][-1]
                size_photo = photo.get('height', 0) * photo.get('width', 0)
                all_photos.append((size_photo, photo['url'], likes_photo, date_photo))
            all_photos.sort(key=lambda x: -x[0])
            n = n if len(all_photos) >= 5 else len(all_photos)
            photos_with_maximum_size = all_photos[0:n]
            test_of_copy = [l for s, u, l, p in photos_with_maximum_size]
            result_photo = []
            for s, u, l, p in photos_with_maximum_size:
                if test_of_copy.count(l) > 1:
                    p = datetime.utcfromtimestamp(p).strftime('%Y-%m-%d %H-%M-%S')
                    name = str(l) + ' ' + str(p)
                else:
                    name = str(l)
                result_photo.append((s, u, name))
            return result_photo
        elif response and 'error' in response.json():
            return response.json()
        else:
            print("Ошибка выполнения запроса:")
            print(self.adress)
            print(f"Http статус: {response.status_code}, {response.reason}")
