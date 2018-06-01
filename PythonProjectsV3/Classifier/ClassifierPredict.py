# -*- coding: utf-8 -*-

def ClassifierPredict(model, test_x):
    """
       根据SVM分类模型对测试数据进行分类

       输入参数
       ----------
       model: object
       test_x: array-like, shape (n_samples, n_features)
               L×2m   空间滤波后的数据
               L: 训练数据trial总数  m: CSP 阶数
       返回值
       ----------
       predict_y: 1 维 L 个
                  L个trial对应的预测标签

       """
    predict_y = model.predict(test_x)

    return predict_y