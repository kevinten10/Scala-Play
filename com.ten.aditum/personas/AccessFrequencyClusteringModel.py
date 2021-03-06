"""
基于访问时间AccessTime[注册天数,每天访问频率]的聚类分析，用于分析用户组类型
"""
import logging

from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import base64
import os
from api import BackRemoteApi

# 保存的临时分析图片的名字
image_path = os.getcwd() + '\\accessFrequencyClustering.png'

# 日期权重增加
day_count_power = 5

# 聚类中心
clustering = 4

# 1展示图片 0不展示
show = 0

# 1打印日志 0不打印
enableLog = 0


def initPersonData():
    """
    获取person数据
    """
    personList = BackRemoteApi.getForAllPerson()
    return personList


def initAccessTimeData(personList):
    """
    获取accessTime数据
    """
    personAccessTimeList = []
    for person in personList:
        personAccessTime = BackRemoteApi.getForAccessTimeByPersonId(person.personnelId)
        if personAccessTime is not None:
            personAccessTimeList.append(personAccessTime)
    return personAccessTimeList


def initEntitySet(personAccessTimeList):
    """
    初始化聚类数据集
    :param personAccessTimeList: 用户时间行为数据
    :return: 二维矩阵 [[],[]...], 用户ID一维数组
    """
    frequencyEntitySet = []
    personnelIdSet = []
    # 数据集
    for personAccessTime in personAccessTimeList:
        personnelId = personAccessTime.personnelId
        count = personAccessTime.averageDailyFrequencyCount
        frequency = personAccessTime.averageDailyFrequency
        # 权重升级: 天数*day_count_power
        count *= day_count_power
        # 添加数据集
        frequencyEntity = [count, frequency]
        frequencyEntitySet.append(frequencyEntity)
        personnelIdSet.append(personnelId)
    return frequencyEntitySet, personnelIdSet


def kmeansClustering(entitySet, n_clusters=3):
    """
    对二维矩阵进行K-means聚类
    """
    # 聚类算法，参数n_clusters=x，聚成x类
    clf = KMeans(n_clusters=n_clusters)
    # 直接对数据进行聚类，聚类不需要进行预测
    y_pred = clf.fit_predict(entitySet)
    # print(type(clf.labels_))
    return y_pred


def showAndSave(entitySet, y_pred, show=0):
    """
    根据聚类结果展示散点图
    :param entitySet: 聚类数据
    :param y_pred: 聚类结果
    :return: 图片
    """
    xData = [n[0] for n in entitySet]
    yData = [n[1] for n in entitySet]
    plt.scatter(xData, yData, c=y_pred, marker='x')
    plt.title("user access frequency clustering")
    plt.xlabel("use count * " + str(day_count_power))
    plt.ylabel("use frequency")
    plt.savefig(image_path)
    # 图片展示
    if show != 0:
        plt.show()


def base64img():
    """
    返回刚刚保存的图片的base64字符串
    :return: base64
    """
    with open(image_path, "rb") as f:
        # b64encode是编码，b64decode是解码
        base64_data = base64.b64encode(f.read())
        # base64.b64decode(base64data)
        # print(base64_data)
        return base64_data


def run():
    """
    执行脚本，并返回图片的base64字符串
    :return: base64图片字符串
    """
    # print("用户门禁使用依赖度聚类分析...开始")

    # Person集合
    personList = initPersonData()
    # print(personList)

    # PersonAccessTime集合
    personAccessTimeList = initAccessTimeData(personList=personList)
    # print(personAccessTimeList)

    # print("数据获取成功，开始分析...")

    # 初始化数据集
    frequencyEntitySet, personnelIdSet = initEntitySet(personAccessTimeList)

    # 聚类分析
    y_pred = kmeansClustering(frequencyEntitySet, clustering)

    # 可视化结果并保存图片
    showAndSave(frequencyEntitySet, y_pred, show=show)

    if enableLog != 0:
        print("用户门禁使用依赖度聚类分析...结束")
        for i in range(len(y_pred)):
            print(personnelIdSet[i] + " " + str(y_pred[i]))

    # base64
    base64 = base64img()
    print(base64)
    return base64


# Java runtime invoke
run()
