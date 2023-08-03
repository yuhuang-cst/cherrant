# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: Yu Huang
# @Email: yuhuang-cst@foxmail.com

import argparse
from typing import List, Dict, Union

from cherrant.modules.annotator import Annotator
from cherrant.modules.tokenizer import Tokenizer
from cherrant.compare_m2_for_evaluation import calculate_metric, processCategories, computeFScore

class Evaluator(object):
    def __init__(self, m2_convert_kwargs: Union[Dict, None] = None, m2_compare_kwargs: Union[Dict, None] = None):
        """
        :param m2_convert_kwargs: call `get_default_m2_convert_kwargs()` for details
        :param m2_compare_kwargs: call `get_default_m2_compare_kwargs()` for details
        """
        self.m2_convert_args = self.check_m2_convert_kwargs(m2_convert_kwargs)
        self.m2_compare_args = self.check_m2_compare_kwargs(m2_compare_kwargs)
        self.tokenizer = Tokenizer(
            self.m2_convert_args.granularity, self.m2_convert_args.device,
            self.m2_convert_args.segmented, self.m2_convert_args.bpe)
        self.annotator = Annotator.create_default(self.m2_convert_args.granularity, self.m2_convert_args.multi_cheapest_strategy)
        self.cc = self.init_open_cc(self.m2_convert_args)


    @staticmethod
    def get_default_m2_convert_kwargs():
        from cherrant.parallel_to_m2 import parse_args
        args = parse_args()
        return vars(args)


    def check_m2_convert_kwargs(self, kwargs):
        ret_kwargs = self.get_default_m2_convert_kwargs()
        if kwargs is not None:
            for k, v in kwargs.items():
                assert k in ret_kwargs, f'Unexpected para for m2_convert_kwargs: {k}'
                ret_kwargs[k] = v
        return argparse.Namespace(**ret_kwargs)


    @staticmethod
    def get_default_m2_compare_kwargs():
        from cherrant.compare_m2_for_evaluation import parse_args
        args = parse_args()
        return vars(args)


    def check_m2_compare_kwargs(self, kwargs):
        ret_kwargs = self.get_default_m2_compare_kwargs()
        if kwargs is not None:
            for k, v in kwargs.items():
                assert k in ret_kwargs, f'Unexpected para for m2_compare_kwargs: {k}'
                ret_kwargs[k] = v
        return argparse.Namespace(**ret_kwargs)


    def init_open_cc(self, m2_convert_args):
        cc = None
        if not m2_convert_args.no_simplified:
            from opencc import OpenCC
            cc = OpenCC("t2s")
        return cc


    def process_source_text(self, text, args):
        if args.segmented:
            text = text.strip()
        else:
            text = "".join(text.strip().split())
        return text


    def process_target_text(self, text, args):
        if args.segmented:
            # print(sent)
            text = text.strip()
        else:
            text = "".join(text.split()).strip()
        if not args.no_simplified:
            text = self.cc.convert(text)
        return text


    def __convert_single_to_m2(self, source: str, targets: List[str], sentence_to_tokenized: Dict[str, List[str]]) -> str:
        """
        :param source: input text
        :param target: target texts
        :param sentence_to_tokenized: {text: [token1, token2, ...]}
        :param target_idx:
        :return: str
        """
        output_str = ''
        for target_idx, target in enumerate(targets):
            source_tokenized, target_tokenized = sentence_to_tokenized[source], sentence_to_tokenized[target]
            out, cors = self.annotator(source_tokenized, target_tokenized, target_idx)
            if target_idx == 0:
                output_str += "".join(out[:-1])
            else:
                output_str += "".join(out[1:-1])
        return output_str.strip()


    def check_targets_list(self, targets_list: List[Union[List[str], str]]):
        ret_list = []
        for targets in targets_list:
            if isinstance(targets, str):
                ret_list.append([targets])
            ret_list.append(targets)
        return ret_list


    def convert_multi_to_m2(self, sources: List[str], targets_list: List[Union[List[str], str]]) -> List[str]:
        """
        :param sources: input texts; length=n_samples
        :param targets: target texts list; length=n_samples
        :return: m2_strs; length=n_samples
        """
        assert len(sources) == len(targets_list)
        sources = [self.process_source_text(source, self.m2_convert_args) for source in sources]
        targets_list = self.check_targets_list(targets_list)
        targets_list = [[self.process_target_text(target, self.m2_convert_args) for target in targets] for targets in targets_list]

        sentences = set()
        for source, targets in zip(sources, targets_list):
            sentences.add(source)
            sentences.update(targets)
        sentences = list(sentences)

        sentence_to_tokenized = {}
        n_sents, batch_size = len(sentences), self.m2_convert_args.batch_size
        for i in range(0, n_sents, batch_size):
            sents_batch = sentences[i: i+batch_size]
            results = self.tokenizer(sents_batch)
            for s, r in zip(sents_batch, results):
                sentence_to_tokenized[s] = r  # Get tokenization map.

        ret_list = []
        for source, targets in zip(sources, targets_list):
            ret_list.append(self.__convert_single_to_m2(source, targets, sentence_to_tokenized))
        return ret_list


    def get_sub_metric_dict(self, tp, fp, fn, betas_list):
        ret_dict = {'tp': tp, 'fp': fp, 'fn': fn, 'support': tp + fn}
        for beta in betas_list:
            p, r, f = computeFScore(tp, fp, fn, beta)
            ret_dict['precision'] = p
            ret_dict['recall'] = r
            ret_dict[f'f{beta}'] = f
        return ret_dict


    def evaluate_m2(self, m2_true: List[str], m2_pred: List[str], betas_list: Union[List[float], None] = None) -> Dict:
        """
        :param m2_true: [m2_str, ...]; length=n_samples
        :param m2_pred: [m2_str, ...]; length=n_samples
        :param betas_list: for each beta, calculate a fbeta-score; if None, use m2_compare_args.beta
        :return: {
            '{category}': {
                'precision': float,
                'recall': float,
                'f{beta}-score': float,
                'support': int,
            },
            'precision': float,
            'recall': float,
            'f{beta}-score': float,
            'support': int,
        }
        """
        ret_dict = {}
        args = self.m2_compare_args
        if betas_list is None:
            betas_list = [args.beta]
        best_dict, best_cats = calculate_metric(m2_true, m2_pred, self.m2_compare_args)
        if args.cat:
            best_cats = processCategories(best_cats, args.cat)
            for cat, cnts in sorted(best_cats.items()):
                ret_dict[cat] = self.get_sub_metric_dict(cnts[0], cnts[1], cnts[2], betas_list)
        ret_dict.update(self.get_sub_metric_dict(best_dict["tp"], best_dict["fp"], best_dict["fn"], betas_list))
        return ret_dict


    def evaluate(self, sources: List[str], targets_true: List[Union[List[str], str]],
                 targets_pred: List[Union[List[str], str]], betas_list: Union[List[float], None] = None) -> Dict:
        """
        :param sources: input texts; length=n_samples
        :param targets_true: target texts list; length=n_samples
        :param targets_pred: target texts list; length=n_samples
        :param betas_list: for each beta, calculate a fbeta-score; if None, use m2_compare_args.beta
        :return: {
            '{category}': {
                'precision': float,
                'recall': float,
                'f{beta}-score': float,
                'support': int,
            },
            'precision': float,
            'recall': float,
            'f{beta}-score': float,
            'support': int,
        }
        """
        m2_true = self.convert_multi_to_m2(sources, targets_true)
        m2_pred = self.convert_multi_to_m2(sources, targets_pred)
        return self.evaluate_m2(m2_true, m2_pred, betas_list=betas_list)


def evaluation_report(sources: List[str], targets_true: List[Union[List[str], str]],
                      targets_pred: List[Union[List[str], str]], betas_list: Union[List[float], None] = None,
                      m2_convert_kwargs: Union[Dict, None] = None, m2_compare_kwargs: Union[Dict, None] = None) -> Dict:
    """
    :param sources: input texts; length=n_samples
    :param targets_true: target texts list; length=n_samples
    :param targets_pred: target texts list; length=n_samples
    :param betas_list: for each beta, calculate a fbeta-score; if None, use m2_compare_args.beta
    :param m2_convert_kwargs: call `get_default_m2_convert_kwargs()` for details
    :param m2_compare_kwargs: call `get_default_m2_compare_kwargs()` for details
    :return: {
        '{category}': {
            'precision': float,
            'recall': float,
            'f{beta}-score': float,
            'support': int,
        },
        'precision': float,
        'recall': float,
        'f{beta}-score': float,
        'support': int,
    }
    """
    evaluator = Evaluator(m2_convert_kwargs=m2_convert_kwargs, m2_compare_kwargs=m2_compare_kwargs)
    return evaluator.evaluate(sources, targets_true, targets_pred, betas_list=betas_list)


get_default_m2_convert_kwargs = Evaluator.get_default_m2_convert_kwargs
get_default_m2_compare_kwargs = Evaluator.get_default_m2_compare_kwargs

if __name__ == '__main__':
    evaluator = Evaluator()
    print('get_default_m2_convert_kwargs', evaluator.get_default_m2_convert_kwargs())
    print('get_default_m2_compare_kwargs', evaluator.get_default_m2_compare_kwargs())

