import tqdm
import os
import pandas as pd
import numpy as np

DATE_LI = ['2014-03', '2014-06', '2014-09', '2014-12', '2015-03', '2015-06', '2015-09', '2015-12', '2016-03',
           '2016-06', '2016-09', '2016-12', '2017-03', '2017-06', '2017-09', '2017-12', '2018-03', '2018-06',
           '2018-09', '2018-12']


def filter_date(a_date):
    year, mon, day = a_date.split("-")
    # 2009年只要1月
    if year == "2009":
        need_mons = [1, 3, 6, 9, 12]
    else:
        need_mons = [3, 6, 9, 12]

    if int(mon) in need_mons:
        return year + "-" + mon
    return "del"


excel_name = r"./2014-2018.xlsx"
df = pd.read_excel(excel_name, converters={"Stkcd": str})

# 只保留 1、3、6、9、12月的数据
# 添加一列date，只要 年-月,同时把不要的数据做个标记
df["date"] = df["Trddt"].apply(filter_date)
# 删掉不要的数据
df = df[~df["date"].isin(["del"])]

result_data = None
# 聚合，按公司去重
grouped = df.groupby(by="Stkcd")
for key, grouped_values in tqdm.tqdm(grouped, desc="进度："):

    # 去重，保留每月最后一个值(就是最大的值)
    grouped_values = grouped_values.drop_duplicates(subset=["date"], keep="last")

    grouped_values = pd.DataFrame(grouped_values.values, columns=grouped_values.columns)

    # 有缺失值的就进去补充
    if grouped_values.shape[0] != len(DATE_LI):
        append_dates = set(grouped_values["date"].tolist()) ^ set(DATE_LI)
        insert_data = [[key, "#N/A", "#N/A", append_date] for append_date in append_dates]

        grouped_values = pd.DataFrame(np.concatenate((grouped_values.values, np.asarray(insert_data)), axis=0),
                                      columns=grouped_values.columns)

        # 按时间排序
        grouped_values.sort_values(by="date", inplace=True)
        # index重新排一下
        grouped_values.reset_index(drop=True, inplace=True)

    if result_data is None:
        result_data = grouped_values.values
    else:
        result_data = np.concatenate((result_data, grouped_values.values), axis=0)

result_df = pd.DataFrame(result_data, columns=["Stkcd", "Trddt", "Adjprcwd", "date"])
result_df = result_df.reindex(columns=["Stkcd", "date", "Trddt", "Adjprcwd"])
save_name = os.path.splitext(excel_name)[0] + "_result.xlsx"
result_df.to_excel(save_name, index=False)
print("Done!")
