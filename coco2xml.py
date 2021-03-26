import os
import xml.etree.ElementTree as ET
import pandas as pd
import cv2
import json
import random 

def randrf(low, high):
    return random.uniform(0, 1) * (high - low) + low
    
def write_to_xml(image_name, image_dict, data_folder, save_folder, xml_template='XML_Template.xml'):
    # get bboxes
    bboxes = image_dict[image_name]
    
    # read xml file
    tree = ET.parse(xml_template)
    root = tree.getroot()    
    
    # modify
    folder = root.find('folder')
    folder.text = 'darkface'
    
    fname = root.find('filename')
    fname.text = image_name 

    path = root.find('path')
    path.text = 'Images/darkface/' +  image_name
    
    src = root.find('source')
    database = src.find('database')
    database.text = 'DaekFace'
    
    # size
    img = cv2.imread(os.path.join(data_folder, image_name))
    h,w,d = img.shape
    
    size  = root.find('size')
    width = size.find('width')
    width.text  = str(w)
    height      = size.find('height')
    height.text = str(h)
    depth = size.find('depth')
    depth.text = str(d)
    
    for box in bboxes:
        # append object
        obj = ET.SubElement(root, 'object')
        
        name = ET.SubElement(obj, 'name')
        name.text = box[0]
        
        pose = ET.SubElement(obj, 'pose')
        pose.text = 'Unspecified'

        truncated = ET.SubElement(obj, 'truncated')
        truncated.text = str(0)

        difficult = ET.SubElement(obj, 'difficult')
        difficult.text = str(0)

        bndbox = ET.SubElement(obj, 'bndbox')
        
        xmin = ET.SubElement(bndbox, 'xmin')
        xmin.text = str(int(box[1]))
        
        ymin = ET.SubElement(bndbox, 'ymin')
        ymin.text = str(int(box[2]))
        
        xmax = ET.SubElement(bndbox, 'xmax')
        xmax.text = str(int(box[3]))
        
        ymax = ET.SubElement(bndbox, 'ymax')
        ymax.text = str(int(box[4]))
    
    # save .xml to anno_path
    anno_path = os.path.join(save_folder, image_name.split('.')[0] + '.xml')
    print(anno_path)
    tree.write(anno_path)
    
# main routine
if __name__=='__main__':
    # read annotations file
    annotations_path = 'DarkFace_Train_COCO.json'
    
    # specify image locations
    image_folder = 'Image_MSRCR'
    
    # specify savepath - where to save .xml files
    savepath = 'Annotations_MSRCR'
    if not os.path.exists(savepath):
        os.makedirs(savepath)
    
    # read in .json format
    with open(annotations_path,'rb') as file:
        doc = json.load(file)
        
    # get annotations
    annotations = doc['annotations']
    images = doc['images']
    id2names = {}
    for name_dt in images:
        id2names[name_dt['id']] = name_dt['file_name']
    
    # iscrowd allowed? 1 for ok, else set to 0
    iscrowd_allowed = 1
    
    # initialize dict to store bboxes for each image
    image_dict = {}
    # loop through the annotations in the subset
    for anno in annotations:
        # get annotation for image name
        image_id = anno['image_id']
        image_name = id2names[image_id]

        # get category
        category = 'face'
        
        # add as a key to image_dict
        if not image_name in image_dict.keys():
            image_dict[image_name]=[]
        
        # append bounding boxes to it
        box = anno['bbox']
        # since bboxes = [xmin, ymin, width, height]:
        image_dict[image_name].append([category, box[0], box[1], box[0]+box[2], box[1]+box[3]])
        
    # generate .xml files
    for image_name in image_dict.keys():
        write_to_xml(image_name, image_dict, image_folder, savepath)
        print('generated for: ', image_name)
        
# if __name__=='__main__':     
    # files = os.listdir('image')

    # train_list = []
    # val_list   = []
    
    # for file in files:
        # file = file.split('.')[0]
        # if(randrf(0,1) <0.8):
            # train_list.append(file)
        # else:
            # val_list.append(file)
            
    # with open('train.txt','w') as f:
        # f.write('\n'.join(train_list))
    # with open('val.txt','w') as f:
        # f.write('\n'.join(val_list))
