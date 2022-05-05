import pandas as pd
import tqdm
import os
import re

# 显示所有列
pd.set_option('display.max_columns', None)
# 显示所有行
pd.set_option('display.max_rows', None)
# 设置value的显示长度为300(当一些链接数据比较长时，可给大一些)，默认为50
pd.set_option('max_colwidth', 300)

"""
第一次使用时：
先  win+r, 左下角会弹出一个运行，然后输入  cmd
接着在弹出的窗口里输入(直接复制这里)：
pip install pandas tqdm  openpyxl -i https://mirrors.aliyun.com/pypi/simple
"""


def transform_V1(origina_xlsx_path, lens=6, save_path="./"):
    """
        这是最开始版本的代码，放这里吧，整一个新的
    origina_xlsx_path：需要转换的表的绝对路径
    lens：证券代码的长度，默认为6位
    save_path：结果的保存地址,不给这个参数就是保存到当前目录下
    """

    id_vars = "证券代码"  # 这个是保持不变的那个
    var_name = "临时名称"  # 这个名字是我乱取的，自己改
    value_name = "临时值"  # 这也是乱取的，自己改了就行

    xlsx_name = os.path.basename(origina_xlsx_path)
    # 默认的表名称就是"Sheet1"，如果excel中表名变了，这里改
    dataframe = pd.read_excel(origina_xlsx_path)
    # dataframe = pd.read_excel(origina_xlsx_path, sheet_name="Sheet1")

    stock_codes = dataframe[id_vars].values
    new_dataframe = dataframe.melt(
        id_vars=[id_vars],
        var_name=var_name,
        value_name=value_name
    )
    temp_values = []
    for stock_code in tqdm.tqdm(stock_codes, desc="转换进度"):
        index = (new_dataframe[id_vars] == stock_code)
        temp_value = new_dataframe[index].values.tolist()

        stock_code = str(stock_code)
        if len(stock_code) < lens:
            for temp in temp_value:
                temp[0] = "0" * (lens - len(stock_code)) + stock_code

        temp_values.extend(temp_value)

    results = pd.DataFrame(data=temp_values, columns=[id_vars, var_name, value_name])

    name, suffix = os.path.splitext(xlsx_name)
    save_name = name + "_trans" + suffix  #
    print("数据较多时，保存还需要一点点时间！")
    results.to_excel(os.path.join(save_path, save_name), index=False)
    print("完成！结果的绝对地址：{}".format(os.path.join(save_path, save_name)))


def transform_V2(trans_excel_path):
    xlsx_name = os.path.basename(trans_excel_path)
    dataframe = pd.read_excel(trans_excel_path)
    # 添加一列证券名称
    com_name_li = list()
    com_name = ""
    for i in range(dataframe.shape[0]):
        if dataframe.loc[i, "临时名称"] == "证券简称":
            com_name = dataframe.loc[i, "临时值"]
        com_name_li.append(com_name)
    # 把所有值存起来一起赋值，比循环中dataframe.loc[i, "证券简称"] = com_name 一个个赋值快得多
    dataframe["证券简称"] = com_name_li

    # 删除掉“临时名称”为“证券简称”的所有行
    dataframe = dataframe[~dataframe["临时名称"].isin(["证券简称"])]
    dataframe.reset_index(drop=True, inplace=True)

    # 将证券代码 000002.SZ 改成 000002
    dataframe["证券代码"] = dataframe["证券代码"].apply(lambda x: x.split(".")[0])

    # 将临时值中的value简化一下
    def my_replace(str_data):
        ret = re.match("[\w\\n[\]]+ (\w*)\\n[\[\]\w]*", str_data)  # match一定要从头开始匹配
        # ret = re.search("\d+\w+", data)     # 这俩效果是一样的，刚好\n做了分割
        return ret.group(1)

    dataframe["临时名称"] = dataframe["临时名称"].apply(my_replace)

    # 修改columns的顺序
    new_columns = ["证券代码", "证券简称", "临时名称", "临时值"]
    dataframe = dataframe.reindex(columns=new_columns)

    name, suffix = os.path.splitext(xlsx_name)
    save_name = name + "_V2" + suffix
    dataframe.to_excel(save_name, index=False)


if __name__ == '__main__':
    """
    这是最开始把两个阶段分开的代码，
    """

    # 把这个path改成自己文件的路径
    path = r"./经营活动现金流量净额（季报）.xlsx"

    # 第一步：把给的数据做个初步转换
    transform_V1(r"./经营活动现金流量净额（季报）.xlsx")

    # 第二步：第一步转换的数据结果再处理一下，到这里成为最终结果(所以带v2的就是)
    transform_V2(r"./经营活动现金流量净额（季报）_trans.xlsx")  # 这就是保存在当前目录,证券代码长度6位
    print("Done!")
