import time
import tensorflow as tf
from ComRec.utils import path,get_logger,get_entity
from ComRec.model import args,BiLSTM_Softmax
from ComRec.data import *

## configuration
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
config = tf.ConfigProto()
config.gpu_options.allow_growth = True
config.gpu_options.per_process_gpu_memory_fraction = 0.33

project_base = os.path.dirname(os.path.abspath(os.path.join(__file__)))

##param
if args.pretrain_embedding == 'random':
    word2id = read_dictionary(os.path.join(project_base, 'data_path/word2id_1.pkl'))
    embeddings = random_embedding(word2id, args.embedding_dim)
else:
    word2id = read_dictionary(os.path.join(project_base, 'data_path/word2id_tecent.pkl'))
    embedding_path = os.path.join(project_base,'data_path/word2id_tecent_embedding')
    embeddings = np.array(np.loadtxt(embedding_path))
train_path = os.path.join(project_base, 'data_path/train_data')
test_path = os.path.join(project_base, 'data_path/test_data')
train_data = read_corpus(train_path)
test_data = read_corpus(test_path)
test_size = len(test_data)

##timestamp
timestamp = str(int(time.time())) if args.mode == 'train' else args.demo_model

##paths
paths = {}
output =os.path.join('.',os.path.join(project_base, 'result_path'),timestamp)
paths['summary_path'] = path(output, 'summaries')
model_path = path(output, "checkpoints/")
paths['model_path'] = path(model_path, "model")
paths['result_path'] = path(output, "results")
log_path = os.path.join(path(output, "results"), "log.txt")
paths['log_path'] = log_path
get_logger(log_path).info(str(args))

class Apply(object):

    def __init__(self):
        self.timestamp=args.demo_model

    def model_test(self):
        ckpt_file = tf.train.latest_checkpoint(model_path)
        paths['model_path'] = ckpt_file
        model = BiLSTM_Softmax(args, embeddings, tag2label, word2id, paths, config=config)
        model.build_graph()
        model.test(test_data)

    def model_demo(self):
        ckpt_file = tf.train.latest_checkpoint(model_path)
        print(ckpt_file)
        paths['model_path'] = ckpt_file
        model = BiLSTM_Softmax(args, embeddings, tag2label, word2id, paths, config=config)
        model.build_graph()
        saver = tf.train.Saver()
        with tf.Session(config=config) as sess:
            print('============= demo =============')
            saver.restore(sess, ckpt_file)
            while(1):
                print('Please input your sentence:')
                demo_sent = input()
                if demo_sent == '' or demo_sent.isspace():
                    print('See you next time!')
                    break
                else:
                    demo_sent = list(demo_sent.strip())
                    demo_data = [(demo_sent, ['O'] * len(demo_sent))]
                    tag = model.demo_one(sess, demo_data)
                    ret= get_entity(tag, demo_sent)
                    print(ret)

    def model_train(self):
        model = BiLSTM_Softmax(args, embeddings, tag2label, word2id, paths, config=config)
        model.build_graph()
        model.train(train=train_data, dev=test_data)

    def extract(self,str):
        ckpt_file = tf.train.latest_checkpoint(model_path)
        model = BiLSTM_Softmax(args, embeddings, tag2label, word2id, paths, config=config)
        model.build_graph()
        saver=tf.train.Saver()
        with tf.Session(config=config) as sess:
            saver.restore(sess,ckpt_file)
            while(1):
                if str=='' or str.isspace():
                    print('please input your sentence:')
                    continue
                else:
                    str=list(str.strip())
                    demo_data = [(str, ['O'] * len(str))]
                    tag = model.demo_one(sess, demo_data)
                    ret= get_entity(tag, str)
                return ret


if __name__=="__main__":

    str = '中建海峡建设发展有限公司中建海峡建设发展有限公司'
    model_apply=Apply()
    if args.mode=="test":
        model_apply.model_test()
    elif args.mode=="demo":
        model_apply.model_demo()
    elif args.mode=='train':
        model_apply.model_train()
    else:
        print(model_apply.extract(str))