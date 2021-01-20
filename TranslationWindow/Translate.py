import io
from PyQt5.QtCore import QBuffer
from threading import Thread
import modded_pytesseract as tess
from googletrans import Translator, LANGUAGES
import cv2
from os import startfile
import numpy
try:
    from ISO_converter import ISO_2_TO_3, ENGLISH_3, ISO_3_TO_2
except ModuleNotFoundError:
    from SettingsDialog.ISO_converter import ISO_2_TO_3, ENGLISH_3, ISO_3_TO_2


def generate_translator():
    return Translator(['translate.googleapis.com'])


tess.modded_pytesseract.tesseract_cmd = r'tesseract2\tesseract.exe'
trans = generate_translator()
languages = LANGUAGES
languages['auto'] = 'Auto'


class TextRecognizer:
    texts = []
    lang = ''
    config = ''

    def __init__(self, img, name=''):
        self.name = name
        self.image = img
        self.dict, self.text = tess.image_to_data_and_text(self.image, self.lang, self.config)
        self.texts.append(self)

    def getAverageConfidence(self):
        return self.avg([self.dict['conf'][i] for i in range(len(self.dict['conf']))
                         if not self.dict['conf'][i] == '-1'])

    def getText(self):
        return self.text

    def __str__(self):
        return "" + \
               self.name + ":" + '\n' + \
               "confident: " f"{self.getAverageConfidence():.2f}" + '\n'

    @staticmethod
    def avg(lst):
        try:
            return sum(lst) / len(lst)
        except ZeroDivisionError:
            return -1

    @classmethod
    def mostReliable(cls):
        return max(cls.texts, key=lambda x: x.getAverageConfidence())

    @classmethod
    def clear(cls):
        cls.texts.clear()


class TextRecognizerThread(Thread):
    def __init__(self, img, name='', start_now=True):
        super(TextRecognizerThread, self).__init__()
        self.image = img
        self.name = name
        if start_now:
            self.start()

    def run(self):
        TextRecognizer(self.image, self.name)


def convertQImageToMat(incomingImage):
    """ Converts a QImage into an opencv MAT format  """

    incomingImage = incomingImage.toImage().convertToFormat(4)

    width = incomingImage.width()
    height = incomingImage.height()

    ptr = incomingImage.bits()
    ptr.setsize(incomingImage.byteCount())
    arr = numpy.array(ptr).reshape(height, width, 4)  # Copies the data

    return arr


def improveImage(img):
    gray = cv2.cvtColor(convertQImageToMat(img), cv2.COLOR_BGR2GRAY)

    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    thresh2 = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_BINARY)[1]

    return thresh, thresh2


def TranslateFromImage(image, destination: str = 'he', src: str = 'auto', imsource=None):
    if imsource is not None:
        imsource = [i for i in imsource if i in ISO_3_TO_2]

    if imsource is None or imsource == [''] or imsource == []:
        imsource = []
        if not src == 'auto':
            imsource.append(ENGLISH_3[languages[src].capitalize()])
            imsource.append(ENGLISH_3[languages[destination].capitalize()])

        if 'eng' not in imsource:
            imsource.append('eng')

    improved = improveImage(image)

    TextRecognizer.clear()
    TextRecognizer.lang = '+'.join(imsource)
    TextRecognizer.config = '--psm 6'
    threads = [
        TextRecognizerThread(improved[0], 'first'),
        TextRecognizerThread(improved[1], 'second'),
        TextRecognizerThread(255 - improved[0], 'third'),
        TextRecognizerThread(255 - improved[1], 'fourth')
    ]
    for thread in threads:
        thread.join()

    final_result = TextRecognizer.mostReliable().getText()

    yield final_result

    t = translate(
        final_result,
        src='auto',
        dest=destination
    )

    if languages[t.src] == languages[t.dest] and not src == 'auto':
        t = translate(
            final_result,
            dest=src,
            src=destination
        )

    yield t.text, t.src, t.dest

    yield t.pronunciation


def TranslateFromText(text, destination: str = 'he', src: str = 'auto'):
    t = translate(
        text,
        dest=destination,
        src=src
    )
    return text, t.text, t.src, t.dest


def translate(text, dest, src):
    global trans
    try:
        t = trans.translate(
            text,
            dest=dest,
            src=src
        )
    except Exception as e:
        print(e)
        trans = generate_translator()
        t = trans.translate(
            text,
            dest=dest,
            src=src
        )
    return t

def openImage(path):
    startfile(path)
