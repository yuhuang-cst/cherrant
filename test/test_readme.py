# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: Yu Huang
# @Email: yuhuang-cst@foxmail.com

if __name__ == '__main__':
    # Use evaluation_report to get metric dict
    from cherrant import get_default_m2_convert_kwargs, get_default_m2_compare_kwargs
    sources = [
        '冬阴功是泰国最著名的菜之一，它虽然不是很豪华，但它的味确实让人上瘾，做也不难、不复。',
        '首先，我们得准备：大虾六到九只、盐一茶匙、已搾好的柠檬汁三汤匙、泰国柠檬叶三叶、柠檬香草一根、鱼酱两汤匙、辣椒6粒，纯净水4量杯、香菜半量杯和草菇10个。',
        '这样，你就会尝到泰国人死爱的味道。',
        '另外，冬阴功对外国人的喜爱不断地增加。',
        '这部电影不仅是国内，在国外也很有名。',
    ]
    targets_true = [
        '冬阴功是泰国最著名的菜之一，虽然它不是很豪华，但它的味确实让人上瘾，做法也不难、不复杂。',
        '首先，我们得准备:大虾六到九只、盐一茶匙、已榨好的柠檬汁三汤匙、泰国柠檬叶三叶、柠檬香草一根、鱼酱两汤匙、辣椒六粒，纯净水四量杯、香菜半量杯和草菇十个。',
        '这样，你就会尝到泰国人爱死的味道。',
        '另外，外国人对冬阴功的喜爱不断地增加。',
        ['这部电影不仅是在国内，在国外也很有名。', '这部电影不仅在国内，在国外也很有名。'],
    ]
    targets_pred = [
        '冬阴功是泰国最著名的菜之一，它虽然不是很豪华，但它味道确实让人上瘾，做法也不难、不复杂。',
        '首先，我们得准备：大虾六到九只、盐一茶匙、已搾好的柠檬汁三汤匙、泰国柠檬叶三叶、柠檬香草一根、鱼酱两汤匙、辣椒6粒，纯净水4量杯、香菜半量杯和草菇10个。',
        '这样，你就会尝到泰国人死爱的味道。',
        '另外，冬阴功对外国人的喜爱也不断地增加。',
        '这部电影不仅是在国内，在国外也很有名。',
    ]
    m2_convert_kwargs = get_default_m2_convert_kwargs()
    m2_compare_kwargs = get_default_m2_compare_kwargs()
    print(f'========= m2_convert_kwargs =========\n{m2_convert_kwargs}')
    print(f'========= m2_compare_kwargs =========\n{m2_compare_kwargs}')
    m2_compare_kwargs['cat'] = True

    # Use evaluation_report to get metric dict
    from cherrant import evaluation_report
    metric_dict = evaluation_report(sources, targets_true, targets_pred, m2_convert_kwargs=m2_convert_kwargs, m2_compare_kwargs=m2_compare_kwargs, betas_list=[0.5, 1])
    print(f'========= metric_dict =========\n{metric_dict}')

    # Use Evaluator to get details
    from cherrant import Evaluator
    evaluator = Evaluator(m2_convert_kwargs, m2_compare_kwargs)
    m2_true = evaluator.convert_multi_to_m2(sources, targets_true)
    m2_pred = evaluator.convert_multi_to_m2(sources, targets_pred)
    metric_dict = evaluator.evaluate_m2(m2_true, m2_pred, betas_list=[0.5, 1])
    print(f'========= m2_true =========\n{m2_true}')
    print(f'========= m2_pred =========\n{m2_pred}')
    print(f'========= metric_dict =========\n{metric_dict}')

