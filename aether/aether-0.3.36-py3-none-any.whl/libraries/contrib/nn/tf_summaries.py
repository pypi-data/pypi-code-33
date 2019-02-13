import tensorflow as tf

class tf_summaries(object):

    # The cast into reduce_mean must be float32 for reduce_mean to work.
    @staticmethod
    def top_k_summaries(one_hot_labels, logits, n_classes):
        label_ids = tf.cast(tf.argmax(one_hot_labels, axis=1), tf.int32)
        for k in [1, 2, 3, 5, 10]:
            if k >= n_classes:
                continue
            top_n = tf.reduce_mean(tf.cast(tf.nn.in_top_k(predictions=logits, targets=label_ids, k=k), tf.float32))
            tf.summary.scalar('top_{}_acc'.format(k), top_n)


# import re
# from textwrap import wrap
# import itertools
# import tfplot
# import numpy as np
# import matplotlib as plt
# from sklearn.metrics import confusion_matrix
#
# def confusion_matrix_heatmap(correct_labels, predict_labels, all_labels, normalize=False,
#                              title='Confusion matrix', tensor_name = 'MyFigure/image'):
#
#     cm = confusion_matrix(correct_labels, predict_labels, labels=all_labels)
#     if normalize:
#         cm = cm.astype('float') * 10 / cm.sum(axis=1)[:, np.newaxis]
#         cm = np.nan_to_num(cm, copy=True)
#         cm = cm.astype('int')
#
#     np.set_printoptions(precision=2)
#
#     fig = plt.figure.Figure(figsize=(7, 7), dpi=320, facecolor='w', edgecolor='k')
#     ax = fig.add_subplot(1, 1, 1)
#     im = ax.imshow(cm, cmap='Oranges')
#
#     classes = [re.sub(r'([a-z](?=[A-Z])|[A-Z](?=[A-Z][a-z]))', r'\1 ', x) for x in all_labels]
#     classes = ['\n'.join(wrap(l, 40)) for l in classes]
#
#     tick_marks = np.arange(len(classes))
#
#     ax.set_xlabel('Predicted', fontsize=7)
#     ax.set_xticks(tick_marks)
#     c = ax.set_xticklabels(classes, fontsize=4, rotation=-90,  ha='center')
#     ax.xaxis.set_label_position('bottom')
#     ax.xaxis.tick_bottom()
#
#     ax.set_ylabel('True Label', fontsize=7)
#     ax.set_yticks(tick_marks)
#     ax.set_yticklabels(classes, fontsize=4, va ='center')
#     ax.yaxis.set_label_position('left')
#     ax.yaxis.tick_left()
#
#     for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
#         ax.text(j, i, format(cm[i, j], 'd') if cm[i,j]!=0 else '.', horizontalalignment="center", fontsize=6, verticalalignment='center', color= "black")
#     fig.set_tight_layout(True)
#     summary = tfplot.figure.to_summary(fig, tag=tensor_name)
#     return summary