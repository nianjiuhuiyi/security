import os
import re
import pandas as pd

# 汇率衍生工具的关键词
# ex_rate_keywords = ["套期保值", "衍生品", "外汇衍生品", "期权", "外汇期货", "无本金交割远期外汇交易"]  # 第一次的
ex_rate_keywords = ["套期保值", "衍生品", "外汇衍生品", "期权", "外汇期货", "无本金交割远期外汇交易", "外汇套期", "期货",
                    "远期合约", "外汇远期", "外汇掉期", "货币互换", "货币掉期", "NDF", "外汇期权"]  # 第二次的
# 外币债务关键词
# debt_keywords = ["外币债务", "美元债务", "日元债务", "英镑债务", "欧元债务", "港元债务"]   # 第一次
debt_type = ["债务", "借款", "贷款"]  # 第二次(找打这符合的，以及其前面的两个字)
currency_name = ["外币", "澳元", "澳门元", "澳门币", "港币", "港元", "美元", "欧元", "日元", "英镑", "新加坡币", "新币", "马来西亚币",
                 "马来币", "马币", "令吉", "俄罗斯卢布", "卢布", "加拿大元", "加元", "印尼盾", "韩元", "新台币", "巴西雷亚尔",
                 "基纳", "基普", "老挝基普", "加纳赛地", "林吉特", "卢比", "印度卢比", "印尼卢比", "孟加拉塔卡", "缅甸元", "缅元",
                 "瑞士法郎", "苏姆", "台币", "泰国铢", "泰铢", "文币", "阿根廷比索", "澳币", "澳大利亚元", "澳洲元", "荷兰盾",
                 "瑞士法郎", "瑞郎"]
debt_keywords = [x + y for x in currency_name for y in debt_type]


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


if __name__ == '__main__':
    total_path = r"./txt_save"

    df = pd.DataFrame({}, columns=["code", "type", "year", "汇率衍生工具", "汇率衍生工具_值", "外币债务", "外币债务_值"])
    txt_names = os.listdir(total_path)

    no_txt_pdf_list = list()
    for i, txt_name in enumerate(txt_names):
        code, temp = txt_name.split("-")
        _type = temp[:4]
        year = temp.split(".")[0][4:]
        df.loc[i, ["code", "type", "year"]] = (code, _type, year)

        abs_txt_path = os.path.join(total_path, txt_name)
        if os.path.getsize(abs_txt_path) < 5 * 1024:
            df.loc[i, "汇率衍生工具"] = -1   # -1代表pdf没能转换成txt
            df.loc[i, "外币债务"] = -1
            df.loc[i, "汇率衍生工具_值"] = txt_name.replace(".txt", ".PDF")
            no_txt_pdf_list.append(txt_name.replace(".txt", ".PDF"))
            continue
        ex_rate_result = check(abs_txt_path, ex_rate_keywords)
        df.loc[i, "汇率衍生工具"] = list(ex_rate_result.keys())[0]
        ex_match_value = list(ex_rate_result.values())[0]
        if ex_match_value:
            df.loc[i, "汇率衍生工具_值"] = "_".join(ex_match_value)

        debt_result = check(abs_txt_path, debt_keywords)
        df.loc[i, "外币债务"] = list(debt_result.keys())[0]
        debt_match_value = list(debt_result.values())[0]
        if debt_match_value:
            df.loc[i, "外币债务_值"] = "_".join(debt_match_value)

    df.to_excel("./supple_results.xlsx")
    print("Done!")
