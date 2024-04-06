# Standard imports
import numpy as np
import cv2
#import yaml


# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

########################################Blob Detector##############################################
# Setup SimpleBlobDetector parameters.
blobParams = cv2.SimpleBlobDetector_Params()

# Change thresholds
blobParams.minThreshold = 8
blobParams.maxThreshold = 255

# Filter by Area.
blobParams.filterByArea = True
blobParams.minArea = 20500     # minArea may be adjusted to suit for your experiment
blobParams.maxArea = 250000   # maxArea may be adjusted to suit for your experiment

# Filter by Circularity
blobParams.filterByCircularity = True
blobParams.minCircularity = 0.1

# Filter by Convexity
blobParams.filterByConvexity = True
blobParams.minConvexity = 0.87

# Filter by Inertia
blobParams.filterByInertia = True
blobParams.minInertiaRatio = 0.01

# Create a detector with the parameters
blobDetector = cv2.SimpleBlobDetector_create(blobParams)


###################################################################################################
# Original blob coordinates, supposing all blobs are of z-coordinates 0
# And, the distance between every two neighbour blob circle centers is 72 centimetres
# In fact, any number can be used to replace 72.
# Namely, the real size of the circle is pointless while calculating camera calibration parameters.
objp = np.zeros((49, 3), np.float32)
objp[0]  = (40  , 40  , 0)
objp[1]  = (40  , 80 , 0)
objp[2]  = (40  , 120, 0)
objp[3]  = (40  , 160, 0)
objp[4]  = (40 , 200, 0)
objp[5]  = (40 , 240, 0)
objp[6]  = (40 , 280, 0)
objp[7]  = (80 , 40, 0)
objp[8]  = (80 , 80, 0)
objp[9]  = (80 , 120, 0)
objp[10] = (80 , 160, 0)
objp[11] = (80 , 200, 0)
objp[12] = (80, 240,  0)
objp[13] = (80, 280, 0)
objp[14] = (120, 40, 0)
objp[15] = (120, 80, 0)
objp[16] = (120, 120, 0)
objp[17] = (120, 160, 0)
objp[18] = (120, 200, 0)
objp[19] = (120, 240, 0)
objp[20] = (120, 280, 0)
objp[21] = (160, 40, 0)
objp[22] = (160, 80, 0)
objp[23] = (160, 120, 0)
objp[24] = (160, 160, 0)
objp[25] = (160, 200, 0)
objp[26] = (160, 240, 0)
objp[27] = (160, 280, 0)
objp[28] = (200, 40, 0)
objp[29] = (200, 80, 0)
objp[30] = (200, 120, 0)
objp[31] = (200, 160, 0)
objp[32] = (200, 200, 0)
objp[33] = (200, 240, 0)
objp[34] = (200, 280, 0)
objp[35] = (240, 40, 0)
objp[36] = (240, 80, 0)
objp[37] = (240, 120, 0)
objp[38] = (240, 160, 0)
objp[39] = (240, 200, 0)
objp[40] = (240, 240, 0)
objp[41] = (240, 280, 0)
objp[42] = (280, 40, 0)
objp[43] = (280, 80, 0)
objp[44] = (280, 120, 0)
objp[45] = (280, 160, 0)
objp[46] = (280, 200, 0)
objp[47] = (280, 240, 0)
objp[48] = (280, 280, 0)
###################################################################################################
objpoints = [] # 3d point in real world sp
imgpoints = [] # 2d points in image plane.





img  = cv2.imread('circles_grid.bmp')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

keypoints = blobDetector.detect(gray) # Detect blobs.

 # Draw detected blobs as red circles. This helps cv2.findCirclesGrid() . 
im_with_keypoints = cv2.drawKeypoints(img, keypoints, np.array([]), (0,255,0), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
im_with_keypoints_gray = cv2.cvtColor(im_with_keypoints, cv2.COLOR_BGR2GRAY)
ret, corners = cv2.findCirclesGrid(im_with_keypoints, (7,7), flags = cv2.CALIB_CB_SYMMETRIC_GRID, blobDetector=blobDetector)   #Find the circle grid

if ret == True:
    objpoints.append(objp)  # Certainly, every loop objp is the same, in 3D.

    corners2 = cv2.cornerSubPix(im_with_keypoints_gray, corners, (11,11), (-1,-1), criteria)    # Refines the corner locations.
    imgpoints.append(corners2)

    # Draw and display the corners.
    im_with_keypoints = cv2.drawChessboardCorners(img, (7,7), corners2, ret)

    # Enable the following 2 lines if you want to save the calibration images.
    # filename = str(found) +".jpg"
    # cv2.imwrite(filename, im_with_keypoints)

    


    #cv2.imshow("img", im_with_keypoints) # display
    #cv2.waitKey(2)





ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)


#  Python code to write the image (OpenCV 3.2)
fs = cv2.FileStorage('calibration.yml', cv2.FILE_STORAGE_WRITE)
fs.write('camera_matrix', mtx)
fs.write('dist_coeff', dist)
fs.release()



img = cv2.imread('80S Sample.bmp')
h,  w = img.shape[:2]
newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))



# undistort
mapx, mapy = cv2.initUndistortRectifyMap(mtx, dist, None, newcameramtx, (w,h), 5)
dst = cv2.remap(img, mapx, mapy, cv2.INTER_LINEAR)
# crop the image
x, y, w, h = roi
dst = dst[y:y+h, x:x+w]
cv2.imwrite('calibresult.png', dst)


cv2.namedWindow('img', cv2.WINDOW_NORMAL)
cv2.imshow('img', img)
cv2.resizeWindow('img', 800, 600)

cv2.namedWindow('cal', cv2.WINDOW_NORMAL)
cv2.imshow('cal', dst)
cv2.resizeWindow('cal', 800, 600)
cv2.waitKey(0)


# If you want to use PyYAML to read and write yaml files,
# try the following part
# It's very important to transform the matrix to list.
# data = {'camera_matrix': np.asarray(mtx).tolist(), 'dist_coeff': np.asarray(dist).tolist()}

# with open("calibration.yaml", "w") as f:
#    yaml.dump(data, f)

# You can use the following 4 lines of code to load the data in file "calibration.yaml"
# Read YAML file
#with open(calibrationFile, 'r') as stream:
#    dictionary = yaml.safe_load(stream)
#camera_matrix = dictionary.get("camera_matrix")
#dist_coeffs = dictionary.get("dist_coeff")