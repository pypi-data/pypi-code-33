import numpy as np
import cv2 as cv
 
img = np.zeros((500,500,3), np.uint8)
 
#draw a red line
img = cv.line(img, (100,100), (300,300), (0,0,255),4)
img = cv.ellipse(img, (300, 450), (100, 50), 45, 130, 270, (255,255,255), 1)





vrx = np.array(([20,80],[60,50],[100.80],[80,120],[40,120]]), np.int32)
vrx = vrx.reshape((-1,1,2))
img = cv.polylines(img, [vrx], True, (0,255,255),3)
 
cv.imshow('Draw01',img)
cv.waitKey(0)