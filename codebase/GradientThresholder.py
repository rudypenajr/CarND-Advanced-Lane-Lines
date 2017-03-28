import cv2
import numpy as np

class GradientThresholder:
    def __init__(self):
        self.sobel_kernel = 3
        self.thresh_direction_min = 0.7
        self.thresh_direction_max = 1.3
        self.thresh_magnitude_min = 20
        self.thresh_magnitude_max = 100

    def sobel_x_y(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=self.sobel_kernel)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=self.sobel_kernel)

        return sobelx, sobely

    def magnitude_threshold(self, sobelx, sobely):
        # Calculate the gradient magnitude
        gradmag = np.sqrt(sobelx ** 2 + sobely ** 2)

        # Rescale to 8 bit
        scale_factor = np.max(gradmag) / 255
        gradmag = (gradmag / scale_factor).astype(np.uint8)

        # Create a binary image of ones where threshold is met, zeros otherwise
        binary_output = np.zeros_like(gradmag)
        binary_output[(gradmag >= self.thresh_magnitude_min) & (gradmag <= self.thresh_magnitude_min)] = 1

        # Return the binary image
        return binary_output

    def direction_threshold(self, sobelx, sobely):
        # 3. Take the absolute value of the x and y gradients
        # gradmag = np.sqrt(sobelx**2 + sobely**2)
        abs_sobelx = np.abs(sobelx)
        abs_sobely = np.abs(sobely)

        # 4. Calculate the direction of the gradient
        absgraddir = np.arctan2(abs_sobely, abs_sobelx)

        # 5. Create a binary mask where direction thresholds are met
        binary_output = np.zeros_like(absgraddir)
        binary_output[(absgraddir >= self.thresh_direction_min) & (absgraddir <= self.thresh_direction_max)] = 1

        return binary_output

    def hsv_color_threshold(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

        yellow_hsv_low = np.array([15, 100, 120], np.uint8)
        yellow_hsv_high = np.array([80, 255, 255], np.uint8)
        yellow_mask = cv2.inRange(img, yellow_hsv_low, yellow_hsv_high)

        white_hsv_low = np.array([0, 0, 200], np.uint8)
        white_hsv_high = np.array([255, 30, 255], np.uint8)
        white_mask = cv2.inRange(img, white_hsv_low, white_hsv_high)

        binary_output = np.zeros_like(img[:, :, 0])
        binary_output[((yellow_mask != 0) | (white_mask != 0))] = 1

        return binary_output


    def combined_threshold(self, img):
        # 1. Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

        # gradx = self.abs_sobel_thresh(img, orient='x')
        # grady = self.abs_sobel_thresh(img, orient='y')
        # sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=self.sobel_kernel)
        # sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=self.sobel_kernel)
        sobelx, sobely = self.sobel_x_y(img)

        magnitude_binary = self.magnitude_threshold(sobelx, sobely)
        direction_binary = self.direction_threshold(sobelx, sobely)

        color_binary = self.hsv_color_threshold(img)

        combined = np.zeros_like(direction_binary)
        combined[((color_binary == 1) & ((magnitude_binary ==1) | (direction_binary== 1)))] = 1
        # combined[((color_img == 1) & ((mag_img == 1) | (dir_img == 1)))] = 1

        return combined