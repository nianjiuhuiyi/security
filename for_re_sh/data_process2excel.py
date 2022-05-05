import os
import re
import time
import tqdm
import pandas as pd
import multiprocessing
from termcolor import colored


# 汇率衍生工具的关键词
# ex_rate_keywords = ["套期保值", "衍生品", "外汇衍生品", "期权", "外汇期货", "无本金交割远期外汇交易"]  # 第一次的
ex_rate_keywords = ["套期保值", "衍生品", "外汇衍生品", "期权", "外汇期货", "无本金交割远期外汇交易", "外汇套期", "期货",
                    "远期合约", "外汇远期", "外汇掉期", "货币互换", "货币掉期", "NDF", "外汇期权"]    # 第二次的
# 外币债务关键词
# debt_keywords = ["外币债务", "美元债务", "日元债务", "英镑债务", "欧元债务", "港元债务"]   # 第一次
debt_type = ["债务", "借款", "贷款"]   # 第二次(找打这符合的，以及其前面的两个字)
currency_name = ["外币", "澳元", "澳门元", "澳门币", "港币", "港元", "美元", "欧元", "日元", "英镑", "新加坡币", "新币", "马来西亚币",
             "马来币", "马币", "令吉", "俄罗斯卢布", "卢布", "加拿大元", "加元", "印尼盾", "韩元", "新台币", "巴西雷亚尔",
             "基纳", "基普", "老挝基普", "加纳赛地", "林吉特", "卢比", "印度卢比", "印尼卢比", "孟加拉塔卡", "缅甸元", "缅元",
             "瑞士法郎", "苏姆", "台币", "泰国铢", "泰铢", "文币", "阿根廷比索", "澳币", "澳大利亚元", "澳洲元", "荷兰盾",
             "瑞士法郎", "瑞郎"]
debt_keywords = [x+y for x in currency_name for y in debt_type]


def check(txt_file_path, keywords):
    """
    匹配日文中是否出现了指定的关键词
    @param txt_file_path: 一个txt文本的结对路径
    @param keywords: 一个list，包含要查找的关联词
    @return: 一个字典，key为-1或0或1，value可能为空或匹配到的所有关键词组成的字符串
    """
    flag = -1  # 默认是没有数据，-1就代表None
    result = []  # 用于存储匹配到的值

    # 只有当文件大于5k时才能进去判断有无关键字，从而返回0或者1
    if os.path.getsize(txt_file_path) > (5 * 1024):
        file = open(txt_file_path, "r", encoding="utf-8")
        data = file.read()
        file.close()
        data = data.replace(" ", "").replace("\n", "").replace("\t", "")

        # 循环检查每个关键词
        for ptn in keywords:
            re_out = re.search(ptn, data)
            if re_out:
                result.append(ptn)
                flag = 1  # 匹配到了后就将其置为1
        # 文件存在，但没匹配到就置为0
        if not result:
            flag = 0
    return {flag: sorted(result)}


def a_company(abs_info_excel_path, txt_path, save_path):
    info_excel_name = os.path.basename(abs_info_excel_path)  #
    # 保存的excel的绝对路径
    abs_excel_path = os.path.join(save_path, info_excel_name)

    df = pd.read_excel(abs_info_excel_path)
    # 如果DataFrame为空，代表没有查到此公司的数据
    if df.empty:
        df.to_excel(abs_excel_path)
        return

    # 去重(有看到pdf名字完全一样的两行，只是在具体日期上有所不同,保留最后一个)（这一行应该不用了，在第一步下载那里就过滤了）
    # df.drop_duplicates(["pdf"], keep="last", inplace=True)

    # 当年份一样，type名字一样，如果有两个及以上的pdf，那size大的那个全是全部报告，小的那个就只有正文部分
    drop_pdfs = []  # 获取到去去掉的pdf的名字
    next_pdf_path = os.path.join(total_pdf_path, info_excel_name.split(".")[0])
    for key, value in df.groupby(by=["year", "type"]):
        pdf_list = value["pdf"].tolist()
        if len(pdf_list) == 1:
            continue
        biggest_pdf = pdf_list[0]
        for a_pdf_name in pdf_list[1:]:
            abs_pdf_1 = os.path.join(next_pdf_path, biggest_pdf)
            abs_pdf_2 = os.path.join(next_pdf_path, a_pdf_name)
            # 第一个pdf(即biggest_pdf)不存在的话，直接就把第二个pdf给biggest_pdf，
            # continue后，再进循环，原来的第二个pdf就成了第一个pdf，也做一次存在与否的判定
            # （如果pdf_list这个列表里的pdf本地都没有的话，最后得到的biggest_pdf也是空，所以下面的同名txt也做了一次判空）
            if not os.path.exists(abs_pdf_1):
                biggest_pdf = a_pdf_name
                continue
            # 第一个pdf存在，第二个不存在时直接continue，进行下一次比较
            if not os.path.exists(abs_pdf_2):
                continue
            # 都存在时，才能做大小的比较
            if os.path.getsize(abs_pdf_2) > os.path.getsize(abs_pdf_1):
                biggest_pdf = a_pdf_name
        pdf_list.remove(biggest_pdf)
        drop_pdfs.extend(pdf_list)

    # 去掉带有这些行的pdf
    df = df[~df["pdf"].isin(drop_pdfs)]
    # 再把索引重新从小到大排序
    df.reset_index(drop=True, inplace=True)

    # 增加四列值（应该是可以不用增加这四行，下面df.loc[i, "汇率衍生工具"]这样赋值时，如果没有这列会自动增加）
    df["汇率衍生工具"] = ""
    df["汇率衍生工具_值"] = ""
    df["外币债务"] = ""
    df["外币债务_值"] = ""

    txt_folder_path = os.path.join(txt_path, info_excel_name.split(".")[0])
    for i, pdf_name in enumerate(df["pdf"].tolist()):
        abs_txt_path = os.path.join(txt_folder_path, pdf_name.replace(".pdf", ".txt"))
        if not os.path.exists(abs_txt_path):
            df.loc[i, "汇率衍生工具"] = "暂未找到对应pdf文件"
            df.loc[i, "外币债务"] = "暂未找到对应pdf文件"
            continue
        # -1：文章存在，但是没能转换；0代表没有这些关键字；1代表有这些关键字
        # 汇率衍生工具的关键词结果
        ex_rate_result = check(abs_txt_path, ex_rate_keywords)
        df.loc[i, "汇率衍生工具"] = list(ex_rate_result.keys())[0]
        ex_match_value = list(ex_rate_result.values())[0]
        if ex_match_value:
            df.loc[i, "汇率衍生工具_值"] = "_".join(ex_match_value)

        # 外币债务关键词结果
        # debt_result = check(abs_txt_path, debt_keywords, True)   # 这行是匹配`**债券`这种时的代码，应该用不到了，先放这里
        debt_result = check(abs_txt_path, debt_keywords)
        df.loc[i, "外币债务"] = list(debt_result.keys())[0]
        debt_match_value = list(debt_result.values())[0]
        if debt_match_value:
            df.loc[i, "外币债务_值"] = "_".join(debt_match_value)

    # 更改一下columns的顺序
    columns = ["code", "company", "type", "year", "date", "pdf", "汇率衍生工具", "汇率衍生工具_值",
               "外币债务", "外币债务_值"]
    df = df.reindex(columns=columns)

    abs_excel_path = os.path.join(save_path, info_excel_name)
    df.to_excel(abs_excel_path)


if __name__ == '__main__':
    """
        第四步：这是主要是读取前面 那个旧的py文件生成的excel文件信息，而不再是在线读取信息来处理
    """
    total_pdf_path = r"F:\for_re\sh\temp_data"
    info_excel_path = r"./download_urls"
    txt_path = r"F:\for_re\sh\temp_txt"
    save_path = r"F:\for_re\sh\temp_excel"
    os.makedirs(save_path, exist_ok=True)

    excel_names = os.listdir(info_excel_path)
    for excel_name in tqdm.tqdm(excel_names):
        abs_info_excel_path = os.path.join(info_excel_path, excel_name)
        a_company(abs_info_excel_path, txt_path, save_path)

    print("Done!")
