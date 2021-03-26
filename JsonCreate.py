import os
import cv2
import json
import numpy
import random 

def randrf(low, high):
    return random.uniform(0, 1) * (high - low) + low
    
# if __name__ == '__main__':
    # Train_Dict = {}
    # Val_Dict   = {}
    
    # Img_Dir = 'image/'
    # Ann_Dir = 'label/'
    
    # Files = os.listdir(Img_Dir)
    # for file in Files:
        # Img_path = Img_Dir + file
        # Ann_path = Ann_Dir + file.replace('png', 'txt')        
    
        # ann_file  = open(Ann_path, "r")
        # ann_lines = ann_file.readlines()
        
        # ann_dict = {}
        # ann_dict['boxs'] = []
        # for line in ann_lines[1:]:
            # line = line.replace("\n", "").split(' ')
            # ann_dict['boxs'].append([float(line[0]),float(line[1]),float(line[2]),float(line[3])])

        # Image = cv2.imread(Img_path)
        # H,W   = Image.shape[:2]
        # ann_dict['width']  = W
        # ann_dict['height'] = H
        
        # if(randrf(0,1) <0.8):
            # Train_Dict[file] = ann_dict
        # else:
            # Val_Dict[file] = ann_dict

    # print(len(Train_Dict.keys()))
    # print(len(Val_Dict.keys()))
    # json.dump(Train_Dict, open('./DarkFace_Train.json', 'w'), indent=4)
    # json.dump(Val_Dict, open('./DarkFace_Val.json', 'w'), indent=4)

    
if __name__ == '__main__':
    Train_Dict = {}
    Val_Dict   = {}
    
    Ann_Dir = 'label/'
    Files = os.listdir(Ann_Dir)
    for file in Files:
        Ann_path = Ann_Dir + file    
    
        ann_file  = open(Ann_path, "r")
        ann_lines = ann_file.readlines()
        
        out_list = []
        for line in ann_lines[1:]:
            line = line.replace("\n", "").split(' ')
            box  = [float(line[0]),float(line[1]),float(line[2]),float(line[3])]
            x_c  = (box[0]+box[2])/(2*1080.0)
            y_c  = (box[1]+box[3])/(2*720.0)
            width = (box[2]-box[0])/1080.0
            height = (box[3]-box[1])/720
            rline = '{:d} {:.6f} {:.6f} {:.6f} {:.6f}'.format(0, x_c, y_c, width, height)
            out_list.append(rline)
            
        if out_list == []:
            continue
            
        if(randrf(0,1) <0.8):
            with open(os.path.join('Anns_Train',file),'w') as f:
                f.write('\n'.join(out_list))
        else:
            with open(os.path.join('Anns_Val',file),'w') as f:
                f.write('\n'.join(out_list))


