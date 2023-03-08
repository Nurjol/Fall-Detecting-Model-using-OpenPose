import argparse
import logging
import time

import cv2
import numpy as np

import os
import math

from tf_pose.estimator import TfPoseEstimator
from tf_pose.networks import get_graph_path, model_wh

logger = logging.getLogger('TfPoseEstimator-WebCam')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

fps_time = 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='tf-pose-estimation realtime webcam')
    parser.add_argument('--video', type=str, default=0)

    parser.add_argument('--resize', type=str, default='0x0',
                        help='if provided, resize images before they are processed. default=0x0, Recommends : 432x368 or 656x368 or 1312x736 ')
    parser.add_argument('--resize-out-ratio', type=float, default=4.0,
                        help='if provided, resize heatmaps before they are post-processed. default=1.0')

    parser.add_argument('--model', type=str, default='cmu', help='cmu / mobilenet_thin / mobilenet_v2_large / mobilenet_v2_small')
    parser.add_argument('--show-process', type=bool, default=False,
                        help='for debug purpose, if enabled, speed for inference is dropped.')

    parser.add_argument('--save_video', type=bool, default=False,
                        help='To write output video. Default name output.avi')

    args = parser.parse_args()

    logger.debug('initialization %s : %s' % (args.model, get_graph_path(args.model)))
    w, h = model_wh(args.resize)
    if w > 0 and h > 0:
        e = TfPoseEstimator(get_graph_path(args.model), target_size=(w, h))
    else:
        e = TfPoseEstimator(get_graph_path(args.model), target_size=(432, 368))
    logger.debug('cam read+')
    cam = cv2.VideoCapture(args.video)
    ret_val, image = cam.read()
    logger.info('cam image=%dx%d' % (image.shape[1], image.shape[0]))

    head_y_list = [0, 0]
    bbox_r_list=[1, 1, 1, 1]
    frame = 0
    last_time=time.time()
    fcount = 0
    fall_state=False
    fall_count=0
    out = cv2.VideoWriter('output.avi', cv2.VideoWriter_fourcc('M','J','P','G'),
                                  10, (image.shape[1], image.shape[0]))
   
    while True:
        ret_val, image = cam.read()
        if image is None:
            print("NULL")
            break
        
        fcount+=1
        if fcount%10 != 0:
            continue
        
        i_h, i_w=image.shape[:2]
        i_h=480*i_h//i_w
        i_w=480
        image=cv2.resize(image, (i_w, i_h), interpolation=cv2.INTER_AREA)

        img_y=cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
        ycrcb_planes=cv2.split(img_y)
        if(np.mean(ycrcb_planes[0])<70):
            ycrcb_ss=list(ycrcb_planes)
            ycrcb_ss[0]=cv2.equalizeHist(ycrcb_ss[0])
            dst_y=cv2.merge(ycrcb_ss)
            image=cv2.cvtColor(dst_y, cv2.COLOR_YCrCb2BGR)
        
        humans = e.inference(image, resize_to_default=(w > 0 and h > 0), upsample_size=args.resize_out_ratio)
        image = TfPoseEstimator.draw_humans(image, humans, imgcopy=False)
        no_people = len(humans)
        print("No. of people: ", no_people)

        if (no_people==1):
            for human in humans:
                try:
                    if 0 in human.body_parts:
                        a = human.body_parts[0]  # head shot
                    else:
                        a = human.body_parts[1]
                    head_x = a.x*image.shape[1]
                    head_y = a.y*image.shape[0]
                    head_y_list.append(head_y)
                    
                    bbox_x=[]
                    bbox_y=[]
                    for i in human.body_parts:
                        bbox_x.append(human.body_parts[i].x)
                        bbox_y.append(human.body_parts[i].y)
                    min_x=int(min(bbox_x)*image.shape[1])
                    min_y=int(min(bbox_y)*image.shape[0])
                    max_x=int(max(bbox_x)*image.shape[1])
                    max_y=int(max(bbox_y)*image.shape[0])
                    bbox_ratio=(max_y-min_y)/(max_x-min_x)
                    bbox_r_list.append(bbox_ratio)
                    
                    cv2.putText(image,
                    "head: %d, %d" % (head_x, head_y),
                    (10, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (255, 255, 255), 2)
                except:
                    pass
                
                if fall_state:
                    fall_count+=1
                    if fall_count<15:
                        if (head_y_list[-(fall_count+1)]-head_y)>=0:
                            image=cv2.rectangle(image, (min_x, min_y), (max_x, max_y), (0, 0, 255))
                            if bbox_ratio>1:
                                print("stand")
                                cv2.putText(image,
                                "STAND",
                                (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                (0, 0, 255), 2, 11)
                                fall_state=False
                                fall_count=0
                    else:
                        print("Fall Detected")
                        cv2.putText(image,
                                "FALL DETECTED",
                                (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                (0, 0, 255), 2, 11)
                        fall_state=False
                        fall_count=0
                    
                    
                else:
                    if head_y - head_y_list[-2] >= 20:
                        theta=0
                        hwratio=0.5
                        image=cv2.rectangle(image, (min_x, min_y), (max_x, max_y), (0, 0, 255))

                        if (bbox_r_list[-2]-bbox_ratio)>hwratio:
                            print("fall state")
                            cv2.putText(image,
                                "FALL state",
                                (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                (0, 0, 255), 2, 11)
                            fall_state=True
                        #else:
                           # pass
                
        cv2.putText(image,
                    "FPS: %f" % (1.0 / (time.time() - fps_time)),
                    (10, 20),  cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 255, 0), 2)
        cv2.putText(image,
                    "No. of People: %d" % (no_people),
                    (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (255, 255, 255), 2)
        cv2.imshow('tf-pose-estimation result', image)

        fps_time = time.time()
        if(frame == 0) and (args.save_video):
            out.write(image)
        if cv2.waitKey(1) == 27:
            break
    cv2.destroyAllWindows()
