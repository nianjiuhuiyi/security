import os
import pandas as pd

# 显示所有列
pd.set_option('display.max_columns', None)
# 显示所有行
pd.set_option('display.max_rows', None)
# 设置value的显示长度为200，默认为50
pd.set_option('max_colwidth', 200)


"""
    这个暂时放这里吧，这个是，下载的2021年的年报，它的日子上全是表的2022的，就手动改过来了
    前面就都执行好了，这个除非更新 ./download_urls/ 文件夹，不要再去执行
"""


counts = 0
info_path = r"./download_urls"
info_names = os.listdir(info_path)
for info_name in info_names:
    abs_path = os.path.join(info_path, info_name)
    df = pd.read_excel(abs_path, converters={"code": str})

    "这下面这几行代码就是把这个时间改了，然后重新保存覆盖的excel"
    # # 现在标准的22的年报，其实是21年的，需要不把这个year的值从2022改成2021
    # type_year = df[["type", "year"]].values.tolist()
    # if ['年报', 2022] in type_year:
    #     index = type_year.index(['年报', 2022])
    #     df.loc[index, "year"] = 2021
    #     df.to_excel(abs_path)   # 然后重新保存覆盖
    #     counts += 1

    "这几行是看看，还有没有每改到的，改完后，理论上，下面的counts就是0了"
    type_year = df[["type", "year"]].values.tolist()
    if ['年报', 2022] in type_year:
        print(abs_path)
        counts += 1

print(counts)
