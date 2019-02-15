#encoding=UTF-8
import numpy as np
import os
import cv2
os.environ['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
import tensorflow as tf
from PIL import Image
import datetime
from distutils.sysconfig import get_python_lib

import pdb



site_package_path = get_python_lib()
path_to_labels = os.path.join(site_package_path, 'hand_detection_v4/data/hand_label_map.pbtxt')
path_to_ckpt = os.path.join(site_package_path,'hand_detection_v4/models/hand.our6_rfcnmv_320_500000/frozen_inference_graph.pb')
num_classes = 1


def save_image(image,origin_file_name,save_file_name,hand_boxes):
   #pdb.set_trace()
   print 'in save_image'
   img=cv2.imread(origin_file_name)
   for hand_box in hand_boxes:
     cv2.rectangle(img,(hand_box['left'],hand_box['top']),(hand_box['right'],hand_box['bottom']),(0,255,0),1)
   cv2.imwrite(save_file_name,img)


def get_predict_boxes_and_scores_use_nms(image, boxes, classes, scores, thresh = 0.3):
    #pdb.set_trace()
    CONF_THRESH = 0.5
    im_width, im_height = image.size
    wid_hei= np.array([[im_height], [im_width], [im_height], [im_width]])
    wid_hei_array = np.stack(wid_hei,axis=1)
    bboxes = wid_hei_array * boxes

    dets = np.hstack((bboxes, scores[:, np.newaxis])).astype(np.float32)
    x1 = dets[:, 1]
    y1 = dets[:, 0]
    x2 = dets[:, 3]
    y2 = dets[:, 2]
    scores1 = dets[:,4]
    #每一个候选框的面积
    areas = (x2 - x1 + 1) * (y2 - y1 + 1)
    #order是按照score降序排序的
    order = scores1.argsort()[::-1]      #按照降序返回 index

    keep = []
    while order.size > 0:
        i = order[0]
        keep.append(i)
        #计算当前概率最大矩形框与其他矩形框的相交框的坐标
        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]])
        #计算相交框的面积
        w = np.maximum(0.0, xx2 - xx1 + 1)
        h = np.maximum(0.0, yy2 - yy1 + 1)
        inter = w * h
        #计算重叠度IOU：重叠面积/（面积1+面积2-重叠面积）
        ovr = inter / (areas[i] + areas[order[1:]] - inter)
        #找到重叠度不高于阈值的矩形框索引
        inds = np.where(ovr <= thresh)[0]
        #将order序列更新，由于前面得到的矩形框索引要比矩形框在原order序列中的索引小1，所以要把这个1加回来
        order = order[inds + 1]
    #pdb.set_trace()
    dets_nms = dets[keep,:]
    indses = np.where(dets_nms[:, -1] >= CONF_THRESH)[0]
    if len(indses) == 0:
       detses = []
    else:
        detses = dets_nms[indses,:]
    #dets_nms 是过完nms的，有很多。detses是scores用门限限制了的.
    return keep, indses, dets_nms, detses

def load_image_into_numpy_array(image):
  (im_width, im_height) = image.size
  return np.array(image.getdata()).reshape(
      (im_height, im_width, 3)).astype(np.uint8)

def get_images(PATH_TO_TEST_IMAGES_DIR):
   test_images=[]
   images=os.listdir(PATH_TO_TEST_IMAGES_DIR)
   i=0
   for image in images:
       i=i+1
       test_images.append('%s/%s'%(PATH_TO_TEST_IMAGES_DIR,image))
   return test_images

def run_model_to_predict(PATH_TO_TEST_IMAGES_DIR):
    
    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.GraphDef()                            #重新定义一个图
        with tf.gfile.GFile(path_to_ckpt, 'rb') as fid:         # 读入模型
            serialized_graph = fid.read()                       #将*.pb文件读入serialized_graph
            od_graph_def.ParseFromString(serialized_graph)      #将serialized_graph的内容恢复到你定义的图中
            #pdb.set_trace()
            #print od_graph_def
            tf.import_graph_def(od_graph_def, name='')          #将od_graph_def导入当前默认的图中（加载模型）

    test_images = get_images(PATH_TO_TEST_IMAGES_DIR)                     # 调函数  返回 所有测试图像的路径

    sum_time = 0
    img_num = 0
    pre_rac_info_tmp = []                                   #llz
    with detection_graph.as_default():
      with tf.Session(graph=detection_graph) as sess:
        for image_path in test_images:
          img_num = img_num + 1
          image_name = image_path.split('/')[-1]
          image = Image.open(image_path)
          image_np = load_image_into_numpy_array(image)       # 调函数 (120,160,3)
          image_np_expanded = np.expand_dims(image_np, axis=0)      # (1,120,160,3)
          image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
          boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
          scores = detection_graph.get_tensor_by_name('detection_scores:0')
          classes = detection_graph.get_tensor_by_name('detection_classes:0')
          num_detections = detection_graph.get_tensor_by_name('num_detections:0')

          start = datetime.datetime.now()               #llz
          (boxes, scores, classes, num_detections) = sess.run(
              [boxes, scores, classes, num_detections],
              feed_dict={image_tensor: image_np_expanded})
          end = datetime.datetime.now()                 #llz
          single_time = (end - start).total_seconds()
          sum_time = sum_time + single_time

          keep, rac_num, pre_all_racts, pre_part_racts = get_predict_boxes_and_scores_use_nms(image, np.squeeze(boxes), np.squeeze(classes).astype(np.int32), np.squeeze(scores), thresh = 0.3)

          if pre_part_racts != []:      #之前写的是len(pre_all_racts),等待验证。
             pre_boxes_info = pre_part_racts
          else:
             pre_boxes_info = []
          pre_txt_dic = {}
          num_p_bbox = len(pre_boxes_info)
          p_bbox = []
          if int(num_p_bbox) != 0:
              for n in range(num_p_bbox):
                  p_bbox.append(str(pre_boxes_info[n][1]))
                  p_bbox.append(str(pre_boxes_info[n][0]))
                  p_bbox.append(str(pre_boxes_info[n][3]))
                  p_bbox.append(str(pre_boxes_info[n][2]))
                  p_bbox.append(str(pre_boxes_info[n][4]))
              pre_txt_dic['img_name'] = image_name
              pre_txt_dic['num_p_bbox'] = str(num_p_bbox)
              pre_txt_dic['p_bbox'] = p_bbox          #xmin, ymin, xmax, ymax
              pre_rac_info_tmp.append(pre_txt_dic)
          print ('img_name:%s, num_p_bbox:%s, p_bbox:%s'%(image_name, str(num_p_bbox), p_bbox))

    return pre_rac_info_tmp, sum_time, img_num





if __name__=="__main__":
#   path_to_labels = './data/hand_label_map.pbtxt'
#    path_to_ckpt = './models/hand.our6_rfcnmv_320_500000/frozen_inference_graph.pb'
#   num_classes = 1
   class_id_list = [101968001]
   for i in range(len(class_id_list)):
       path_to_test_images_dir = os.path.join('./data', str(class_id_list[i])+'/')
       
   pre_racts, sum_time, img_num = run_model_to_predict(path_to_test_images_dir) 
   





