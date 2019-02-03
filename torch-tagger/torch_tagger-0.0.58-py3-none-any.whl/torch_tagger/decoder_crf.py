# -*- coding: utf-8 -*-
"""
.. module:: decoder_crf

"""

import numpy as np
import torch
from torch import nn

from .torch_lm import START_TAG, STOP_TAG
from .utils import sequence_mask

# Transfer disable
NO_TRANS = -10000.


class DecoderCRF(nn.Module):
    """CRF loss and inference
    """

    def __init__(self, tag_to_ix):
        """init"""
        super(DecoderCRF, self).__init__()
        self._tag_to_ix = tag_to_ix
        self._stop_idx = self._tag_to_ix[STOP_TAG]
        self._start_idx = self._tag_to_ix[START_TAG]
        self._tagset_size = len(tag_to_ix)
        self._transitions = nn.Parameter(
            torch.zeros(self._tagset_size, self._tagset_size))
        # These two statements enforce the constraint that we never transfer
        # to the start tag and we never transfer from the stop tag
        nn.init.constant_(self._transitions[self._start_idx, :], NO_TRANS)
        nn.init.constant_(self._transitions.data[:, self._stop_idx], NO_TRANS)
        # PAD_TAG
        nn.init.constant_(self._transitions.data[:, 0], NO_TRANS)
        nn.init.constant_(self._transitions.data[0, :], NO_TRANS)

    def _forward_alg_single(self, feats):
        # Do the forward algorithm to compute the partition function
        init_alphas = torch.full((1, self._tagset_size),
                                 NO_TRANS,
                                 device=feats.device)
        # START_TAG has all of the score.
        init_alphas[0][self._start_idx] = 0.

        # Wrap in a variable so that we will get automatic backprop
        forward_var = init_alphas

        # Iterate through the sentence
        for feat in feats:
            alphas_t = []  # The forward tensors at this timestep
            for next_tag in range(self._tagset_size):
                # broadcast the emission score: it is the same regardless of
                # the previous tag
                emit_score = feat[next_tag].view(1, -1).expand(
                    1, self._tagset_size)
                # the ith entry of trans_score is the score of transitioning to
                # next_tag from i
                trans_score = self._transitions[next_tag].view(1, -1)
                # The ith entry of next_tag_var is the value for the
                # edge (i -> next_tag) before we do log-sum-exp
                next_tag_var = forward_var + trans_score + emit_score
                # The forward variable for this tag is log-sum-exp of all the
                # scores.
                alphas_t.append(
                    torch.logsumexp(next_tag_var.view(1, -1), 1).view(1))
            forward_var = torch.cat(alphas_t).view(1, -1)
        terminal_var = forward_var + self._transitions[self._stop_idx]
        alpha = torch.logsumexp(terminal_var.view(1, -1), 1)
        return alpha

    def _forward_alg(self, feats_batch, lengths_batch):
        """Get CRF result"""
        # feats_batch dim: [batch_size, seq_len, target_dim]
        # lengths_batch dim: [batch_size]
        batch_size = feats_batch.size(0)
        alpha_batch = []

        for i in range(batch_size):
            length = lengths_batch[i]
            feats = feats_batch[i][:length]
            alpha = self._forward_alg_single(feats)
            alpha_batch.append(alpha)
        return torch.stack(alpha_batch).view(-1)

    def _forward_alg_batch(self, feats, lengths):
        """Get CRF result, batch version"""
        # feats dim: [batch_size, seq_len, target_dim]
        # lengths dim: [batch_size]
        # masks dim: [batch_size, seq_len]
        batch_size, seq_len = feats.size()[:2]

        # Do the forward algorithm to compute the partition function
        init_alphas = torch.full((batch_size, 1, self._tagset_size),
                                 NO_TRANS,
                                 requires_grad=False,
                                 device=feats.device)
        # START_TAG has all of the score.
        init_alphas[:, 0, self._start_idx] = 0.

        # Wrap in a variable so that we will get automatic backprop
        forward_var = init_alphas

        # feats dim: [seq_len, batch_size, target_dim]
        feats = feats.transpose(1, 0)
        feats = feats.view(seq_len, batch_size, self._tagset_size, 1)

        trans_score = self._transitions.view(1, self._tagset_size,
                                             self._tagset_size)

        forward_var_batch = []
        for emit_score in feats:
            forward_var = forward_var.view(batch_size, 1, self._tagset_size)
            next_tag_var = forward_var + \
                trans_score + \
                emit_score
            next_tag_var = torch.logsumexp(next_tag_var, dim=2)
            forward_var = next_tag_var
            forward_var_batch.append(forward_var)

        forward_var_batch = torch.stack(forward_var_batch)
        forward_var = forward_var_batch.gather(
            0, (lengths.view(1, batch_size, 1) - 1).expand(
                1, batch_size, self._tagset_size)).squeeze()
        forward_var = forward_var.view(batch_size, -1)

        alpha = forward_var + self._transitions[self._stop_idx]
        alpha = torch.logsumexp(alpha, 1)
        return alpha.view(-1)

    def _score_sentence_single(self, feats, tags):
        # Gives the score of a provided tag sequence
        score = torch.zeros(1, device=feats.device)
        tags = torch.cat([
            torch.tensor([self._start_idx],
                         dtype=torch.long,
                         device=feats.device), tags
        ])
        for i, feat in enumerate(feats):
            score = score + \
                self._transitions[tags[i + 1], tags[i]] + feat[tags[i + 1]]
        score = score + self._transitions[self._stop_idx, tags[-1]]
        return score

    def _score_sentence(self, feats_batch, tags_batch, lengths_batch):
        """Get the gold standard of sentences
        Gives the score of a provided tag sequence
        feats_batch dim: [batch_size, seq_len, target_dim]
        tags_batch dim: [batch_size, seq_len]
        lengths_batch dim: [batch_size]
        """
        batch_size = feats_batch.size(0)
        score_batch = []
        for i in range(batch_size):
            score = torch.zeros(1, device=feats_batch[0].device)
            length = lengths_batch[i]
            feats = feats_batch[i][:length]
            tags = tags_batch[i][:length]
            score = self._score_sentence_single(feats, tags)
            score_batch.append(score)
        score = torch.stack(score_batch).view(-1)
        return score.view(-1)

    def _score_sentence_batch(self, feats, tags, lengths, masks):
        """Get the gold standard of sentences, batch version
        Gives the score of a provided tag sequence
        feats dim: [batch_size, seq_len, target_dim]
        tags dim: [batch_size, seq_len]
        lengths dim: [batch_size]
        masks dim: [batch_size, seq_len]
        """
        batch_size = feats.size(0)
        score = torch.zeros(
            batch_size, requires_grad=True, device=feats.device)
        start = torch.tensor([self._start_idx],
                             dtype=torch.long,
                             device=feats.device).expand(batch_size, 1)
        tags = torch.cat([start, tags], dim=1)
        # feats dim: [seq_len, batch_size, hidden_dim]
        feats = feats.transpose(1, 0)
        for j, feat in enumerate(feats):
            mask = masks[:, j].contiguous().view(batch_size, 1)
            tag_next, tag_cur = tags[:, j + 1], tags[:, j]
            score = score \
                + self._transitions[tag_next, tag_cur] * mask \
                + feat[:, tag_next] * mask
        ends = tags.gather(1, lengths.view(-1, 1))
        trans = self._transitions[self._stop_idx].expand(
            batch_size, self._tagset_size).gather(1, ends.view(-1, 1))
        score = score + trans.view(-1)
        score = score.diag()
        return score.view(-1)

    def _viterbi_decode_single(self, feats):
        backpointers = []

        # Initialize the viterbi variables in log space
        init_vvars = torch.full((1, self._tagset_size),
                                NO_TRANS,
                                device=feats.device)
        init_vvars[0][self._start_idx] = 0

        # forward_var at step i holds the viterbi variables for step i-1
        forward_var = init_vvars
        for feat in feats:
            bptrs_t = []  # holds the backpointers for this step
            viterbivars_t = []  # holds the viterbi variables for this step

            for next_tag in range(self._tagset_size):
                # next_tag_var[i] holds the viterbi variable for tag i at the
                # previous step, plus the score of transitioning
                # from tag i to next_tag.
                # We don't include the emission scores here because the max
                # does not depend on them (we add them in below)
                next_tag_var = forward_var + self._transitions[next_tag]
                best_tag_id = torch.argmax(next_tag_var, 1)[0]
                bptrs_t.append(best_tag_id)
                viterbivars_t.append(next_tag_var[0][best_tag_id].view(1))
            # Now add in the emission scores, and assign forward_var to the set
            # of viterbi variables we just computed
            forward_var = (torch.cat(viterbivars_t) + feat).view(1, -1)
            backpointers.append(bptrs_t)

        # Transition to STOP_TAG
        terminal_var = forward_var + \
            self._transitions[self._stop_idx]
        best_tag_id = torch.argmax(terminal_var, 1)[0]
        path_score = terminal_var[0][best_tag_id]

        # Follow the back pointers to decode the best path.
        best_path = [best_tag_id]
        for bptrs_t in reversed(backpointers):
            best_tag_id = bptrs_t[best_tag_id]
            best_path.append(best_tag_id)
        # Pop off the start tag (we dont want to return that to the caller)
        start = best_path.pop()
        assert start == self._start_idx  # Sanity check
        best_path.reverse()
        return path_score, best_path

    def _viterbi_decode(self, feats_batch, lengths):
        """Inference result
        feats_batch dim: [batch_size, seq_len, target_dim]
        lengths dim: [batch_size]
        """
        batch_size = feats_batch.size(0)
        path_scores, best_paths = [], []
        for i in range(batch_size):
            length = lengths[i]
            feats = feats_batch[i][:length]
            path_score, best_path = self._viterbi_decode_single(feats)
            path_scores.append(path_score)
            best_paths.append(best_path)
        path_scores = torch.stack(path_scores)
        best_paths = np.asarray([np.asarray(x) for x in best_paths])
        return path_scores, best_paths

    def _viterbi_decode_batch(self, feats, lengths, masks):
        """Inference result"""
        # feats dim: [batch_size, seq_len, target_dim]
        batch_size = feats.size(0)

        backpointers = []

        # Initialize the viterbi variables in log space
        # init_vvars dim: [batch_size, tagset_size]
        init_vvars = torch.full((batch_size, self._tagset_size),
                                NO_TRANS,
                                device=feats.device)
        init_vvars[:, self._start_idx] = 0

        # forward_var at step i holds the viterbi variables for step i-1
        forward_var = init_vvars

        # feats dim: [seq_len, batch_size, target_dim]
        feats = feats.transpose(1, 0)
        # feat dim: [batch_size, target_dim]
        bptrs_t = None
        for i, feat in enumerate(feats):
            mask = masks[:, i]
            # bptrs_t_old = bptrs_
            bptrs_t = []  # holds the backpointers for this step
            viterbivars_t = []  # holds the viterbi variables for this step

            for next_tag in range(self._tagset_size):
                # next_tag_var[i] holds the viterbi variable for tag i at the
                # previous step, plus the score of transitioning
                # from tag i to next_tag.
                # We don't include the emission scores here because the max
                # does not depend on them (we add them in below)
                # next_tag_var dim: [batch_size, tagset_size]
                next_tag_var = forward_var + self._transitions[next_tag].view(
                    1, -1).expand(batch_size, self._tagset_size)
                best_tag_id = torch.argmax(next_tag_var, 1)
                bptrs_t.append(best_tag_id.view(1, -1))
                tmp = next_tag_var.gather(1, best_tag_id.view(-1, 1)).squeeze()
                viterbivars_t.append(tmp.view(1, batch_size))
            # Now add in the emission scores, and assign forward_var to the set
            # of viterbi variables we just computed
            # forward_var dim: [batch_size, tagset_size]
            tmp = torch.cat(viterbivars_t)
            tmp = tmp.permute(1, 0)
            tmp_new_forward_var = (tmp + feat).view(batch_size, -1)

            mask_table = mask.view(-1, 1).expand(-1, self._tagset_size)
            forward_var = tmp_new_forward_var * mask_table + forward_var * (
                mask_table - 1).abs()

            bptrs_t = torch.cat(bptrs_t)

            backpointers.append(bptrs_t)

        # Transition to STOP_TAG
        # terminal_var dim: [1, tagset_size]
        terminal_var = forward_var + \
            self._transitions[self._stop_idx]
        best_tag_id = torch.argmax(terminal_var, 1)
        path_score = [terminal_var[i][x] for i, x in enumerate(best_tag_id)]

        # Follow the back pointers to decode the best path.
        backpointers = torch.stack(backpointers)
        # backpointers dim: [seq_len, batch_size, tagset_size]
        backpointers = backpointers.permute(0, 2, 1)
        # print('backpointers', backpointers.size())
        best_path = [best_tag_id]
        for bptrs_t in reversed(backpointers):
            if batch_size > 1:
                best_tag_id = bptrs_t.gather(1, best_tag_id.view(-1,
                                                                 1)).squeeze()
                best_path.append(best_tag_id)
            else:
                best_tag_id = bptrs_t[0][best_tag_id]
                best_path.append(best_tag_id)
        # Pop off the start tag (we dont want to return that to the caller)
        # best_path.pop()
        # check start
        start = best_path.pop()
        assert np.sum(start.cpu().detach().numpy() -
                      np.array([self._start_idx] * batch_size)) <= 1e-5
        best_path.reverse()

        path_score = torch.stack(path_score)
        best_path = torch.stack(best_path)
        best_path = best_path.permute(1, 0).cpu().detach().numpy()
        best_path = np.asarray(
            [np.asarray(x[:i]) for i, x in zip(lengths, best_path)])

        return path_score, best_path

    def compute_loss(self, encoder_output, tags, lengths):
        """Calculate loss
        encoder_output dim: [batch_size, seq_len, embedding_dim]
        tags dim: [batch_size, seq_len]
        lengths dim: [batch_size]
        """

        seq_len = encoder_output.size(1)
        masks = sequence_mask(lengths, seq_len)

        forward_score = self._forward_alg_batch(encoder_output, lengths)
        gold_score = self._score_sentence_batch(encoder_output, tags, lengths,
                                                masks)

        loss = torch.sum(forward_score) - torch.sum(gold_score)
        # loss = loss / batch_size
        return loss

    def forward(self, encoder_output, lengths, masks):
        return self._viterbi_decode_batch(encoder_output, lengths, masks)
