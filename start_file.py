import sys
import os
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow
from files.social_network import Vk
from files.uploaders import GoUploader, YaUploader, TOKEN_VK

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        adress = os.path.join(os.getcwd(), 'files')
        interface = os.path.join(adress, 'Window.ui')
        uic.loadUi(interface, self)
        self.pushButton.clicked.connect(self.run)
        self.progressBar.setMaximum(4)
        self.count = 0
        self.startData = {}

    def run(self):
        self.textEdit_2.clear()
        self.startData = {
            'id_user': self.lineEdit.text(),
            'token_drive': ''.join(self.textEdit.toPlainText().split()),
            'name_catalog': self.lineEdit_2.text()
        }
        for name in self.startData:
            if not self.startData[name]:
                textinfo = f'Не указан {name}'
                self.__messages(textinfo)
        self.startData['socnetwork'] = self.comboBox_2.currentText()
        self.startData['cloudDrive'] = self.comboBox.currentText()
        if all(self.startData.values()):
            self._connect()
            self._progress()
            self.__messages('Закончили')
            self.__clear()

    def __clear(self):
        # Очищаем переменные, готовимся к следующему запросу
        self.startData = {}
        self.count = 0
        self.progressBar.setMaximum(4)
        self.progressBar.setValue(self.count)

    def __messages(self, text):
        self.textEdit_2.append(text)

    def _connect(self):
        network = None
        if self.startData['socnetwork'] == 'VKontakte':
            network = Vk(TOKEN_VK)
        if network:
            self.__messages('Ищем фотографии')
            user_photos = network.get_photos(self.startData['id_user'])
        else:
            return self._fail('Ошибка подключения к соцсети')
        """Проверяем грузанулись ли фотки, если да то выбираем диск для сохранения."""
        """Если нет отправляем сообщение с ошибкой"""
        if 'error' not in user_photos:
            self._progress()  # прогресс бар
            self.__messages('Фотографии найдены')  # сообщения пользователю
            self.__messages('Подключаемся к диску')
            if self.startData['cloudDrive'] == 'Google Drive':  # Подключаем диски
                re = GoUploader(self.startData['token_drive'])
                if re:
                    self._progress()  # прогресс бар
                    self.__messages('Подключились к диску')  # сообщения пользователю
                    re.new_catalog = self.startData.get('name_catalog', 'NoName')
                    try:
                        return self._download(user_photos, re)
                    except:
                        self._fail('Ошибка в токене')
                else:
                    return self._fail('Ошибка подключения к диску')
            elif self.startData['cloudDrive'] == 'Яндекс Диск':
                re = YaUploader(self.startData['token_drive'])
                if re:
                    self._progress()  # прогресс бар
                    self.__messages('Подключились к диску')  # сообщения пользователю
                    re.new_catalog = self.startData.get('name_catalog', 'NoName')
                    try:
                        return self._download(user_photos, re)
                    except:
                        self._fail('Ошибка в токене')
                else:
                    return self._fail('Ошибка подключения к диску')
        elif 'error' in user_photos:
            self._fail(user_photos['error']['error_msg'])
        else:
            self._fail('Фотографий нет')

    def _download(self, photos, uploader):
        self.__messages('Загружаем фотографии на диск')
        result = uploader.upload(photos)
        if result:
            self._progress()  # прогресс бар
            self.__messages('Загрузили фотографии')  # сообщения пользователю
        else:
            self._fail('Фотографии не загружены, проверьте токен')

    def _progress(self):
        self.count += 1
        self.progressBar.setValue(self.count)

    def _fail(self, message):
        self.__messages(message)
        self.__clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWindow()
    ex.show()
    sys.exit(app.exec_())
