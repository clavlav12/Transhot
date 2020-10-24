import cv2
import numpy as np


def image_tint(src, tint=(1, 0, 0)):
    if isinstance(src, str):
        src = cv2.imread(src, cv2.IMREAD_UNCHANGED)
    return src * np.array([*reversed(tint), 1])


def inverse(src):
    for i in src:
        for j in i:
            j[0] = 255 - j[0]
            j[1] = 255 - j[1]
            j[2] = 255 - j[2]


if __name__ == '__main__':
    from glob import glob
    for image in glob('*.png'):
        img = cv2.imread(image, cv2.IMREAD_UNCHANGED)
        inverse(img)
        new = image_tint(img, (22/255, 146/255, 203/255)).astype(np.uint8)

        cv2.imwrite(f'blue\\blue {image}', new)

    # cv2.imshow('new', new)
    # cv2.waitKey(0)

