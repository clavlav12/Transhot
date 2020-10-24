from imgurpython.helpers.error import ImgurClientError
from imgurpython import ImgurClient
from PyQt5.QtCore import QThread, pyqtSignal
import requests
import base64
import six


class MyClient(ImgurClient):
    def upload_from_data(self, contents, config=None, anon=True):
        if not config:
            config = dict()

        b64 = base64.b64encode(contents)
        data = {
            'image': b64,
            'type': 'base64',
        }
        data.update({meta: config[meta] for meta in set(self.allowed_image_fields).intersection(config.keys())})

        return self.make_request('POST', 'upload', data, anon)


def decode(key, string):
    string = base64.urlsafe_b64decode(string + b'===')
    string = string.decode('latin') if six.PY3 else string
    encoded_chars = []
    for i in range(len(string)):
        key_c = key[i % len(key)]
        encoded_c = chr((ord(string[i]) - ord(key_c) + 256) % 256)
        encoded_chars.append(encoded_c)
    encoded_string = ''.join(encoded_chars)
    return encoded_string


def authenticate():
    client_secret = ''
    client_id = ''

    return MyClient(client_id, client_secret)


def upload_image(image, client):
    """
    upload image to imgur
    :param image_path:
    :return: url of the image
    """

    config = {
        'album': None,
        'name': '',
        'title': '',
        'description': ''
    }

    image_url = client.upload_from_data(image, config=config, anon=True)

    return image_url


class Connect(QThread):
    connected = pyqtSignal(ImgurClient)

    def run(self):
        print("connecting...")
        try:
            self.connected.emit(authenticate())
        except (ImgurClientError, requests.exceptions.RequestException) as e:
            pass


class Upload(QThread):
    uploaded = pyqtSignal(str)
    failed = pyqtSignal(Exception)

    def __init__(self, image, client, parent=None):
        super(Upload, self).__init__(parent)
        self.image = image
        self.client = client
        self.start()

    def run(self):
        try:
            image_link = upload_image(self.image, self.client)
            self.uploaded.emit(image_link['link'])
        except (ImgurClientError, requests.exceptions.RequestException) as e:
            self.failed.emit(e)


class uploadToGoogleSearch(QThread):
    uploaded = pyqtSignal(str)
    failed = pyqtSignal(Exception)

    def __init__(self, image, parent=None):
        super(uploadToGoogleSearch, self).__init__(parent)
        self.image = image
        self.start()

    def run(self):
        try:
            filePath = 'F:\TranslateSelected\Screenshot_1.png'
            searchUrl = 'http://www.google.hr/searchbyimage/upload'
            multipart = {'encoded_image': (filePath, self.image), 'image_content': ''}
            response = requests.post(searchUrl, files=multipart, allow_redirects=False)
            fetchUrl = response.headers['Location']
            self.uploaded.emit(fetchUrl)
        except requests.exceptions.RequestException as e:
            self.failed.emit(e)


class UploaderInterface:
    def __init__(self, fail, image_uploaded, connected, parent=None):
        self.connected = connected
        self.image_uploaded = image_uploaded
        self.fail = fail
        self.parent = parent

    def on_image_upload(self, function):
        self.image_uploaded = function

    def on_fail(self, function):
        self.fail = function

    def on_connection(self, function):
        self.connected = function

    def connect(self):
        self.connectionThread = Connect()
        self.connectionThread.connected.connect(self.setClient)
        self.connectionThread.start()
        self.threads = []

    def setClient(self, client):
        self.client = client
        self.connected()

    def upload_image(self, image):
        thread = Upload(image, self.client, self.parent)
        thread.failed.connect(self.fail)
        thread.uploaded.connect(self.image_uploaded)
        thread.uploaded.connect(lambda: self.threads.remove(thread))
        self.threads.append(thread)
        thread.start()

    def upload_image_to_google_search(self, image):
        thread = uploadToGoogleSearch(image, self.parent)
        thread.failed.connect(self.fail)
        thread.uploaded.connect(self.image_uploaded)
        thread.uploaded.connect(lambda: self.threads.remove(thread))
        self.threads.append(thread)
        thread.start()


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)

    def connected():
        interface.upload_image('screenshot_1.png')
    interface = UploaderInterface(lambda: print("fail"), print, connected, None)
    interface.connect()
    sys.exit(app.exec_())
