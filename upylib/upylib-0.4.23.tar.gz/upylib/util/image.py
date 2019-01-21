from PIL import Image
from PIL import ImageFile
from PIL import ExifTags
ImageFile.LOAD_TRUNCATED_IMAGES = True

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|
def save_thumb(src_fn, dst_fn, size, verbose=1):
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|
    # open
    try:
        img = Image.open(src_fn)
    except Exception as e:
        if verbose>=1:
            print(e)
        return False

    # rotate based on exif
    try:
        exif_dict = img._getexif()
        if exif_dict:
            orientation = None
            for k, v in ExifTags.TAGS.items() : 
                if v == "Orientation":
                    orientation = k
                    break
            if orientation:
                if exif_dict[orientation] == 3 : 
                    img=img.rotate(180, expand=True)
                elif exif_dict[orientation] == 6 : 
                    img=img.rotate(270, expand=True)
                elif exif_dict[orientation] == 8 : 
                    img=img.rotate(90, expand=True)
                else:
                    pass
    except Exception as e:
        if verbose>=2:
            print(e)
        pass

    # prevent alpha channel warning
    try:
        img = img.convert("RGB")
    except Exception as e:
        if verbose>=2:
            print("convert RGB fail: %s" % e)
        pass

    # save
    try:
        img.thumbnail( size, Image.ANTIALIAS )
        img.save(dst_fn, "JPEG")
    except Exception as e:
        if verbose>=1:
            print("Save fail: %s" % e)
        return False

    return True


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|
def test_save_thumb():
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|
    src_fn = "/tmp/image.jpg"
    dst_fn = "/tmp/image_thumb.jpg"
    size = (120, 100)
    if save_thumb(src_fn, dst_fn, size, verbose=1):
        print("ok")
    else:
        print("fail")



if __name__ == '__main__':
    test_save_thumb()
