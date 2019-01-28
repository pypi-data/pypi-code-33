import os
import dlib
import numpy
import cv2
import mxnet as mx
from keras.models import load_model
from .mtcnn_detector import MtcnnDetector
from . import utils

def age_detection(faces, img, should_draw = False):
    age_classfier_path = os.path.abspath(os.path.join(
        __file__, "../data/age/model"
    ))
    mtcnn_path = os.path.join(os.path.dirname(__file__), './data/mtcnn-model')
    model = utils.load_model(age_classfier_path);
    def get_age (data):
        model.forward(data, is_train=False)
        ret = model.get_outputs()[0].asnumpy()
        a = ret[:,2:202].reshape( (100,2) )
        a = numpy.argmax(a, axis=1)
        age = str(int(sum(a)))
        return age

    input_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    margin = 0.4
    img_size = 112
    img_h, img_w, _ = numpy.shape(input_img)

    text_result = ''

    detector = MtcnnDetector(model_folder=mtcnn_path, ctx=mx.cpu(), num_worker=1, accurate_landmark = True, threshold=[0.6,0.7,0.8])
    if len(faces) > 0:
        for i, d in enumerate(faces):
            x1, y1, x2, y2, w, h = d.left(), d.top(), d.right() + 1, d.bottom() + 1, d.width(), d.height()
            xw1 = max(int(x1 - margin * w), 0)
            yw1 = max(int(y1 - margin * h), 0)
            xw2 = min(int(x2 + margin * w), img_w - 1)
            yw2 = min(int(y2 + margin * h), img_h - 1)
            crop_face = cv2.resize(img[yw1:yw2 + 1, xw1:xw2 + 1, :], (img_size, img_size))
            ret  = detector.detect_face(crop_face, det_type = 0)
            if ret is None:
                    return None
            bbox, points = ret
            if bbox.shape[0]==0:
              return None
            bbox = bbox[0,0:4]
            points = points[0,:].reshape((2,5)).T
          
            nimg = utils.preprocess(crop_face, bbox, points, image_size='112,112')
            nimg = cv2.cvtColor(nimg, cv2.COLOR_BGR2RGB)
            aligned = numpy.transpose(nimg, (2,0,1))
            input_blob = numpy.expand_dims(aligned, axis=0)
            data = mx.nd.array(input_blob)
            db = mx.io.DataBatch(data=(data,))
            
            age = get_age(db)
            if should_draw:
                color = (0, 255, 0)
                utils.draw_text(d, img, age, color, 280, -10, 1, 2)
            else:
                text_result = age
    return img if should_draw else text_result

def emotion_detection(faces, img, should_draw = False):
      rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
      gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
      emotion_labels = {
          0: "angry", 1: "disgust", 2: "fear", 3: "happy",
          4: "sad", 5: "surprise", 6: "neutral",
      }
      emotion_model_path = os.path.abspath(os.path.join(
          __file__, "../data/fer2013_mini_XCEPTION.102-0.66.hdf5"
      ))
      emotion_classifier = load_model(emotion_model_path, compile=False)
      emotion_target_size = emotion_classifier.input_shape[1:3]
      emotion_offsets = (20, 40)
      emotion_offsets = (0, 0)
      text_result = ''
      for _, face_coordinates in enumerate(faces):

          x1, x2, y1, y2 = utils.apply_offsets(face_coordinates, emotion_offsets)
          gray_face = gray_image[y1:y2, x1:x2]

          try:
              gray_face = cv2.resize(gray_face, (emotion_target_size))
          except:
              continue
          
          gray_face = utils.preprocess_input(gray_face, True)
          gray_face = numpy.expand_dims(gray_face, 0)
          gray_face = numpy.expand_dims(gray_face, -1)
          emotion_label_arg = numpy.argmax(emotion_classifier.predict(gray_face))
          emotion_text = emotion_labels[emotion_label_arg]
          if should_draw:
              color = (255, 0, 0)
              utils.draw_text(face_coordinates, rgb_image, emotion_text, color, 0, -10, 1, 2)
          else:
              text_result = emotion_text
      return cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR) if should_draw else text_result

def gender_detection(faces, img, should_draw = False):
      rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
      gender_labels = {0: "woman", 1: "man"}
      gender_model_path = os.path.abspath(os.path.join(
          __file__, "../data/simple_CNN.81-0.96.hdf5"
      ))
      gender_classifier = load_model(gender_model_path, compile=False)
      gender_target_size = gender_classifier.input_shape[1:3]
      gender_offsets = (30, 60)
      gender_offsets = (10, 10)
      text_result = ''
      for _, face_coordinates in enumerate(faces):
          x1, x2, y1, y2 = utils.apply_offsets(face_coordinates, gender_offsets)
          rgb_face = rgb_image[y1:y2, x1:x2]

          try:
              rgb_face = cv2.resize(rgb_face, (gender_target_size))
          except:
              continue

          rgb_face = utils.preprocess_input(rgb_face, False)
          rgb_face = numpy.expand_dims(rgb_face, 0)
          gender_prediction = gender_classifier.predict(rgb_face)
          gender_label_arg = numpy.argmax(gender_prediction)
          gender_text = gender_labels[gender_label_arg]
          if should_draw:
                color = (0,0,255)
                utils.draw_text(face_coordinates, rgb_image, gender_text, color,  130, -10, 1, 2)
          else:
                text_result = gender_text
      return cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR) if should_draw else text_result


detect_method = {
  "age": age_detection,
  "gender": gender_detection,
  "emotion": emotion_detection,
}