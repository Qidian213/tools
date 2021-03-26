# -*- coding:utf-8 -*-
# !/usr/bin/env python

import argparse
import json
import matplotlib.pyplot as plt
import skimage.io as io
import cv2
import numpy as np
import glob
import PIL.Image
from shapely.geometry import Polygon

class labelme2coco(object):
    def __init__(self,labelme_json,save_json_path='./new.json'):
        self.labelme_json  =labelme_json
        self.save_json_path=save_json_path
        self.images=[]
        self.categories  = [{'supercategory': 'face', 'id': 1, 'name': 'face'}]
        self.annotations = []
        self.label=[]
        self.annID=1
        self.height=0
        self.width=0

        self.save_json()

    def data_transfer(self):
        with open(self.labelme_json,'r') as fp:
            data = json.load(fp)
            for num, key in enumerate(data.keys()):
                anns = data[key]
                
                self.images.append(self.image(anns, num, key))
                
                for box in anns['boxs']:
                    self.annotations.append(self.annotation(box,'face',num))
                    self.annID+=1
        print(self.categories)

    def image(self,data, num, file_name):
        image={}
        image['height']    = data['height']
        image['width']     = data['width']
        image['id']        = num+1
        image['file_name'] = file_name

        return image

    def categorie(self,label):
        categorie={}
        categorie['supercategory'] = label
        categorie['id']   = len(self.label)+1 
        categorie['name'] = label
        return categorie

    def annotation(self, box, label, num):
        annotation={}
        annotation['area']     = (box[2]-box[0])*(box[3]-box[1])
        annotation['iscrowd']  = 0
        annotation['image_id'] = num+1
        annotation['bbox']     = [box[0], box[1], box[2]-box[0], box[3]-box[1]]

        annotation['category_id'] = self.getcatid(label)
        annotation['id']          = self.annID
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
        return data_coco

    def save_json(self):
        self.data_transfer()
        self.data_coco = self.data2coco()

        json.dump(self.data_coco, open(self.save_json_path, 'w'), indent=4) 

labelme_json='DarkFace_Train.json'

labelme2coco(labelme_json, './DarkFace_Train_COCO.json')
