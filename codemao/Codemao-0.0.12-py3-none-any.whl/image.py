import cv2
import functools
import getpass
import hashlib
import os
import platform
import re
import shutil
import signal
import subprocess
import sys
import tempfile
from . import utils

class Image():

    def __init__(self, path):
        if not(os.path.exists(path)):
            raise TypeError("No such file exist")
        if not(self.valid(path)):
            raise TypeError("invalid image")
        self.image_path = path
        self.child = ""

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
    

    def change_filename(self,name):
        pattern = re.compile(r"\(+[1-9]\d*")
        search = pattern.findall(name)
        if (not search) or name[-1] != ")":
            return name + "(1)"
        elif name.rindex(search[-1]) + len(search[-1]) != len(name) - 1:
            return name + "(1)"
        else:
            num = int(search[-1][1:])
            num = num + 1
            name = name[:name.rindex(search[-1]) + 1] + str(num) + ")"
            return name

    def checkfile(self,path):
        if os.path.exists(path):
            file_name = os.path.splitext(os.path.basename(path))[0]
            extension_name = os.path.splitext(os.path.basename(path))[1]
            name = self.change_filename(file_name)
            file_path = os.path.join(os.path.dirname(path), name + extension_name)
            file_path = self.checkfile(file_path)
            return file_path
        else:
            return path

    def open_image(self):
        show_py = os.path.abspath(os.path.join(
            __file__,
            "../show.py"
        ))
        self.child = subprocess.Popen([sys.executable, show_py, self.image_path])

    def close_image(self):
        if self.child.poll() == 0:
            return
        else:
            self.child.kill()

    def save_to(self, path, rename=""):
        file_name = os.path.basename(self.image_path)
        extension_name = os.path.splitext(file_name)[1]
        if rename :
            file_name = rename + extension_name
        file_path = os.path.join(path, file_name)
        file_path = self.checkfile(file_path)
        shutil.copyfile(self.image_path,file_path)


    def save_to_desktop(self, rename=""):
        file_name = os.path.basename(self.image_path)
        user_name = getpass.getuser()
        file_path = ""
        extension_name = os.path.splitext(file_name)[1]
        if rename :
            file_name = rename + extension_name
        if platform.system() == "Darwin" :
            file_path = os.path.join("/Users", user_name, "Desktop", file_name)
        else :
            file_path = os.path.join("C:", "Users", user_name, "Desktop", file_name)
        file_path = self.checkfile(file_path)
        shutil.copyfile(self.image_path,file_path)

    def face_recognize(self, prop):
        from .detect import detect_method
        image_path = self.image_path
        if prop not in detect_method:
            raise TypeError("`props` not supported")
            
        img = cv2.imdecode(numpy.fromfile(self.image_path, dtype=numpy.uint8),cv2.IMREAD_COLOR)
        faces = utils.detect_faces(img)
        count_face = len(faces)
        if count_face == 0:
            raise TypeError("No face found in this image")
        elif count_face > 1:
            raise TypeError("More than 1 face")
        else:
            return detect_method[prop](faces, img)

    def face_comment(self, props ):
        from .detect import detect_method
        prop_type = type(props)
        if ((prop_type is str) or (prop_type is tuple)):
            if (prop_type is str):
                props = (props,)
            _, filename = os.path.split(self.image_path)
            basename, ext_name = os.path.splitext(filename)
            temp_image = self.highlight_face()
            img = cv2.imdecode(numpy.fromfile(self.image_path, dtype=numpy.uint8),cv2.IMREAD_COLOR)
            faces = utils.detect_faces(img)
            for x in props:
                img = detect_method[x](faces, img, True)
                img_path = tempfile.mktemp(prefix=basename, suffix=ext_name)
                cv2.imencode(ext_name, img)[1].tofile(img_path)
            image = Image(img_path)
            return image.highlight_face()
        else:
            raise TypeError('invalid props')


    def face_highlight(self):
        _, filename = os.path.split(self.image_path)
        basename, ext_name = os.path.splitext(filename)
        img = cv2.imdecode(numpy.fromfile(self.image_path, dtype=numpy.uint8),cv2.IMREAD_COLOR)
        faceRects = utils.detect_faces(img)
        if len(faceRects) > 0:
            for _, faceRect in enumerate(faceRects):
                utils.draw_bounding_box(faceRect, img)
                img_path = tempfile.mktemp(prefix=basename, suffix=ext_name)
                cv2.imencode(ext_name, img)[1].tofile(img_path)
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
    take_photo_py = os.path.abspath(os.path.join(
        __file__,
        "../take_photo.py"
    ))
    try:
        take_photos = subprocess.run([sys.executable, take_photo_py, img_path, key],timeout=120)
    except subprocess.TimeoutExpired:
        print("未收到截图指令，积木运行超时，请重新运行")
    img = Image(img_path)
    return img


if __name__ == "__main__":
    #img = take_photos("face_appears")
    img = take_photos("enter_pressed")
    print(img)
