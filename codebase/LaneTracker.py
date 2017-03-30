from Undistorter import Undistorter
from GradientThresholder import GradientThresholder
from PerspectiveTransform import PerspectiveTransform
from FindingLaneLines import FindingLaneLines
from LaneDrawer import LaneDrawer

class LaneTracker():
	def __init__(self):
		self.undistorter = Undistorter()
		self.gradientThresholder = GradientThresholder()
		self.perspectiveTransform = PerspectiveTransform()
		self.findingLaneLines = FindingLaneLines()
		self.laneDrawer = LaneDrawer()

	def process(self, img):
		# Step 1: Undistort the image to remove camera and lens distortion (Cell 2)
		undistorted_img = self.undistorter.undistort(img)

		# Step 2: Threshold the image to help find lane lines
		threshold_img = self.gradientThresholder.combined_threshold(undistorted_img)

		# Step 3: Perspective Transformation to rectify binary image ("birds-eye view")
		warped_img = self.perspectiveTransform.warp(threshold_img)

		# Step 4: Detect lane pixels and fit to find the lane boundary
        # left_lane_inds, right_lane_inds, left_fit, right_fit = self.findingLaneLines.detect_lane_lines(warped_img)
		left_lane_inds, right_lane_inds, left_fit, right_fit = self.findingLaneLines.detect_lane_lines(warped_img)

		# Get Left and Right Lane Curvature + Car Offset
        # Step 5: Calculate radius of curvature of the lane and position of the vehicle in respect to center
        # leftx, rightx, left_fitx, right_fitx = self.findingLaneLines.measure_curvature(warped_img)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     car_offset = self.findingLaneLines.get_car_offset(warped_img)
		left_curverad, right_curverad = self.findingLaneLines.get_curvature(warped_img)
		car_offset = self.findingLaneLines.get_car_offset(warped_img)

		# Plot the detected lanes on image
		plotted_img = self.laneDrawer.plotPolygon(img, left_fit, right_fit, self.perspectiveTransform.Minv)
		left_curve_str = "Left ROC: "+str(round(left_curverad,0))+"m"
		right_curve_str = "Right ROC: "+str(round(right_curverad,0))+"m"
		car_offset_str = "Car Offset:"+str(round(car_offset,3))+"m"

		#Overlay text
		text_img = self.laneDrawer.textOverLay(plotted_img,left_curve_str,pos=(100,100))
		text_img = self.laneDrawer.textOverLay(text_img,right_curve_str,pos=(100,150))
		text_img = self.laneDrawer.textOverLay(text_img,car_offset_str,pos=(100,200))
		return plotted_img