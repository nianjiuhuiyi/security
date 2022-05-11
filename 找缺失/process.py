import pandas as pd

excel_path = r"./回归总表(1).xlsx"
df = pd.read_excel(excel_path, converters={"Stkcd": str})

for key, group_df in df.groupby(by=["Stkcd"]):
    all_times = group_df["time"].tolist()  # 季度的列表
    first = all_times[0]
    last = all_times[-1]

    true_nums = (int(last[:4]) - int(first[:4]) + 1) * 4
    if first[4:] == "Q4":
        true_nums -= 3
    elif first[4:] == "Q3":
        true_nums -= 2
    elif first[4:] == "Q2":
        true_nums -= 1
    else:
        pass
    # 把有缺失的打印出来
    if len(all_times) != true_nums:
        print(key)
        print(all_times)

