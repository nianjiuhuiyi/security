import os
import shutil
import pandas as pd


"""
    用来获取那些值为-1，即无法直接转换的pdf，将其集中复制到一个地方
"""


total_save_path = r"C:\Users\Administrator\Desktop\123"

original_pdf_path = [r"D:\SZ\temp_data", r"H:\SH\temp_data"]  # 深圳、上海对应的pdf路径
original_txt_path = [r"D:\SZ\temp_txt", r"H:\SH\temp_txt"]    # 深圳、上海对应的txt路径

excels_path = [r"./for_re_sz/sz_results.xlsx", r"./for_re_sh/sh_results.xlsx"]

city_name = ["SZ", "SH"]

for index, excel_path in enumerate(excels_path):
    df = pd.read_excel(excel_path, converters={"code": str})

    df = df[df["汇率衍生工具"] == -1]
    df = df[["code", "company", "pdf"]]
    df.reset_index(drop=True, inplace=True)

    for i in range(df.shape[0]):
        com_code = df.loc[i, "code"]
        com_name = df.loc[i, "company"]
        pdf_name = df.loc[i, "pdf"]
        folder_name = com_code + "_" + com_name

        des_pdf_path = os.path.join(total_save_path, city_name[index], "temp_data", folder_name)  # pdf的目的路径
        des_txt_path = os.path.join(total_save_path, city_name[index], "temp_txt", folder_name)  # txt的目的路径
        os.makedirs(des_pdf_path, exist_ok=True)
        os.makedirs(des_txt_path, exist_ok=True)

        # 开始复制
        abs_pdf_path = os.path.join(original_pdf_path[index], folder_name, pdf_name)
        abs_txt_path = os.path.join(original_txt_path[index], folder_name, pdf_name.replace(".pdf", ".txt"))
        shutil.copy(abs_pdf_path, des_pdf_path)
        shutil.copy(abs_txt_path, des_txt_path)

print("Done!")
