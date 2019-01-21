import os
import platform
import tempfile
import cv2
import getpass
import hashlib
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from . import utils
from .detect import detect_method


class Image():

    def __init__(self, path):
        if not(os.path.exists(path)):
            raise TypeError("No such file exist")
        self.image_path = path
        md5 = hashlib.md5()
        md5.update(path.encode("utf-8"))
        self.figure_name = os.path.basename(path) + md5.hexdigest()

    def __str__(self):
        return F"Image ({self.image_path})"


    def valid(self, path: str) -> bool:
        """Check specified image with path is expected file type and size.

        Supported image type: png, jpg, bmp.
        Maximum image size is 2Mib.
        :param path: Absolute path to image file.
        :return: bool
        """
        _, extname = os.path.splitext(path.lower())
        if extname not in (".jpg", ".jpeg", ".png", ".bmp"):
            return False

        file_stat = os.stat(path)
        kMaxSize = 2 ** 21
        if file_stat.st_size > kMaxSize:
            return False
        return True

    def open_image(self):
        img = mpimg.imread(self.image_path)
        plt.imshow(img)
        plt.figure(self.figure_name)
        plt.axis("off")
        plt.show(block=False)

    def close_image(self):
        plt.close(self.figure_name)

    def save_to(self, path, rename=""):
        file_name = os.path.basename(self.image_path)
        if rename :
            file_name = rename
        file_path = os.path.join(path, file_name)
        plt.savefig(file_path)

    def save_to_desktop(self, rename=""):
        file_name = os.path.basename(self.image_path)
        user_name = getpass.getuser()
        file_path = ""
        if rename :
            file_name = rename
        if platform.system() == "Darwin" :
            file_path = os.path.join("Users", user_name, "Desktop", file_name)
        else :
            file_path = os.path.join("C:", "Users", user_name, "Desktop", file_name)
        plt.savefig(file_path)

    def recognize_face(self, prop):
        image_path = self.image_path
        if prop not in detect_method:
            raise TypeError("`props` not supported")
        if not(self.valid(self.image_path)):
            raise TypeError("invalid image")
            
        img = cv2.imread(self.image_path)
        faces = utils.detect_faces(img)
        count_face = len(faces)
        if count_face == 0:
            raise TypeError("No face found in this image")
        elif count_face > 1:
            raise TypeError("More than 1 face")
        else:
            return detect_method[prop](faces, img)

    def face_comment(self, props ):
        prop_type = type(props)
        if ((prop_type is str) or (prop_type is tuple)):
            if (prop_type is str):
                props = (props,)
            _, filename = os.path.split(self.image_path)
            basename, ext_name = os.path.splitext(filename)
            temp_image = self.highlight_face()
            img = cv2.imread(self.image_path)
            faces = utils.detect_faces(img)
            for x in props:
                img = detect_method[x](faces, img, True)
                img_path = tempfile.mktemp(prefix=basename, suffix=ext_name)
                cv2.imwrite(img_path, img)
            image = Image(img_path)
            return image.highlight_face()
        else:
            raise TypeError('invalid props')


    def highlight_face(self):

        _, filename = os.path.split(self.image_path)
        basename, ext_name = os.path.splitext(filename)
        img = cv2.imread(self.image_path)
        faceRects = utils.detect_faces(img)
        if len(faceRects) > 0:
            for _, faceRect in enumerate(faceRects):
                utils.draw_bounding_box(faceRect, img)
                img_path = tempfile.mktemp(prefix=basename, suffix=ext_name)
                cv2.imwrite(img_path, img)
            image = Image(img_path)
            return image
        else:
            raise TypeError("No face found in this image")
        


    def count_face(self):
        pass


def take_photos(event: str, img_path=""):
    """Take photos on event occurs.

    :param event:
    :param img_path: The photo will be saved to, or an temp filepath will be used is not specified.
    :return: A new image object.
    """
    classfier_xml_path = os.path.abspath(os.path.join(
        cv2.__file__,
        "../data/haarcascade_frontalface_alt.xml"
    ))
    classfier = cv2.CascadeClassifier(classfier_xml_path)
    def take_photo(save_as, key):
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faceRects = classfier.detectMultiScale(grey, scaleFactor = 1.2, minNeighbors = 10, minSize = (32, 32))
            cv2.imshow("img1", frame)
            # Close window on SpaceBar pressed.
            if ((key == "f" and len(faceRects) > 0) or (cv2.waitKey(1) & 0xff) == ord(key)):
                cv2.imwrite(save_as, frame)
                cv2.destroyAllWindows()
                break
        cap.release()

    events = ("space_pressed", "enter_pressed", "face_appears")
    if event not in events:
        raise TypeError("Event not support, expected:", events)

    if not img_path:
        img_path = tempfile.mktemp(prefix="codemao_face_", suffix=".png")
    if event == "space_pressed":
        key = " "
    elif event == "enter_pressed":
        key = "\r"
    elif event == "face_appears":
        key = "f"
    else:
        key = ""
    take_photo(img_path, key)

    img = Image(img_path)
    return img


if __name__ == "__main__":
    #img = take_photos("face_appears")
    img = take_photos("enter_pressed")
    print(img)
