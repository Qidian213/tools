import pycocotools.coco as coco
import json
import numpy as np
import cv2
import shutil
import random

train_images_coco =[]
train_annotations =[]

val_images_coco =[]
val_annotations =[]

img_num     = 0
ann_num     = 0

coco_data   = coco.COCO('Train_head_bk.json')
categories  = coco_data.dataset['categories']

print(categories)
images = coco_data.getImgIds()
for img_id in images:
    img_num  += 1
    img_info  = coco_data.loadImgs(ids=[img_id])[0]
    ann_ids   = coco_data.getAnnIds(imgIds=[img_id])
    img_anns  = coco_data.loadAnns(ids=ann_ids)

    if('PartA' in img_info['file_name']):
        continue
        
    if(random.uniform(0, 1) < 0.9):
        img_info['id']        = img_num
        img_info['file_name'] = img_info['file_name']
        
        train_images_coco.append(img_info)
        
        for ann in img_anns:
            ann['image_id'] = img_num
            ann['id']       = ann_num
            ann_num        += 1
            train_annotations.append(ann)
    else:
        img_info['id']        = img_num
        img_info['file_name'] = img_info['file_name']
        
        val_images_coco.append(img_info)
        
        for ann in img_anns:
            ann['image_id'] = img_num
            ann['id']       = ann_num
            ann_num        += 1
            val_annotations.append(ann)

coco_data   = coco.COCO('Val_head_bk.json')
images = coco_data.getImgIds()
for img_id in images:
    img_num  += 1
    img_info  = coco_data.loadImgs(ids=[img_id])[0]
    ann_ids   = coco_data.getAnnIds(imgIds=[img_id])
    img_anns  = coco_data.loadAnns(ids=ann_ids)

    if('PartA' in img_info['file_name']):
        continue
        
    if(random.uniform(0, 1) < 0.9):
        img_info['id']        = img_num
        img_info['file_name'] = img_info['file_name']
        
        train_images_coco.append(img_info)
        
        for ann in img_anns:
            ann['image_id'] = img_num
            ann['id']       = ann_num
            ann_num        += 1
            train_annotations.append(ann)
    else:
        img_info['id']        = img_num
        img_info['file_name'] = img_info['file_name']
        
        val_images_coco.append(img_info)
        
        for ann in img_anns:
            ann['image_id'] = img_num
            ann['id']       = ann_num
            ann_num        += 1
            val_annotations.append(ann)

train_data_coco={}
train_data_coco['images']     = train_images_coco
train_data_coco['categories'] = categories
train_data_coco['annotations']= train_annotations
json.dump(train_data_coco, open('Train_head.json', 'w'), indent=4)

val_data_coco={}
val_data_coco['images']     = val_images_coco
val_data_coco['categories'] = categories
val_data_coco['annotations']= val_annotations
json.dump(val_data_coco, open('Val_head.json', 'w'), indent=4)
