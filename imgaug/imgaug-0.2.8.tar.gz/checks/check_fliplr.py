from imgaug import augmenters as iaa
import imgaug as ia
from six import moves as sm

ia.seed(1)


def main():
    img = ia.quokka(size=(128, 128), extract="square")
    aug = iaa.Fliplr(p=0.5)

    for _ in sm.xrange(10000):
        img_aug = aug.augment_image(img)


if __name__ == "__main__":
    main()
