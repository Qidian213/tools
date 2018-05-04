import xml.etree.ElementTree as ET
import pickle
import os
from os import listdir, getcwd
from os.path import join
import numpy as np

sets=[('HollywoodHeads', 'train'),('HollywoodHeads', 'val'), ('HollywoodHeads', 'test')]
sets2=[('SCUT_HEAD_Part_A', 'val'), ('SCUT_HEAD_Part_A', 'test'),('SCUT_HEAD_Part_A', 'train'), ('SCUT_HEAD_Part_B', 'val'), ('SCUT_HEAD_Part_B', 'test'),('SCUT_HEAD_Part_B', 'train')]

classes = ["person","head"]

# main
wd = getcwd()
num =0 
for year, image_set in sets:
    image_ids = open('%s/Splits/%s.txt'%(year, image_set)).read().strip().split()
    list_file = open('%s_%s.txt'%(year[:5], image_set), 'w')
    #for image_id in image_ids:
    for i in range(0,len(image_ids)//100):
        num = i*100
        image_id = image_ids[num]
        in_file = open('%s/Annotations/%s.xml'%(year, image_id))
        tree=ET.parse(in_file)
        root = tree.getroot()
        print(image_id)
        found_list = []
        num  = 0
        for obj in root.iter('object'):
            difficult = obj.find('difficult').text
            
            cls = obj.find('name').text
            if cls not in classes or int(difficult) == 1:
                continue
            xmlbox = obj.find('bndbox')
            b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))

            xmin = b[0]
            ymin = b[2]
            xmax = b[1]
            ymax = b[3]
            num = num+1
            found_list.append([xmin,ymin,xmax,ymax])

        if num != 0:
            list_file.write(str('%s/JPEGImages/%s '%(year, image_id)))
            for i in range(0,num):
                list_file.write(str(found_list[i][0]) + ' '+str(found_list[i][1]) + ' '+str(found_list[i][2]) + ' '+str(found_list[i][3]) + ' ')
            list_file.write('\n')
    list_file.close()
    
for year, image_set in sets2:
    image_ids = open('%s/ImageSets/Main/%s.txt'%(year, image_set)).read().strip().split()
    list_file = open('%s_%s.txt'%(year, image_set), 'w')
    for image_id in image_ids:
        in_file = open('%s/Annotations/%s.xml'%(year, image_id))
        tree=ET.parse(in_file)
        root = tree.getroot()
        print(image_id)
        found_list = []
        num  = 0
        for obj in root.iter('object'):
            difficult = obj.find('difficult').text
            
            cls = obj.find('name').text
            if cls not in classes or int(difficult) == 1:
                continue
            xmlbox = obj.find('bndbox')
            b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))

            xmin = b[0]
            ymin = b[2]
            xmax = b[1]
            ymax = b[3]
            num = num+1
            found_list.append([xmin,ymin,xmax,ymax])

        if num != 0:
            list_file.write(str('%s/JPEGImages/%s '%(year, image_id)))
            for i in range(0,num):
                list_file.write(str(found_list[i][0]) + ' '+str(found_list[i][1]) + ' '+str(found_list[i][2]) + ' '+str(found_list[i][3]) + ' ')
            list_file.write('\n')

os.system("cat Holly_test.txt Holly_train.txt Holly_val.txt SCUT_HEAD_Part_A_test.txt SCUT_HEAD_Part_A_train.txt SCUT_HEAD_Part_A_val.txt SCUT_HEAD_Part_B_test.txt SCUT_HEAD_Part_B_train.txt SCUT_HEAD_Part_B_val.txt> train.txt")

