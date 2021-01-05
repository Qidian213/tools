import os
import cv2
import base64
import torch
import numpy as np
import functools
import aioserver

from detector import Detector

def base64_cv2(string_file):
    image_file = base64.b64decode(string_file)
    image_file = np.fromstring(image_file, np.uint8)  
    image      = cv2.imdecode(image_file,cv2.IMREAD_COLOR)
    return image
    
def async_func(samples, face_detector, batch_size):
    images = [base64_cv2(x['image']) for x in samples]
    return_flags = [x['return_image'] for x in samples]
    
    with torch.no_grad():
        for sample_id in range(0, len(samples), batch_size):
            batch = images[sample_id: sample_id + batch_size]
            flags = return_flags[sample_id: sample_id + batch_size]
            
            torch_images, scales = face_detector.batch_preprocess(batch)
            b_scores, b_boxs, b_landmarks = face_detector.batch_forward(torch_images, scales)
        
        results = []
        for image, flag, scores, boxes, landmarks in zip(batch, flags, b_scores, b_boxs, b_landmarks):
            img_dict = {'code': 200, 'msg': 'ok', 'data': {}}
            
            if(len(scores) <=0):
                img_dict["code"] = 30002 
                img_dict["msg"]  = "image no found object"
                results.append(img_dict)
            else:
                H, W  = image.shape[:2]
                img_dict["data"]['image_width']  = int(W)
                img_dict["data"]['image_height'] = int(H)
                img_dict["data"]['face_num'] = len(boxes)
                img_dict["data"]['result'] = []
                
                for id, (score, box, landmark) in enumerate(zip(scores, boxes, landmarks)):
                    face_dict = {}
                    face_dict['score'] = float('%.4f' % score)
                    face_dict['label'] = 0
                    face_dict['box']  = {}
                    face_dict['box']['left']       = int(box[0])
                    face_dict['box']['top']        = int(box[1])
                    face_dict['box']['right']      = int(box[2])
                    face_dict['box']['bottom']     = int(box[3])
                    face_dict['landmark'] = {}
                    face_dict['landmark']['left_eye']    = [int(landmark[0][0]), int(landmark[0][1])]
                    face_dict['landmark']['right_eye']   = [int(landmark[1][0]), int(landmark[1][1])]
                    face_dict['landmark']['nose']        = [int(landmark[2][0]), int(landmark[2][1])]
                    face_dict['landmark']['left_mouth']  = [int(landmark[3][0]), int(landmark[3][1])]
                    face_dict['landmark']['right_mouth'] = [int(landmark[4][0]), int(landmark[4][1])]

                    img_dict["data"]['result'].append(face_dict)

                    # if(flag):
                        # cv2.rectangle(image, (int(box[0]), int(box[1]), int((box[2]-box[0]))+1, int((box[3]-box[1]))+1), [00,255,255], 2, 16)
                        # for point in landmark:
                            # cv2.circle(image, (int(point[0]), int(point[1])), 2, [0,0,255], -1, 16)
                
                # if(flag):
                    # base64_str = cv2.imencode('.jpg', image)[1].tostring()
                    # base64_str = bytes.decode(base64.b64encode(base64_str))
                    # img_dict["data"]['image'] = base64_str
                    
                results.append(img_dict)
        return results

if __name__ == '__main__':
    os.environ['CUDA_VISIBLE_DEVICES'] = '7'

    current_dir = os.path.abspath(os.path.dirname(__file__))
    face_detector = Detector(checkpoint = current_dir)

    func = functools.partial(async_func, face_detector=face_detector, batch_size=6)

    aioserver.start_inference_service(func, host='127.0.0.1', port=5001, route_path='/face_detection')
