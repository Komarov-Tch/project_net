import requests
import json

TOKEN_VK = 'a67f00c673c3d4b12800dd0ba29579ec56d804f3c5f3bbcef5328d4b3981fa5987b951cf2c8d8b24b9abd'


class YaUploader:

    def __init__(self, token):
        self.token = token
        self.new_catalog = ''

    def _get_geader(self):
        return {'Content-Type': 'application/json',
                'Authorization': f'OAuth {self.token}'}

    def _create_catalog(self):
        url = 'https://cloud-api.yandex.net/v1/disk/resources?path=' + self.new_catalog
        response = requests.put(url=url, headers=self._get_geader(), timeout=5)
        return response
    def _create_json_file(self, info_photos):
        result = [{'filename': f'{name}.jpg', 'size': size} for name, size in info_photos]
        with open('photos_info_yd.txt', 'w') as save_file:
            json.dump(result, save_file, indent=4)

    def upload(self, photos):
        files_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = self._get_geader()
        all_photos_info = []
        result = self._create_catalog()
        if result:
            for size, url_photo, name in photos:
                params = {'path': f'{self.new_catalog}/{name}', 'overwrite': 'false'}
                response = requests.get(url=files_url, headers=headers, params=params, timeout=5)
                response_json = response.json()
                if response:
                    href = response_json.get('href', '')
                    response = requests.put(href, data=requests.get(url_photo).content)
                    if response.status_code == 201:
                        all_photos_info.append((name, size))
                    elif 400 <= response.status_code < 600:
                        print('\tОшибка', response.status_code)
            self._create_json_file(all_photos_info)


class GoUploader:
    def __init__(self, token):
        self.new_catalog = ''
        self.token = 'Bearer ' + token
        self.url = 'https://www.googleapis.com/drive/v3/files'
        self.headers = {'Authorization': self.token, 'Content-type': 'application/json'}

    def _connecct(self):
        # Вызываем метод, который создает каталог на гугл диске, он возвращает код, и json файл запроса.
        # Из Json файла нам нужен id, что бы кудато сохранять потом фотографии
        new_catalog = self.new_catalog
        response_create_catalog, response_create_catalog_json = self._create_catalog(new_catalog)
        self.id_create_catalog = response_create_catalog_json['id']
        file = False
        if response_create_catalog.status_code == 200:
            response = requests.get(url=self.url, headers=self.headers)
            for i in response.json()['files']:
                if i['name'] == new_catalog \
                        and i['mimeType'] == 'application/vnd.google-apps.folder' \
                        and i['id'] == self.id_create_catalog:
                    file = True
                    break
            return file
        return False

    def _create_catalog(self, name):
        body = {'name': name, 'mimeType': "application/vnd.google-apps.folder"}
        response = requests.post(url=self.url, headers=self.headers, json=body, )
        return response, response.json()

    def _create_json_file(self, info_photos):
        result = [{'filename': f'{name}.jpg', 'size': size} for name, size in info_photos]
        with open('photos_info_gd.txt', 'w') as save_file:
            json.dump(result, save_file, indent=4)

    def upload(self, photos):
        result_create_catalog = self._connecct()
        upload_url = "https://www.googleapis.com/upload/drive/v3/files/?uploadType=multipart"
        headers = {'Authorization': self.token}
        info_photos = []
        if result_create_catalog:
            for size, url, name in photos:
                para = {
                    "name": f"{name}.jpg",
                    "parents": [self.id_create_catalog]
                }
                files = {
                    "data": ("metadata", json.dumps(para), "application/json; charset=UTF-8"),
                    "file": requests.get(url).content,
                }
                response = requests.post(url=upload_url, headers=headers, files=files)
                if response:
                    info_photos.append((name, size))
        self._create_json_file(info_photos)
