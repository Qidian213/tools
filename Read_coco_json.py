import os
import pycocotools.coco as coco
import json
import numpy as np
import cv2
import shutil

# fp = open('Train_head.json', 'r')
# data = json.load(fp)
# images = data['images']

# for img in images:
    # img_path = img['file_name']
    # print(img_path)
    # img = cv2.imread(img_path)
    # height, width = img.shape[0], img.shape[1]
    
coco_data = coco.COCO('Val_head.json')
images = coco_data.getImgIds()
for img_id in images[0:10]:
    file_name = coco_data.loadImgs(ids=[img_id])[0]['file_name']
    ann_ids   = coco_data.getAnnIds(imgIds=[img_id])
    anns      = coco_data.loadAnns(ids=ann_ids)

    img_path = file_name
    image = cv2.imread(img_path)

    for ann in anns:
        action_id = ann['category_id']
        box = ann['bbox']
        cv2.rectangle(image, (int(box[0]), int(box[1]), int(box[2]), int(box[3])), [0,255,0], 2, 16)
        cv2.putText(image, str(action_id), (int(box[0]), int(box[1])), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
    cv2.imwrite("Ann_vis/"+file_name.split('/')[1], image)
