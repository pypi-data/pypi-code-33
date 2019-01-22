import typing

import numpy  # type: ignore
from sklearn import metrics, preprocessing  # type: ignore

from d3m import exceptions
from d3m.metadata import problem

__ALL__ = ('functions_map',)

Truth = typing.TypeVar('Truth', bound=typing.Sequence)
Predictions = typing.TypeVar('Predictions', bound=typing.Sequence)


def f1(y_true: Truth, y_pred: Predictions, *, pos_label: str = None) -> float:
    if pos_label is None:
        raise exceptions.InvalidArgumentValueError("\"pos_label\" is required for f1 metric.")
    return metrics.f1_score(y_true, y_pred, pos_label=pos_label)


def precision(y_true: Truth, y_pred: Predictions, *, pos_label: str = None) -> float:
    if pos_label is None:
        raise exceptions.InvalidArgumentValueError("\"pos_label\" is required for precision metric.")
    return metrics.precision_score(y_true, y_pred, pos_label=pos_label)


def recall(y_true: Truth, y_pred: Predictions, *, pos_label: str = None) -> float:
    if pos_label is None:
        raise exceptions.InvalidArgumentValueError("\"pos_label\" is required for recall metric.")
    return metrics.recall_score(y_true, y_pred, pos_label=pos_label)


# TODO: This is the same as "roc_auc_macro".
#       See: https://gitlab.datadrivendiscovery.org/MIT-LL/d3m_data_supply/issues/148
def roc_auc(y_true: Truth, y_pred: Predictions) -> float:
    return metrics.roc_auc_score(y_true, y_pred)


def roc_auc_micro(y_true: Truth, y_pred: Predictions) -> float:
    return metrics.roc_auc_score(y_true, y_pred, average='micro')


def roc_auc_macro(y_true: Truth, y_pred: Predictions) -> float:
    return metrics.roc_auc_score(y_true, y_pred, average='macro')


def precision_at_top_k(y_true: Truth, y_pred: Predictions, *, k: int = 20) -> float:
    y_true = numpy.argsort(y_true)[::-1]
    y_pred = numpy.argsort(y_pred)[::-1]

    y_true = typing.cast(Truth, y_true[0:k])
    y_pred = typing.cast(Predictions, y_pred[0:k])

    return numpy.float(len(numpy.intersect1d(y_true, y_pred))) / k


def root_mean_squared_error_avg(y_true: Truth, y_pred: Predictions) -> float:
    return numpy.average(metrics.mean_squared_error(y_true, y_pred, multioutput='raw_values') ** 0.5)


def unvectorize(targets: typing.Sequence) -> typing.Sequence:
    """
    If ``targets`` have two columns (index, object detection target) or three (index, object detection
    target, confidence), we make it into 5 or 6, respectively, by splitting the second column into
    4 columns for each bounding box edge.
    """

    new_targets = []

    for target in targets:
        if len(target) == 2:
            new_targets.append([target[0]] + target[1].split(','))
        elif len(target) == 3:
            new_targets.append([target[0]] + target[1].split(',') + list(target[2:]))
        else:
            new_targets.append(target)

    return new_targets


def group_gt_boxes_by_image_name(gt_boxes: Truth) -> typing.Dict:
    gt_dict: typing.Dict = {}

    for box in gt_boxes:
        image_name = box[0]
        bbox = box[1:]

        if image_name not in gt_dict.keys():
            gt_dict[image_name] = []

        gt_dict[image_name].append({'bbox': bbox})

    return gt_dict


def voc_ap(rec: numpy.ndarray, prec: numpy.ndarray) -> float:
    # First append sentinel values at the end.
    mrec = numpy.concatenate(([0.], rec, [1.]))
    mpre = numpy.concatenate(([0.], prec, [0.]))

    # Compute the precision envelope.
    for i in range(mpre.size - 1, 0, -1):
        mpre[i - 1] = numpy.maximum(mpre[i - 1], mpre[i])

    # To calculate area under PR curve, look for points
    # where X axis (recall) changes value.
    i = numpy.where(mrec[1:] != mrec[:-1])[0]

    # And sum (\Delta recall) * prec.
    ap = numpy.sum((mrec[i + 1] - mrec[i]) * mpre[i + 1])

    return float(ap)


def object_detection_average_precision(y_true: Truth, y_pred: Predictions) -> float:
    """
    This function is different from others because ``y_true`` and ``y_pred`` are not vectors but arrays.
    """

    ovthresh = 0.5

    y_true = typing.cast(Truth, unvectorize(y_true))
    y_pred = typing.cast(Predictions, unvectorize(y_pred))

    # Load ground truth.
    gt_dict = group_gt_boxes_by_image_name(y_true)

    # Extract gt objects for this class.
    recs = {}
    npos = 0

    imagenames = sorted(gt_dict.keys())
    for imagename in imagenames:
        Rlist = [obj for obj in gt_dict[imagename]]
        bbox = numpy.array([x['bbox'] for x in Rlist])
        det = [False] * len(Rlist)
        npos = npos + len(Rlist)
        recs[imagename] = {'bbox': bbox, 'det': det}

    # Load detections.
    det_length = len(y_pred[0])

    # Check that all boxes are the same size.
    for det in y_pred:
        assert len(det) == det_length, 'Not all boxes have the same dimensions.'

    image_ids = [x[0] for x in y_pred]
    BB = numpy.array([[float(z) for z in x[1:5]] for x in y_pred])

    if det_length == 6:
        confidence = numpy.array([float(x[-1]) for x in y_pred])
        # Sort by confidence.
        sorted_ind = numpy.argsort(-confidence)

    else:
        num_dets = len(y_pred)
        sorted_ind = numpy.arange(num_dets)

    BB = BB[sorted_ind, :]
    image_ids = [image_ids[x] for x in sorted_ind]

    # Go down y_pred and mark TPs and FPs.
    nd = len(image_ids)
    tp = numpy.zeros(nd)
    fp = numpy.zeros(nd)
    for d in range(nd):
        R = recs[image_ids[d]]
        bb = BB[d, :].astype(float)
        ovmax = -numpy.inf
        BBGT = R['bbox'].astype(float)

        if BBGT.size > 0:
            # Compute overlaps.
            # Intersection.
            ixmin = numpy.maximum(BBGT[:, 0], bb[0])
            iymin = numpy.maximum(BBGT[:, 1], bb[1])
            ixmax = numpy.minimum(BBGT[:, 2], bb[2])
            iymax = numpy.minimum(BBGT[:, 3], bb[3])
            iw = numpy.maximum(ixmax - ixmin + 1., 0.)
            ih = numpy.maximum(iymax - iymin + 1., 0.)
            inters = iw * ih

            # Union.
            uni = ((bb[2] - bb[0] + 1.) * (bb[3] - bb[1] + 1.) +
                   (BBGT[:, 2] - BBGT[:, 0] + 1.) *
                   (BBGT[:, 3] - BBGT[:, 1] + 1.) - inters)

            overlaps = inters / uni
            ovmax = numpy.max(overlaps)
            jmax = numpy.argmax(overlaps)

        if ovmax > ovthresh:
            if not R['det'][jmax]:
                tp[d] = 1.
                R['det'][jmax] = 1
            else:
                fp[d] = 1.
        else:
            fp[d] = 1.

    # Compute precision recall.
    fp = numpy.cumsum(fp)
    tp = numpy.cumsum(tp)
    rec = tp / float(npos)
    # Avoid divide by zero in case the first detection matches a difficult ground truth.
    prec = tp / numpy.maximum(tp + fp, numpy.finfo(numpy.float64).eps)
    ap = voc_ap(rec, prec)

    return ap


functions_map = {
    problem.PerformanceMetric.ACCURACY: lambda y_true, y_pred: metrics.accuracy_score(y_true, y_pred),  # type: ignore
    problem.PerformanceMetric.PRECISION: precision,  # type: ignore
    problem.PerformanceMetric.RECALL: recall,  # type: ignore
    problem.PerformanceMetric.F1: f1,  # type: ignore
    problem.PerformanceMetric.F1_MICRO: lambda y_true, y_pred: metrics.f1_score(y_true, y_pred, average='micro'),  # type: ignore
    problem.PerformanceMetric.F1_MACRO: lambda y_true, y_pred: metrics.f1_score(y_true, y_pred, average='macro'),  # type: ignore
    problem.PerformanceMetric.ROC_AUC: roc_auc,  # type: ignore
    problem.PerformanceMetric.ROC_AUC_MICRO: roc_auc_micro,  # type: ignore
    problem.PerformanceMetric.ROC_AUC_MACRO: roc_auc_macro,  # type: ignore
    problem.PerformanceMetric.MEAN_SQUARED_ERROR: lambda y_true, y_pred: metrics.mean_squared_error(y_true, y_pred),  # type: ignore
    problem.PerformanceMetric.ROOT_MEAN_SQUARED_ERROR: lambda y_true, y_pred: metrics.mean_squared_error(y_true, y_pred) ** 0.5,  # type: ignore
    problem.PerformanceMetric.ROOT_MEAN_SQUARED_ERROR_AVG: root_mean_squared_error_avg,  # type: ignore
    problem.PerformanceMetric.MEAN_ABSOLUTE_ERROR: lambda y_true, y_pred: metrics.mean_absolute_error(y_true, y_pred),  # type: ignore
    problem.PerformanceMetric.R_SQUARED: lambda y_true, y_pred: metrics.r2_score(y_true, y_pred),  # type: ignore
    problem.PerformanceMetric.NORMALIZED_MUTUAL_INFORMATION: lambda labels_true, labels_pred: metrics.normalized_mutual_info_score(labels_true, labels_pred),  # type: ignore
    problem.PerformanceMetric.JACCARD_SIMILARITY_SCORE: lambda y_true, y_pred: metrics.jaccard_similarity_score(y_true, y_pred),  # type: ignore
    problem.PerformanceMetric.PRECISION_AT_TOP_K: precision_at_top_k,  # type: ignore
    problem.PerformanceMetric.OBJECT_DETECTION_AVERAGE_PRECISION: object_detection_average_precision,  # type: ignore
}
