# -*- coding: utf-8 -*-
from sklearn.svm import SVC
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA

def ClassifierTrain(train_x, train_y, classifier_type):
    """
       训练LDA/SVM，生成分类模型

       输入参数
       ----------
       train_x: array-like, shape (n_samples, n_features)
                L×2m   空间滤波后的数据samples
                L: 训练数据trial总数  m: CSP 阶数
       train_y: array-like, shape (n_samples,)
                L 个trial对应的标签
        classifier_type: 训练模型 svm 或者lda

       返回值
       ----------
       svmModel: object

       """
    if classifier_type == 'svm':
        model = SVC(kernel='rbf', probability=True)
        model.fit(train_x, train_y)
    elif classifier_type == 'lda':
        model = LDA()
        model.fit(train_x, train_y)
    return model
