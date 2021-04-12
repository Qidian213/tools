import pycocotools.coco as coco
import json
import numpy as np
import cv2
import shutil

images_coco =[]
annotations =[]

img_num     = 0
ann_num     = 0

coco_data   = coco.COCO('DarkFace_Train_Light/DarkFace_Train.json')
categories  = coco_data.dataset['categories']

print(categories)
images = coco_data.getImgIds()
for img_id in images:
    img_num  += 1
    img_info  = coco_data.loadImgs(ids=[img_id])[0]
    ann_ids   = coco_data.getAnnIds(imgIds=[img_id])
    img_anns  = coco_data.loadAnns(ids=ann_ids)

    img_info['id'] = img_num
    img_info['file_name'] = img_info['file_name']
    images_coco.append(img_info)
    
    for ann in img_anns:
        ann['image_id'] = img_num
        ann['id']       = ann_num
        ann_num        += 1
        annotations.append(ann)

coco_data   = coco.COCO('DarkFace_Train_Light/WidFace_Train2.json')
images = coco_data.getImgIds()
for img_id in images:
    img_num  += 1
    img_info  = coco_data.loadImgs(ids=[img_id])[0]
    ann_ids   = coco_data.getAnnIds(imgIds=[img_id])
    img_anns  = coco_data.loadAnns(ids=ann_ids)

    img_info['id'] = img_num
    img_info['file_name'] = img_info['file_name']
    images_coco.append(img_info)
    
    for ann in img_anns:
        ann['image_id'] = img_num
        ann['id']       = ann_num
        ann_num        += 1
        annotations.append(ann)

data_coco={}
data_coco['images']     = images_coco
data_coco['categories'] = categories
data_coco['annotations']= annotations

json.dump(data_coco, open('DarkFace_Train_Light/DarkFace_WideFace_Train.json', 'w'), indent=4)
