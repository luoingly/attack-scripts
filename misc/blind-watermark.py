import numpy as np


"""
Blind WaterMark
===============

"""


def analysis(image: np.ndarray) -> np.ndarray:

    figure = np.fft.fft2(image)
    figure = np.abs(np.log(figure))
    figure = (figure - np.min(figure)) / \
        (np.max(figure) - np.min(figure)) * 255

    return figure


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import cv2

    file_path = input("[>] Input the image file path: ").strip()

    print("[*] Analyzing...")

    image = cv2.imread(file_path, 0)
    figure = analysis(image)
    figure_centered = np.fft.fftshift(figure)

    print("[+] Check the plots...")

    plt.subplot(121), \
        plt.imshow(figure, 'gray'), plt.title('ORIGINAL')
    plt.subplot(122), \
        plt.imshow(figure_centered, 'gray'), plt.title('CENTERED')
    plt.show()
