import os
import dlib
import numpy
import cv2
from keras.models import load_model
from . import utils

def age_detection(faces, img, should_draw = False):
      age_classfier_path = os.path.abspath(os.path.join(
          __file__, "../data/age_only_resnet50_weights.061-3.300-4.410.hdf5"
      ))
    
      # load model and weights
      model = utils.get_model()
      margin = 0.4

      model.load_weights(age_classfier_path)
      img_size = model.input.shape.as_list()[1]
      
      input_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
      img_h, img_w, _ = numpy.shape(input_img)

      # detect faces using dlib detector
      after_faces = numpy.empty((len(faces), img_size, img_size, 3))
      text_result = ''
      if len(faces) > 0:
          for i, d in enumerate(faces):
              x1, y1, x2, y2, w, h = d.left(), d.top(), d.right() + 1, d.bottom() + 1, d.width(), d.height()
              xw1 = max(int(x1 - margin * w), 0)
              yw1 = max(int(y1 - margin * h), 0)
              xw2 = min(int(x2 + margin * w), img_w - 1)
              yw2 = min(int(y2 + margin * h), img_h - 1)
              after_faces[i, :, :, :] = cv2.resize(img[yw1:yw2 + 1, xw1:xw2 + 1, :], (img_size, img_size))

          # predict ages and genders of the detected faces
          results = model.predict(after_faces)
          ages = numpy.arange(0, 101).reshape(101, 1)
          predicted_ages = results.dot(ages).flatten()
          for i, d in enumerate(faces):
              label = str(int(predicted_ages[i]))
              if should_draw:
                  color = (0, 255, 0)
                  utils.draw_text(d, img, label, color, 0, -80, 1, 2)
              else:
                  text_result = label
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
              utils.draw_text(face_coordinates, rgb_image, emotion_text, color, 0, -20, 1, 2)
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
                utils.draw_text(face_coordinates, rgb_image, gender_text, color,  0, -50, 1, 2)
          else:
                text_result = gender_text
      return cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR) if should_draw else text_result


detect_method = {
  "age": age_detection,
  "gender": gender_detection,
  "emotion": emotion_detection,
}