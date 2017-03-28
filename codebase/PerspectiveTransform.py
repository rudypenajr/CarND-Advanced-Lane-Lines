import numpy as np
import cv2

class PerspectiveTransform:
    def __init__(self):
        # Provided by Udacity
        src_pts = np.float32([[585, 460], [203, 720], [1127, 720], [695, 460]])
        dst_pts = np.float32([[320, 0], [320, 720], [960, 720], [960, 0]])

        # Undistory and Transform (Lesson 17)
        # Given src and dst points, calculate the perspective transform matrix
        self.M = cv2.getPerspectiveTransform(src_pts, dst_pts)

    def warp(self, img):
        img_size = (img.shape[1], img.shape[0])
        warp = cv2.warpPerspective(img, self.M, img_size, flags=cv2.INTER_LINEAR)
        return warp