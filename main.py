import pandas as pd
import matplotlib.pyplot as plt
import pymysql
from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_PORT, MYSQL_DB

conn = pymysql.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    port=MYSQL_PORT,
    database=MYSQL_DB
)


plt.rcParams["font.sans-serif"] = ["SimHei"] #显示中文（让中文汉字不乱码）
plt.rcParams["axes.unicode_minus"] = False #显示负号（让负号 `-`不乱码）

RAW_DATA_PATH = "./data/UserBehavior.csv"
CLEAN_SAVE_PATH = "./clean_taobao.csv"
IMAGE_SAVE_DIR = "./images/"

# ----------------------1、读取csv数据----------------------
# 从数据集中抽样10万行，不做复杂映射，只用loc赋值
df = pd.read_csv(RAW_DATA_PATH,
                 names=["user_id", "item_id", "category_id", "behavior_type", "timestamp"],
                 nrows=100000)

print("原始数据前5行")
print(df.head())

# behavior_type：1浏览pv，2收藏fav，3加购cart，4购买buy
# loc方法选择行进行赋值
df.loc[df["behavior_type"] == 1, "behavior_type"] = "pv"
df.loc[df["behavior_type"] == 2, "behavior_type"] = "fav"
df.loc[df["behavior_type"] == 3, "behavior_type"] = "cart"
df.loc[df["behavior_type"] == 4, "behavior_type"] = "buy"

# 时间处理：把时间戳转为datetime，dt提取小时
df["datetime"] = pd.to_datetime(df["timestamp"], unit="s")
df["hour"] = df["datetime"].dt.hour

# drop_duplicates方法去除重复值
df = df.drop_duplicates(subset=["user_id", "item_id", "behavior_type", "timestamp"])
print("清洗之后数据总行数：", len(df))

# 如果数据为空直接结束，防止报错
if len(df) <= 0:
    print("警告，数据集为空，请检查文件路径！")
    exit()

# ----------------------2、基础指标统计：PV、UV（布尔索引筛选）----------------------
# PV：浏览行为总次数
pv_data = df[df["behavior_type"] == "pv"]
pv_count = len(pv_data)

# UV：去重用户总人数 nunique()
uv_count = df["user_id"].nunique()

# 收藏、加购、购买
fav_count = len(df[df["behavior_type"] == "fav"])
cart_count = len(df[df["behavior_type"] == "cart"])
buy_count = len(df[df["behavior_type"] == "buy"])

print("="*40)
print(f"浏览PV次数：{pv_count}")
print(f"独立用户UV数量：{uv_count}")
print(f"收藏次数：{fav_count}")
print(f"加购次数：{cart_count}")
print(f"购买次数：{buy_count}")
print("="*40)

# ----------------------3、绘制转化漏斗柱状图（matplotlib基础绘图）----------------------
x_data = ["浏览", "收藏", "加购", "购买"]
y_data = [pv_count, fav_count, cart_count, buy_count]

plt.figure(figsize=(8, 5))
plt.bar(x=x_data, height=y_data, color=["#3498db", "#2ecc71", "#f39c12", "#e74c3c"])
plt.title("电商用户行为转化漏斗图（抽样数据集）")
plt.xlabel("用户行为环节")
plt.ylabel("行为发生次数")
plt.savefig(f"{IMAGE_SAVE_DIR}bar.png", dpi=300, bbox_inches="tight") # 保存图片
plt.show()

# ----------------------4、24小时用户行为分布图 groupby----------------------
hour_result = df.groupby("hour").size()
print("\n按小时统计行为数量")
print(hour_result)

plt.figure(figsize=(10,4))
plt.plot(hour_result.index, hour_result.values, marker="o")
plt.title("全天24小时用户行为分布")
plt.xlabel("小时")
plt.ylabel("行为总次数")
plt.xticks(range(0,24))
plt.grid(alpha=0.3)
plt.savefig(f"{IMAGE_SAVE_DIR}funnel.png", dpi=300, bbox_inches="tight")  # 保存图片
plt.show()

# ----------------------5、统计类目访问TOP15  groupby + sort_values----------------------
# 按类目、行为分组统计数量
cat_group = df.groupby(["category_id", "behavior_type"]).size()
# unstack可以做行转列
cat_table = cat_group.unstack(fill_value=0)

print("\n各个类目行为统计表")
print(cat_table.head())

# 判断是否存在pv列，防止抽样没有浏览数据报错
if "pv" in cat_table.columns:
    # sort_values排序
    top15_cat = cat_table.sort_values(by="pv", ascending=False).head(15)
    print("\n浏览量TOP15类目")
    print(top15_cat)
    # 保存结果到csv文件
    top15_cat.to_csv("top15_category.csv", encoding="utf-8")
    print("\n✅已经保存 top15_category.csv 到项目文件夹")
else:
    print("抽样数据集无浏览pv数据，跳过类目排序")

print("\n========项目全部执行结束========")
