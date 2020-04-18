import cv2
import numpy as np


def highlight_white(image):
    r = image[:, :, 2]
    g = image[:, :, 1]
    b = image[:, :, 0]
    mask = r > 200
    r[mask] = 255
    r[~mask] = 0
    mask = g > 200
    r[mask] = 255
    r[~mask] = 0
    mask = b > 200
    r[mask] = 255
    r[~mask] = 0

    return r.copy()


def find_contours(image):
    _, contours, hiers = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # MARK Find phone
    phone = None
    phone_approx = None
    phone_size = 0
    phone_center = (-1, -1)
    phone_hier = None

    for i, contour in enumerate(contours):
        hull = cv2.convexHull(contour, clockwise=True, returnPoints=True)
        epsilon = 0.1 * cv2.arcLength(hull, True)
        approx = cv2.approxPolyDP(hull, epsilon, True)

        if len(approx) == 4:
            size = cv2.contourArea(hull)
            if size > phone_size:
                phone = hull
                phone_approx = approx
                phone_size = size
                phone_hier = hiers[0, i]

    # MARK Find large triangle
    triangle = None
    triangle_size = 0
    triangle_hier = None

    if phone_hier is not None:
        M = cv2.moments(phone)
        phone_center = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
        # current index is set to phone's child's ID
        current = phone_hier[2]

        while current != -1:
            contour = contours[current]
            epsilon = 0.1 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)

            if len(approx) == 3:
                size = cv2.contourArea(contour)
                if size > triangle_size:
                    triangle = contour
                    triangle_size = size
                    triangle_hier = hiers[0, current]

            current = hiers[0, current][0]

    # MARK Find small triangle
    key = None
    key_approx = None
    key_size = 0

    if triangle_hier is not None:
        # current index is set to triangle's child's ID
        current = triangle_hier[2]

        while current != -1:
            contour = contours[current]
            epsilon = 0.1 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)

            if len(approx) == 3:
                size = cv2.contourArea(contour)
                if size > key_size:
                    key = contour
                    key_approx = approx
                    key_size = size

            current = hiers[0, current][0]

    # VISUALIZE
    if phone is not None:
        cv2.drawContours(image, [phone], -1, (255, 0, 0), 6)

    if triangle is not None:
        cv2.drawContours(image, [triangle], -1, (0, 0, 255), 6)
    if key is not None:
        cv2.drawContours(image, [key], -1, (0, 255, 0), 6)

    cv2.imshow('cont', cv2.pyrDown(image))
    ch = cv2.waitKey(1)



    return phone_size, phone_center#triangle_size, key_size


"""
            if phone is not None:
                cv2.drawContours(frame, [phone], -1, (255, 0, 0), 6)
            #     # 2436 x 1125
            #     w, h = 1125 // 4, 2436 // 4
            #     pts1 = phone_approx[:, 0].astype('float32')  # tl, bl, tr, br
            #     pts2 = np.array([[0, 0], [0, h], [w, h], [w, 0]], dtype='float32')
            #
            #     M = cv2.getPerspectiveTransform(pts1, pts2)
            #     phone = cv2.warpPerspective(r, M, (w, h))
            #
            #     cv2.imshow('phone', phone)
            if triangle is not None:
                cv2.drawContours(frame, [triangle], -1, (0, 0, 255), 6)
            if key is not None:
                cv2.drawContours(frame, [key], -1, (0, 255, 0), 6)

            cv2.imshow('cont', cv2.pyrDown(frame))
            ch = cv2.waitKey(1)
            if ch == 27:
                break
"""

from CustomThread import Threadable
class USB(Threadable):
    def __init__(self, port, queue):
        self.film = cv2.VideoCapture(port)
        # self.film.set(3, 1920 // 4)
        # self.film.set(4, 1080 // 4)

        self.queue = queue
        self.enabled = False

    def run(self):
        self.enabled = True

        while self.enabled:
            out = False,
            while not out[0]:
                out = self.get()
            self.queue.put(out)

    def stop(self):
        self.enabled = False

    def get(self):
        frame = self.film.read()
        if frame[0]:
            highlighted = highlight_white(frame[1])
            return True, highlighted, find_contours(highlighted)
        else:
            return False,
