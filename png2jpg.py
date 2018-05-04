# -*- coding:utf-8 -*-
# !/usr/bin/env python
import glob
import cv2
import numpy as np

rgb_list=glob.glob('./*.png')
print(rgb_list)
for rgb_str in rgb_list:
    image = cv2.imread(rgb_str)  
    cv2.imwrite("./rgb_"+rgb_str[6:-4]+".jpg",image) 
