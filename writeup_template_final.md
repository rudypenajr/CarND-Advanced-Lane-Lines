##Writeup Template
###You can use this file as a template for your writeup if you want to submit it as a markdown file, but feel free to use some other method and submit a pdf if you prefer.

---

**Advanced Lane Finding Project**

The goals / steps of this project are the following:

* Compute the camera calibration matrix and distortion coefficients given a set of chessboard images.
* Apply a distortion correction to raw images.
* Use color transforms, gradients, etc., to create a thresholded binary image.
* Apply a perspective transform to rectify binary image ("birds-eye view").
* Detect lane pixels and fit to find the lane boundary.
* Determine the curvature of the lane and vehicle position with respect to center.
* Warp the detected lane boundaries back onto the original image.
* Output visual display of the lane boundaries and numerical estimation of lane curvature and vehicle position.

[//]: # (Image References)

[image1]: ./examples/undistort_output.png "Undistorted"
[image2]: ./test_images/test1.jpg "Road Transformed"
[image3]: ./examples/binary_combo_example.jpg "Binary Example"
[image4]: ./examples/warped_straight_lines.jpg "Warp Example"
[image5]: ./examples/color_fit_lines.jpg "Fit Visual"
[image6]: ./examples/example_output.jpg "Output"
[video1]: ./project_video.mp4 "Video"

## [Rubric](https://review.udacity.com/#!/rubrics/571/view) Points
###Here I will consider the rubric points individually and describe how I addressed each point in my implementation.  

---
###Writeup / README

####1. Provide a Writeup / README that includes all the rubric points and how you addressed each one.  You can submit your writeup as markdown or pdf.  [Here](https://github.com/udacity/CarND-Advanced-Lane-Lines/blob/master/writeup_template.md) is a template writeup for this project you can use as a guide and a starting point.  

You're reading it!

### Camera Calibration

#### 1. Briefly state how you computed the camera matrix and distortion coefficients. Provide an example of a distortion corrected calibration image.

===

The code for this step is contained the `codebase/Project 4 - Advanced Lane Finding.ipynb`, cells 2 - 4. 

I computed the camera matrix and distortion coeffients based off what was taught on Lessons 3 - 11. You can see the majority of my notes and teachings being implemented in `Undistort (Lesson 4).ipynb`. 

When it came to the project, I thought it best to move it to a Python Class, which can be found in `codebase/Undistorter.py`. I start off the `__init__` method by searching for appropriate `.npy` files, which is just a binary file holding a saved array. In the case of the `Undistorter.py`, the separate `.npy` files hold the `objpoints`, `imgpoints`, and `shape`, which we need when we `cv2.calibratCamera()`. If those files are not found, then we go into our `find_corners` method which does the following:

* Use `glob` to grab all the images. `glob` is the most approriate for this use case because this module finds all the pathnames matching a specified pattern. In our case, we want all images that start with `calibration*.jpg'.
* Prepare the "object points", which will be the (x, y, z) coordinates of the chessboard corners in the world. Here I am assuming that the chessboard is fixed on the (x, y) place at z=0, such that the object poionts are the same for each calibration image. So `objp` is just a replicated array of cooridnates, and `self.objpoints` will be append with a copy of it every time I successfully detect all chessboard coarners in a trest image.
* Prepare `self.imgpoints` which will be appended with the (x, y) pixel position of each of the corners in the image place with each successful chessboard detection.

Once `find_corners` is completed, we have `self.objpoints`, `self.imgpoints`, and `self.shape`, meaning we can now compute the camera calibration and distortion coefficients using the `cv2.calibrateCamera()` function. 

**Chessboard:**
![Undistorted Chessboard](./output_images/snap_undistorted_chessboard.jpg)

**Straight Lane Lines:**
![Undistorted Chessboard](./output_images/snap_undistorted_straight_lines2.jpg)

The Straight Lane Lines Image is the best example of showing the undistortion of the original image. In the original image, notice that the car (possibly a Fiat) on the left is located roughly at 100 on the x-axis. Undistorting the image moves the car location to near 0 on the x-axis.

---


###Pipeline (single images)

####1. Provide an example of a distortion-corrected image.

I believe I answered this with the previous (1. Briefly state how you computed the camera matrix and distortion coefficients. Provide an example of a distortion corrected calibration image).

--- 

####2. Describe how (and identify where in your code) you used color transforms, gradients or other methods to create a thresholded binary image.  Provide an example of a binary image result.

I used a combination of gradient and color thresholds to generate a binar image (threshold steps are located in `codebase/Project 4 - Advanced Lane Finding.ipynb`, cells 5 - 10. Similar to the calibration step, I made a Python Class for the creation of a binary image, which is located 
at `codebase/GradientThresholder.py`. 

* `codebase/GradientThresholder.py` incorporates a magnitude and direction threshold function. I went about also refactoring majority of the duplicate code, such as `grayscaling` of an image.
* `codebase/GradientThresholder.py` also contains something I found as I was researching color spaces. Mehdi Sqalli had a very good write up on [color thresholding](codebase/GradientThresholder.py). This also helped validate my usage of the HSV color space versus the HLS. Our lesson kind of touched on this but I feel this could be a whole semester to truly understand color spaces and the effects on imagery. 

HSV makes more sense to me in this situation because tt allows us to filter much more easily by focusing on the hue and saturation of the pixel (which color it is and how intense the color is), and not so much on its value (how dark it is), thus handling shadows and overall worse lighting conditions much more easily. So if we want to focus on yellow and/or white lines, HSV allows us that capability.

**Threholding:**
![Thresholding](./output_images/snap_threholding_straight_lines1.png)

--- 

####3. Describe how (and identify where in your code) you performed a perspective transform and provide an example of a transformed image.

The code for my perspective transform includes a function called `warper()`, which appears in lines 1 through 8 in the file `example.py` (output_images/examples/example.py) (or, for example, in the 3rd code cell of the IPython notebook).  The `warper()` function takes as inputs an image (`img`), as well as source (`src`) and destination (`dst`) points.  I chose the hardcode the source and destination points in the following manner:

```
src = np.float32(
    [[(img_size[0] / 2) - 55, img_size[1] / 2 + 100],
    [((img_size[0] / 6) - 10), img_size[1]],
    [(img_size[0] * 5 / 6) + 60, img_size[1]],
    [(img_size[0] / 2 + 55), img_size[1] / 2 + 100]])
dst = np.float32(
    [[(img_size[0] / 4), 0],
    [(img_size[0] / 4), img_size[1]],
    [(img_size[0] * 3 / 4), img_size[1]],
    [(img_size[0] * 3 / 4), 0]])

```
This resulted in the following source and destination points:

| Source        | Destination   | 
|:-------------:|:-------------:| 
| 585, 460      | 320, 0        | 
| 203, 720      | 320, 720      |
| 1127, 720     | 960, 720      |
| 695, 460      | 960, 0        |

I verified that my perspective transform was working as expected by drawing the `src` and `dst` points onto a test image and its warped counterpart to verify that the lines appear parallel in the warped image.

![alt text][image4]

####4. Describe how (and identify where in your code) you identified lane-line pixels and fit their positions with a polynomial?

Then I did some other stuff and fit my lane lines with a 2nd order polynomial kinda like this:

![alt text][image5]

####5. Describe how (and identify where in your code) you calculated the radius of curvature of the lane and the position of the vehicle with respect to center.

I did this in lines # through # in my code in `my_other_file.py`

####6. Provide an example image of your result plotted back down onto the road such that the lane area is identified clearly.

I implemented this step in lines # through # in my code in `yet_another_file.py` in the function `map_lane()`.  Here is an example of my result on a test image:

![alt text][image6]

---

###Pipeline (video)

####1. Provide a link to your final video output.  Your pipeline should perform reasonably well on the entire project video (wobbly lines are ok but no catastrophic failures that would cause the car to drive off the road!).

Here's a [link to my video result](./project_video.mp4)

---

###Discussion

####1. Briefly discuss any problems / issues you faced in your implementation of this project.  Where will your pipeline likely fail?  What could you do to make it more robust?

Here I'll talk about the approach I took, what techniques I used, what worked and why, where the pipeline might fail and how I might improve it if I were going to pursue this project further.  

