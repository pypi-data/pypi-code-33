import cv2
import os
import dlib
from keras.applications import ResNet50
from keras.layers import Dense
from keras.models import Model
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

def get_model():
    base_model = ResNet50(include_top=False, weights="imagenet", input_shape=(224, 224, 3), pooling="avg")
    prediction = Dense(units=101, kernel_initializer="he_normal", use_bias=False, activation="softmax",
                       name="pred_age")(base_model.output)
    model = Model(inputs=base_model.input, outputs=prediction)

    return model

def draw_bounding_box(cors, img, color=(0,0,255)):
    x1, y1, x2, y2 = cors.left(), cors.top(), cors.right() + 1, cors.bottom() + 1
    cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

def draw_text(cors, image_array, text, color, x_offset=0, y_offset=0,
                                            font_scale=2, thickness=2):
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
