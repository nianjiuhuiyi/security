import os
import tqdm
import pandas as pd
import numpy as np

excel_path = r"D:\SH\temp_excel"
excels_name = os.listdir(excel_path)
counts = 0

# 用来记录空的公司(有17个)
empty_company = []

results = pd.DataFrame()
for excel_name in tqdm.tqdm(excels_name):
    abs_excel_path = os.path.join(excel_path, excel_name)
    dataFrame = pd.read_excel(abs_excel_path)
    if not dataFrame.empty:
        results = pd.concat([results, dataFrame], ignore_index=True)
    else:
        code, name = excel_name.replace(".xlsx", "").split("_")
        empty_company.append((code, name))
# 当存有为空的公司列表里有值时再做处理
if empty_company:
    empty_company = np.asarray(empty_company)
    empty_dataFrame = pd.DataFrame({"code": empty_company[:, 0], "company": empty_company[:, 1]})
    print(empty_dataFrame)
    results = pd.concat([results, empty_dataFrame], ignore_index=True)

results.to_excel("./sh_results.xlsx")
print("Done!")
