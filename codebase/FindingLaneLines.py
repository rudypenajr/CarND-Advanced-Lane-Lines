import numpy as np
import cv2
import matplotlib.pyplot as plt

class FindingLaneLines:
    def __init__(self):
        self.left_fit = None
        self.right_fit = None
        self.nwindows = 9
        self.margin = 100
        self.minpix = 50

    def histogram(self, img):
        # Take a histogram of the bottom half of the image
        histogram = np.sum(img[int(img.shape[0] / 2):, :], axis=0)
        return histogram

    def find_peaks(self, histogram):
        midpoint = np.int(histogram.shape[0] / 2)
        leftx_base = np.argmax(histogram[:midpoint])
        rightx_base = np.argmax(histogram[midpoint:]) + midpoint

        return midpoint, leftx_base, rightx_base

    def out_img(self, img):
        return np.dstack((img, img, img))*255

    def nonzeros(self, img):
        nonzero = img.nonzero()
        nonzeroy = np.array(nonzero[0])
        nonzerox = np.array(nonzero[1])

        return nonzero, nonzeroy, nonzerox

    def detect_lane_lines(self, img):
        histogram = self.histogram(img)

        # Output Image
        out_img = self.out_img(img)

        # Find the peak of the left and right halves of the histogram
        # These will be the starting point for the left and right lines
        midpoint, leftx_base, rightx_base = self.find_peaks(histogram)

        # Set height of windows
        window_height = np.int(img.shape[0] / self.nwindows)

        # Identify the x and y positions of all nonzero pixels in the image
        nonzero, nonzeroy, nonzerox = self.nonzeros(img)

        # Current positions to be updated for each window
        leftx_current = leftx_base
        rightx_current = rightx_base

        # Create empty lists to receive left and right lane pixel indeces
        left_lane_inds = []
        right_lane_inds = []

        # Step through the windows one by one
        for window in range(self.nwindows):
            # Identify window boundaries in x and y (and right and left)
            win_y_low = img.shape[0] - (window + 1) * window_height
            win_y_high = img.shape[0] - window * window_height
            win_xleft_low = leftx_current - self.margin
            win_xleft_high = leftx_current + self.margin
            win_xright_low = rightx_current - self.margin
            win_xright_high = rightx_current + self.margin

            # Draw the windows on the visualization image
            cv2.rectangle(out_img, (win_xleft_low, win_y_low), (win_xleft_high, win_y_high), (0, 255, 0), 2)
            cv2.rectangle(out_img, (win_xright_low, win_y_low), (win_xright_high, win_y_high), (0, 255, 0), 2)

            # Identify the nonzero pixels in x and y within the window
            good_left_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) & (nonzerox >= win_xleft_low) & (
            nonzerox < win_xleft_high)).nonzero()[0]
            good_right_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) & (nonzerox >= win_xright_low) & (
            nonzerox < win_xright_high)).nonzero()[0]

            # Append these indices to the lists
            left_lane_inds.append(good_left_inds)
            right_lane_inds.append(good_right_inds)

            # If you found > minpix pixels, recenter next window on their mean position
            if len(good_left_inds) > self.minpix:
                leftx_current = np.int(np.mean(nonzerox[good_left_inds]))
            if len(good_right_inds) > self.minpix:
                rightx_current = np.int(np.mean(nonzerox[good_right_inds]))

        # Concatenate the arrays of indices
        left_lane_inds = np.concatenate(left_lane_inds)
        right_lane_inds = np.concatenate(right_lane_inds)

        # Extract left and right line pixel positions
        leftx = nonzerox[left_lane_inds]
        lefty = nonzeroy[left_lane_inds]
        rightx = nonzerox[right_lane_inds]
        righty = nonzeroy[right_lane_inds]

        # Fit a second order polynomial to each
        self.left_fit = np.polyfit(lefty, leftx, 2)
        self.right_fit = np.polyfit(righty, rightx, 2)

        return left_lane_inds, right_lane_inds, self.left_fit, self.right_fit

    def measure_curvature(self, image):
        left_fit = self.left_fit
        right_fit = self.right_fit

        ym_per_pix = 30 / 720  # meters per pixel in y dimension
        xm_per_pix = 3.7 / 700  # meters per pixel in x dimension

        height = image.shape[0]
        width = image.shape[1]

        # Generate some fake data to represent lane-line pixels
        ploty = np.linspace(0, height-1, height)
        y_eval = np.max(ploty)

        # For each y position generate random x position within +/-50 pix
        # of the line base position in each case (x=200 for left, and x=900 for right)
        leftx = left_fit[0] * ploty ** 2 + left_fit[1] * ploty + left_fit[2]
        rightx = right_fit[0] * ploty ** 2 + right_fit[1] * ploty + right_fit[2]

        # leftx = leftx[::-1]  # Reverse to match top-to-bottom in y
        # rightx = rightx[::-1]  # Reverse to match top-to-bottom in y

        # Fit a second order polynomial to pixel positions in each fake lane line
        left_fit = np.polyfit(ploty, leftx, 2)
        left_fitx = left_fit[0] * ploty ** 2 + left_fit[1] * ploty + left_fit[2]
        right_fit = np.polyfit(ploty, rightx, 2)
        right_fitx = right_fit[0] * ploty ** 2 + right_fit[1] * ploty + right_fit[2]

        return leftx, rightx, left_fitx, right_fitx