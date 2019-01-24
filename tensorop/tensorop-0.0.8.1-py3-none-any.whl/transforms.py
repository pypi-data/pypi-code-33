from torchvision import transforms

trn_tfms = [
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomVerticalFlip(),
    transforms.RandomAffine(degrees=30),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )]

tst_tfms = [
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )]

def get_std_transforms(res):
    l,b = res[0],res[1]
    trn_tfms[0] = transforms.Resize((l,b))
    tst_tfms[0] = transforms.Resize((l,b))
    return transforms.Compose(trn_tfms),transforms.Compose(tst_tfms)