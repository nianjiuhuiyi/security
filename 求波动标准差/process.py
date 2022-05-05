import pandas as pd

excel_path = r"./经营活动现金流量(1).xlsx"
df = pd.read_excel(excel_path, converters={"Stkcd": str})

# # 这是将年份你不连续的数据打印出来
# df["year"] = df["year"].apply(lambda x: int(x[:4]))
# for key, group_df in df.groupby(by=["Stkcd"]):
#     years = group_df["year"].unique().tolist()
#     if (len(years) - 1) != (years[-1] - years[0]):
#         print(key, years)


for key, group_df in df.groupby(by=["Stkcd"]):
    # group_df = group_df[:-7]  # 去掉最后的7行数据
    group_df.reset_index(drop=True, inplace=True)  # 每个分组都把索引从0开始从新来过
    print(group_df)

    # exit()
