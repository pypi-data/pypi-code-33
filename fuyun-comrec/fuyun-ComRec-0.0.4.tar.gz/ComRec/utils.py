import  argparse,os,logging
from .data import all_type

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def path(output_path,dir):
    dirs=os.path.join(output_path,dir)
    if not os.path.exists(dirs):
        os.makedirs(dirs)
    return dirs

def conlleval(label_predict, label_path, metric_path):
    eval_perl = "./conlleval_rev.pl"
    with open(label_path, "w") as fw:
        line = []
        for sent_result in label_predict:
            for char, tag, tag_ in sent_result:
                tag = '0' if tag == 'O' else tag
                char = char.encode("utf-8")
                line.append("{} {} {}\n".format(char, tag, tag_))
            line.append("\n")
        fw.writelines(line)
    os.system("perl {} < {} > {}".format(eval_perl, label_path, metric_path))
    with open(metric_path,'r') as fr:
        metrics = [line.strip() for line in fr]
    return metrics

def get_entity(tag_seq, char_seq):
    ret = {}
    for t in all_type:
        tmp = get_entity_by_type(tag_seq, char_seq, t)
        if len(tmp) > 0: ret[t] = tmp
    return ret

def get_entity_by_type(tag_seq, char_seq, t):
    length = len(char_seq)
    ret = []
    tmp = ''
    for i, (char, tag) in enumerate(zip(char_seq, tag_seq)):
        if tag == 'B-' + t:
            if len(tmp) > 0:
                ret.append(tmp)
                tmp = ''
            tmp = char
            if i + 1 == length:
                ret.append(tmp)
        if tag == 'I-' + t:
            try:
                tmp += char
            except:
                tmp = char
            if i + 1 == length:
                ret.append(tmp)
        if tag not in ['I-' + t, 'B-' + t]:
            if len(tmp) > 0:
                ret.append(tmp)
                tmp = ''
            continue
    return ret

def get_logger(filename):
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)
    handler = logging.FileHandler(filename)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s: %(message)s'))
    logging.getLogger().addHandler(handler)
    return logger