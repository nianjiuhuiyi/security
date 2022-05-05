import pandas as pd

excel_path = r"./包含大陆的删选(2)(1).xlsx"
df = pd.read_excel(excel_path, converters={"Symbol": str, "Sgnrgn": str})

"""这一行是把地区为中国的数据删掉来统计（第一种方式不要这行，第二种要这行）
第一个是包括所有的数据。一个是在这个表里剔除Sgnrgn（区域标识）为3的数据。"""
df = df[~df["Sgnrgn"].isin(["3"])]


datas = list()
for keys, group_df in df.groupby(by=["Symbol", "Year "]):
    area_names = group_df["AreaName"].unique()
    k = area_names.size
    all_sub_j = group_df.shape[0]  # 总的机构数
    geoscope = 1
    for area_name in area_names:
        sub_j = group_df[group_df["AreaName"].isin([area_name])].shape[0]
        geoscope -= ((sub_j / all_sub_j) ** 2)
    datas.append([*keys, geoscope])
results = pd.DataFrame(datas, columns=["Symbol", "Year", "Geoscope"])
results.to_excel("result_不包含中国.xlsx", index=False)
print("Done!")
