# -*- coding:utf-8 -*-
# !/usr/bin/env python
import os
import xml.dom.minidom as xmldom
import numpy as np
import glob
from PIL import Image
import json
import random

class xml2coco(object):
    def __init__(self,labelme_json=[], save_json_path='./new.json'):
        '''
        :param labelme_json: 所有labelme的json文件路径组成的列表
        :param save_json_path: json保存位置
        '''
        self.labelme_json=labelme_json
        self.save_json_path=save_json_path
        self.images=[]
        self.categories = [{'supercategory': 'mask', 'id': 1, 'name': 'crazing'},
                           {'supercategory': 'mask', 'id': 2, 'name': 'inclusion'},
                           {'supercategory': 'mask', 'id': 3, 'name': 'patches'},
                           {'supercategory': 'mask', 'id': 4, 'name': 'pitted_surface'},
                           {'supercategory': 'mask', 'id': 5, 'name': 'rolled-in_scale'},
                           {'supercategory': 'mask', 'id': 6, 'name': 'scratches'}]
        self.annotations=[]
        self.label=[]
        self.annID=1
        self.imgID=1
        self.height=0
        self.width=0
        self.save_json()

    def data_transfer(self):
        for num,xmlfile in enumerate(self.labelme_json):
            DomTree = xmldom.parse(xmlfile)
            annotation = DomTree.documentElement 
            self.images.append(self.image(annotation,num))
            
            objectlist = annotation.getElementsByTagName('object')
            
            for objects in objectlist:
                namelist = objects.getElementsByTagName('name')
                label = (namelist[0].childNodes[0].data)#.encode('unicode-escape').decode('string_escape')
                
                bndbox = objects.getElementsByTagName('bndbox')
                if(len(bndbox) >0):
                    self.annotations.append(self.annotation(bndbox,label,num))
                    self.annID += 1
                    
    def image(self,annotation,num):
        image={}
        
        widthlist = annotation.getElementsByTagName('width')
        heightlist = annotation.getElementsByTagName('height')
        filenamelist = annotation.getElementsByTagName('filename')
        
        filename = (filenamelist[0].childNodes[0].data)#.encode('unicode-escape').decode('string_escape')
        width = int(widthlist[0].childNodes[0].data)
        height = int(heightlist[0].childNodes[0].data)

        if('.jpg' not in filename):
            filename = filename + '.jpg'
        image['file_name'] = filename
        image['height']=height
        image['width'] = width
        image['id']=num+1
        
        self.height=height
        self.width=width

        return image

    def annotation(self,bndbox,label,num):
        annotation={}
        for box in bndbox: 
            x1_list = box.getElementsByTagName('xmin')
            x1 = int(x1_list[0].childNodes[0].data)
            y1_list = box.getElementsByTagName('ymin')
            y1 = int(y1_list[0].childNodes[0].data)
            x2_list = box.getElementsByTagName('xmax')
            x2 = int(x2_list[0].childNodes[0].data)
            y2_list = box.getElementsByTagName('ymax')
            y2 = int(y2_list[0].childNodes[0].data)
            
            w = x2 - x1
            h = y2 - y1
            annotation['bbox'] = [x1,y1,w,h]
                
        annotation['segmentation']= None
        annotation['area'] = annotation['bbox'][2]*annotation['bbox'][3]
        annotation['iscrowd'] = 0
        annotation['image_id'] = num+1
        
        annotation['category_id'] = self.getcatid(label)
        annotation['id'] = self.annID
        return annotation

    def getcatid(self,label):
        for categorie in self.categories:
            if label==categorie['name']:
                return categorie['id']
        return -1

    def data2coco(self):
        data_coco={}
        data_coco['images']=self.images
        data_coco['categories']=self.categories
        data_coco['annotations']=self.annotations
        print("Num categories: %s" % len(self.categories))
        print("Num images: %s" % len(self.images))
        print("Num annotations: %s" % len(self.annotations))
        return data_coco

    def save_json(self):
        self.data_transfer()
        self.data_coco = self.data2coco()
        json.dump(self.data_coco, open(self.save_json_path, 'w'), indent=4)  # indent=4 更加美观显示

xml_files = glob.glob('IMAGES/*.xml')
save_json_train = 'netu_train.json'
random.shuffle(xml_files)

xml2coco(xml_files,save_json_train)
