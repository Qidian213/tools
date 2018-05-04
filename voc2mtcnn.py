import xml.etree.ElementTree as ET
import pickle
import os
from os import listdir, getcwd
from os.path import join
import numpy as np

sets=[('2012', 'train'), ('2012', 'val'), ('2007', 'train'), ('2007', 'val'), ('2007', 'test')]

classes = ["person"]

# main
wd = getcwd()

for year, image_set in sets:
    if not os.path.exists('VOCdevkit/VOC%s/labels/'%(year)):
        os.makedirs('VOCdevkit/VOC%s/labels/'%(year))
    image_ids = open('VOCdevkit/VOC%s/ImageSets/Main/%s.txt'%(year, image_set)).read().strip().split()
    list_file = open('%s_%s.txt'%(year, image_set), 'w')
    for image_id in image_ids:
        in_file = open('VOCdevkit/VOC%s/Annotations/%s.xml'%(year, image_id))
        tree=ET.parse(in_file)
        root = tree.getroot()
        size = root.find('size')
        w = int(size.find('width').text)
        h = int(size.find('height').text)
        found_list = []
        num  = 0
        for obj in root.iter('object'):
            difficult = obj.find('difficult').text
            cls = obj.find('name').text
            if cls not in classes or int(difficult) == 1:
                continue
            xmlbox = obj.find('bndbox')
            b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))
#            x = b[0]
#            y = b[2]
#            w = b[1] - b[0]
#            h = b[3] - b[2]
#            num = num+1
#            found_list.append([x,y,w,h])
#            
            xmin = b[0]
            ymin = b[2]
            xmax = b[1]
            ymax = b[3]
            num = num+1
            found_list.append([xmin,ymin,xmax,ymax])
            
        if num != 0:
            list_file.write(str('VOC%s/JPEGImages/%s '%(year, image_id)))
            for i in range(0,num):
                list_file.write(str(found_list[i][0]) + ' '+str(found_list[i][1]) + ' '+str(found_list[i][2]) + ' '+str(found_list[i][3]) + ' ')
            list_file.write('\n')
#            list_file.write(str('VOC%s/JPEGImages/%s.jpg\n'%(year, image_id)) + str(num)+'\n') #+str(found_list) +'\n')
#            for i in range(0,num):
#                list_file.write(str(found_list[i][0]) + ' '+str(found_list[i][1]) + ' '+str(found_list[i][2]) + ' '+str(found_list[i][3]) + '\n')

    list_file.close()
os.system("cat 2007_test.txt 2007_train.txt 2007_val.txt 2012_train.txt 2012_val.txt > train.txt")

