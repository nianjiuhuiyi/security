import os
import time
import requests
import multiprocessing
import pandas as pd


def download(save_path, excel_path):
    dataFrame = pd.read_excel(excel_path, converters={"code": str})
    folder_name = dataFrame.loc[0, "code"] + "_" + dataFrame.loc[0, "company"]
    save_path = os.path.join(save_path, folder_name)
    os.makedirs(save_path, exist_ok=True)
    for i in range(dataFrame.shape[0]):
        file_name = dataFrame.loc[i, "pdf"]
        url = dataFrame.loc[i, "url"]
        abs_file_path = os.path.join(save_path, file_name)
        result = requests.get(url, stream=True)
        try:
            with open(abs_file_path, "wb") as fp:
                for chunk in result.iter_content(chunk_size=10240):
                    if chunk:
                        fp.write(chunk)
        except:
            pass
    print("{} 下载完毕！".format(dataFrame.loc[0, "code"]))


if __name__ == '__main__':
    """
    这是第二步：根据读取到的url进行对应的pdf下载
    """
    begin = time.time()
    save_path = r"D:\SZ\temp_data"
    all_excel_path = r"E:\PycharmProject\PDF2TXT\for_re_SZ\download_urls"
    execl_names = os.listdir(all_excel_path)
    pool = multiprocessing.Pool(5)
    for execl_name in execl_names:
        excel_path = os.path.join(all_excel_path, execl_name)
        pool.apply_async(download, args=(save_path, excel_path))
    pool.close()
    pool.join()
    print("ALL IS DONE!")
    end = time.time()
    print("总用时：{:.2f} 分钟".format(end - begin))
