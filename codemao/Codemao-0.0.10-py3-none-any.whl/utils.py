
import os
import shutil

import cv2
import dlib
import math
import mxnet as mx
import numpy as np
from skimage import transform as trans
from pathlib import Path



def preprocess_input(x, v2=True):
    x = x.astype("float32")
    x = x / 255.0
    if v2:
        x = x - 0.5
        x = x * 2.0
    return x


def apply_offsets(cors, offsets):
    x, y, width, height = cors.left(), cors.top(), cors.width(), cors.height(),
    x_off, y_off = offsets
    return (x - x_off, x + width + x_off, y - y_off, y + height + y_off)


def detect_faces(img):
    input_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    detector = dlib.get_frontal_face_detector()
    detected = detector(input_img, 1)
    return detected

def load_model (model_path):
    ctx = mx.cpu()
    image_size = (112,112)
    layer = 'fc1'
    sym, arg_params, aux_params = mx.model.load_checkpoint(model_path, 0)
    all_layers = sym.get_internals()
    sym = all_layers[layer+'_output']
    model = mx.mod.Module(symbol=sym, context=ctx, label_names = None)
    model.bind(data_shapes=[('data', (1, 3, image_size[0], image_size[1]))])
    model.set_params(arg_params, aux_params)
    return model


def draw_bounding_box(cors, img, color=(0,0,255)):
    x1, y1, x2, y2 = cors.left(), cors.top(), cors.right() + 1, cors.bottom() + 1
    cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)


def draw_text(cors, image_array, text, color, x_offset=0, y_offset=0, font_scale=2, thickness=2):
    x, y = cors.left(), cors.top()
    cv2.putText(image_array, text, (x + x_offset, y + y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                font_scale, color, thickness, cv2.LINE_AA)


def processing_image(image_path):
    img = cv2.imread(image_path)
    if img is not None:
        h, w, _ = img.shape
        r = 640 / max(w, h)
        cv2.resize(img, (int(w * r), int(h * r)))
    return img

def preprocess(img, bbox=None, landmark=None, **kwargs):
    if isinstance(img, str):
      img = read_image(img, **kwargs)
    M = None
    image_size = []
    str_image_size = kwargs.get('image_size', '')
    if len(str_image_size)>0:
      image_size = [int(x) for x in str_image_size.split(',')]
      if len(image_size)==1:
        image_size = [image_size[0], image_size[0]]
      assert len(image_size)==2
      assert image_size[0]==112
      assert image_size[0]==112 or image_size[1]==96
    if landmark is not None:
      assert len(image_size)==2
      src = np.array([
      [30.2946, 51.6963],
      [65.5318, 51.5014],
      [48.0252, 71.7366],
      [33.5493, 92.3655],
      [62.7299, 92.2041] ], dtype=np.float32 )
      if image_size[1]==112:
        src[:,0] += 8.0
      dst = landmark.astype(np.float32)

      tform = trans.SimilarityTransform()
      tform.estimate(dst, src)
      M = tform.params[0:2,:]
      #M = cv2.estimateRigidTransform( dst.reshape(1,5,2), src.reshape(1,5,2), False)

    if M is None:
      if bbox is None: #use center crop
        det = np.zeros(4, dtype=np.int32)
        det[0] = int(img.shape[1]*0.0625)
        det[1] = int(img.shape[0]*0.0625)
        det[2] = img.shape[1] - det[0]
        det[3] = img.shape[0] - det[1]
      else:
        det = bbox
      margin = kwargs.get('margin', 44)
      bb = np.zeros(4, dtype=np.int32)
      bb[0] = np.maximum(det[0]-margin/2, 0)
      bb[1] = np.maximum(det[1]-margin/2, 0)
      bb[2] = np.minimum(det[2]+margin/2, img.shape[1])
      bb[3] = np.minimum(det[3]+margin/2, img.shape[0])
      ret = img[bb[1]:bb[3],bb[0]:bb[2],:]
      if len(image_size)>0:
        ret = cv2.resize(ret, (image_size[1], image_size[0]))
      return ret 
    else: #do align using landmark
      assert len(image_size)==2
      warped = cv2.warpAffine(img,M,(image_size[1],image_size[0]))

      return warped


def nms(boxes, overlap_threshold, mode='Union'):

    # if there are no boxes, return an empty list
    if len(boxes) == 0:
        return []

    # if the bounding boxes integers, convert them to floats
    if boxes.dtype.kind == "i":
        boxes = boxes.astype("float")

    # initialize the list of picked indexes
    pick = []

    # grab the coordinates of the bounding boxes
    x1, y1, x2, y2, score = [boxes[:, i] for i in range(5)]

    area = (x2 - x1 + 1) * (y2 - y1 + 1)
    idxs = np.argsort(score)

    # keep looping while some indexes still remain in the indexes list
    while len(idxs) > 0:
        # grab the last index in the indexes list and add the index value to the list of picked indexes
        last = len(idxs) - 1
        i = idxs[last]
        pick.append(i)

        xx1 = np.maximum(x1[i], x1[idxs[:last]])
        yy1 = np.maximum(y1[i], y1[idxs[:last]])
        xx2 = np.minimum(x2[i], x2[idxs[:last]])
        yy2 = np.minimum(y2[i], y2[idxs[:last]])

        # compute the width and height of the bounding box
        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)

        inter = w * h
        if mode == 'Min':
            overlap = inter / np.minimum(area[i], area[idxs[:last]])
        else:
            overlap = inter / (area[i] + area[idxs[:last]] - inter)

        # delete all indexes from the index list that have
        idxs = np.delete(idxs, np.concatenate(([last],
                                               np.where(overlap > overlap_threshold)[0])))

    return pick

def adjust_input(in_data):

    if in_data.dtype is not np.dtype('float32'):
        out_data = in_data.astype(np.float32)
    else:
        out_data = in_data

    out_data = out_data.transpose((2,0,1))
    out_data = np.expand_dims(out_data, 0)
    out_data = (out_data - 127.5)*0.0078125
    return out_data

def generate_bbox(map, reg, scale, threshold):

     stride = 2
     cellsize = 12

     t_index = np.where(map>threshold)

     # find nothing
     if t_index[0].size == 0:
         return np.array([])

     dx1, dy1, dx2, dy2 = [reg[0, i, t_index[0], t_index[1]] for i in range(4)]

     reg = np.array([dx1, dy1, dx2, dy2])
     score = map[t_index[0], t_index[1]]
     boundingbox = np.vstack([np.round((stride*t_index[1]+1)/scale),
                              np.round((stride*t_index[0]+1)/scale),
                              np.round((stride*t_index[1]+1+cellsize)/scale),
                              np.round((stride*t_index[0]+1+cellsize)/scale),
                              score,
                              reg])

     return boundingbox.T


def detect_first_stage(img, net, scale, threshold):

    height, width, _ = img.shape
    hs = int(math.ceil(height * scale))
    ws = int(math.ceil(width * scale))
    
    im_data = cv2.resize(img, (ws,hs))
    
    # adjust for the network input
    input_buf = adjust_input(im_data)
    output = net.predict(input_buf)
    boxes = generate_bbox(output[1][0,1,:,:], output[0], scale, threshold)

    if boxes.size == 0:
        return None

    # nms
    pick = nms(boxes[:,0:5], 0.5, mode='Union')
    boxes = boxes[pick]
    return boxes

def detect_first_stage_warpper( args ):
    return detect_first_stage(*args)
