import pandas as pd
import numpy as np


def check():
    """这是将年份你不连续的数据打印出来,,拿来单独使用"""
    excel_path = r"./经营活动现金流量(1).xlsx"
    df = pd.read_excel(excel_path, converters={"Stkcd": str})

    df["year"] = df["year"].apply(lambda x: int(x[:4]))
    for key, group_df in df.groupby(by=["Stkcd"]):
        years = group_df["year"].unique().tolist()
        # 最后一个年份减去第一个年份的值，== 这个时间列表的长度-1 就代表是连续的
        if (len(years) - 1) != (years[-1] - years[0]):
            print(key, years)


def cal_std(dataFrame: pd.DataFrame, step=8):
    """
    传进来的数据，一个求标准差的函数
    :param dataFrame:
    :param step: step个为一组来求标准差，默认为8
    :return: 处理完结果的一个list
    """
    datas = list()
    for key, group_df in dataFrame.groupby(by=["Stkcd"]):
        # group_df = group_df[:-7]  # 去掉最后的7行数据
        group_df.reset_index(drop=True, inplace=True)  # 每个分组都把索引从0开始从新来过

        for i in range(group_df.shape[0]):
            # 最后不足8个那些数据就不要了
            if i + step > group_df.shape[0]:
                break
            time_name = group_df.loc[i, "time"]  # 类似于这种 2009Q1、2009Q2、2009Q3
            # 一定要注意pandas，df.loc[0: 8] ,它是能取到索引为8的那列的，那这里就会有9个值，而不是想象中的8个值
            # 标注差
            std_money = np.std(group_df.loc[i: i + step - 1, "经营活动现金流量"], ddof=1)  # 给了后面这个参数才是 /(n-1)  不然是 /n
            datas.append((key, group_df.loc[0, "name"], time_name, std_money))
    return datas


""" 下面是进行标准差的计算 """
# excel_path = r"./123.xlsx"
excel_path = r"./现金流量波动.xlsx"
df = pd.read_excel(excel_path, converters={"Stkcd": str})

# # 年份从小到大的加stp，函数中默认为8
data_asc = cal_std(df)
result_asc = pd.DataFrame(data_asc, columns=["Stkcd", "name", "time", "往后两年经营现金流标准差"])
result_asc.to_excel("result_asc.xlsx", index=False)

# 年份从大往小，每次加stp，函数中默认为8
data_desc = cal_std(df[::-1])
result_desc = pd.DataFrame(data_desc, columns=["Stkcd", "name", "time", "往前两年经营现金流标准差"])
result_desc.to_excel("result_desc.xlsx", index=False)
print("Done!")

