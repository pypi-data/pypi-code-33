import os
import torch
import tqdm
import pandas as pd
import csv


# ############################                   Balancing Predictions          ###########################################
# Adapted from https://github.com/PavelOstyakov/predictions_balancing/blob/master/run.py

def _get_predicts(predicts, coefficients):
    return torch.einsum("ij,j->ij", (predicts, coefficients))


def _get_labels_distribution(predicts, coefficients):
    predicts = _get_predicts(predicts, coefficients)
    labels = predicts.argmax(dim=-1)
    counter = torch.bincount(labels, minlength=predicts.shape[1])
    return counter


def _compute_score_with_coefficients(predicts, coefficients):
    counter = _get_labels_distribution(predicts, coefficients).float()
    counter = counter * 100 / len(predicts)
    max_scores = torch.ones(len(coefficients)).cuda().float() * 100 / len(coefficients)
    result, _ = torch.min(torch.cat([counter.unsqueeze(0), max_scores.unsqueeze(0)], dim=0), dim=0)

    return float(result.sum().cpu())


def _find_best_coefficients(predicts, coefficients, alpha=0.001, iterations=100):
    best_coefficients = coefficients.clone()
    best_score = _compute_score_with_coefficients(predicts, coefficients)

    for _ in tqdm.trange(iterations):
        counter = _get_labels_distribution(predicts, coefficients)
        label = int(torch.argmax(counter).cpu())
        coefficients[label] -= alpha
        score = _compute_score_with_coefficients(predicts, coefficients)
        if score > best_score:
            best_score = score
            best_coefficients = coefficients.clone()

    return best_coefficients


def get_balanced_preds(preds,start_alpha=0.01,min_alpha=0.0001):
    """
    preds: Torch Tensor of shape (num_samples,num_classes)
    """
    alpha = start_alpha
    y=preds.cuda()
    coefs = torch.ones(y.shape[1]).cuda().float()
    last_score = _compute_score_with_coefficients(y, coefs)
    print("Start score", last_score)

    while alpha >= min_alpha:
        coefs = _find_best_coefficients(y, coefs, iterations=3000, alpha=alpha)
        new_score = _compute_score_with_coefficients(y, coefs)

        if new_score <= last_score:
            alpha *= 0.5

        last_score = new_score
        print("Score: {}, alpha: {}".format(last_score, alpha))

    predicts = _get_predicts(y, coefs)
    return predicts.cpu()

#######################################################################################################


