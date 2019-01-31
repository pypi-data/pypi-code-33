from bootstrap.lib.options import Options
from .vqa2 import VQA2
from .tdiuc import TDIUC


def factory(engine=None):
    opt = Options()['dataset']

    dataset = {}
    if opt.get('train_split', None):
        dataset['train'] = factory_split(
            opt['train_split'])
    if opt.get('eval_split', None):
        dataset['eval'] = factory_split(
            opt['eval_split'])

    return dataset


def factory_split(split):
    opt = Options()['dataset']
    shuffle = ('train' in split)

    if opt['name'] == 'tdiuc':
        dataset = TDIUC(
            dir_data=opt['dir'],
            split=split,
            batch_size=opt['batch_size'],
            nb_threads=opt['nb_threads'],
            pin_memory=Options()['misc']['cuda'],
            shuffle=shuffle,
            nans=opt['nans'],
            minwcount=opt['minwcount'],
            nlp=opt['nlp'],
            dir_rcnn=opt['dir_rcnn'])

    elif opt['name'] == 'vqa2':
        samplingans = (opt['samplingans'] and 'train' in split)
        dataset = VQA2(
            dir_data=opt['dir'],
            split=split,
            batch_size=opt['batch_size'],
            nb_threads=opt['nb_threads'],
            pin_memory=Options()['misc']['cuda'],
            shuffle=shuffle,
            nans=opt['nans'],
            minwcount=opt['minwcount'],
            nlp=opt['nlp'],
            proc_split=opt['proc_split'],
            samplingans=samplingans,
            dir_rcnn=opt['dir_rcnn'])

    return dataset
