import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["SimHei"] #显示中文（让中文汉字不乱码）
plt.rcParams["axes.unicode_minus"] = False #显示负号（让负号 `-`不乱码）

# ================= 1.读取SQL导出的4份结果文件 =================
df_pv_uv = pd.read_csv("pv_uv.csv")       # 总PV UV
df_dau = pd.read_csv("dau.csv")          # 每日DAU
df_funnel = pd.read_csv("funnel.csv")    # 漏斗数据
user_active = pd.read_csv("user_active.csv") # 用户活跃日期（留存计算）
df_hour = pd.read_csv('hour_dist.csv') # 用户行为24小时时段分布

# 打印整体PV、UV结果
print("=====整体指标=====")
print(f"总PV（全部行为次数）：{df_pv_uv['pv_total'][0]}")
print(f"总UV（独立用户数）：{df_pv_uv['uv_total'][0]}")


# ================= 2.DAU趋势图 =================
df_dau["dt_date"] = pd.to_datetime(df_dau["dt_date"])
plt.figure(figsize=(10,4))
plt.plot(df_dau["dt_date"], df_dau["dau"], marker="o", color="#2E86AB")
plt.title("每日活跃用户DAU趋势")
plt.xlabel("日期")
plt.ylabel("DAU(日活跃用户)")
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig("images/dau_trend.png") # 保存到images文件夹
plt.show()


# =================3. 用户行为转化漏斗 =================
# 行为名称映射，按漏斗顺序：浏览→收藏→加购→购买
map_dict = {"pv":"浏览","fav":"收藏","cart":"加购","buy":"购买"}
df_funnel["behavior_name"] = df_funnel["behavior_type"].map(map_dict)
order = ["浏览","收藏","加购","购买"]
df_funnel["behavior_name"] = pd.Categorical(df_funnel["behavior_name"],categories=order,ordered=True)
df_funnel = df_funnel.sort_values("behavior_name")

# 计算转化率
pv_total = df_funnel[df_funnel["behavior_name"]=="浏览"]["user_cnt"].values[0]
df_funnel["转化率"] = df_funnel["user_cnt"] / pv_total
print("\n=====转化漏斗指标=====")
print(df_funnel)
#绘制行为转化漏斗图
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False
plt.figure(figsize=(9,5))
plt.bar(df_funnel["behavior_name"], df_funnel["user_cnt"], color=["#2E86AB","#A23B72","#F18F01","#C73E1D"])
plt.title("用户行为转化漏斗")
plt.xlabel("用户行为")
plt.ylabel("独立用户数量")

# 在柱子上标注人数+转化率
for i,row in df_funnel.iterrows():
    plt.text(i, row["user_cnt"]+8000, f'{row["user_cnt"]}\n转化率：{row["转化率"]:.2%}',ha="center")

plt.tight_layout()
plt.savefig("images/funnel_chart.png") # 保存到images文件夹
plt.show()

# =================4. 用户24小时行为时段分布==================
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False
plt.figure(figsize=(12,4))
plt.bar(df_hour["hour"], df_hour["behavior_cnt"], color="#6A994E")
plt.title("用户24小时行为时段分布")
plt.xlabel("小时（0~23点）")
plt.ylabel("行为次数")
plt.xticks(range(0,24))
plt.tight_layout()
plt.savefig("images/hour_dist.png") # 保存到images文件夹
plt.show()

# ==================5.次日留存计算=================
user_active["dt_date"] = pd.to_datetime(user_active["dt_date"])
# 按用户分组，获取下一次活跃日期
user_active = user_active.sort_values(by=["user_id","dt_date"])
user_active["next_date"] = user_active.groupby("user_id")["dt_date"].shift(-1)

# 判断是否为次日回来
user_active["is_next_day"] = (user_active["next_date"] - user_active["dt_date"]).dt.days ==1

# 分组统计当日活跃人数、次日回流人数、留存率
retention_df = user_active.groupby("dt_date").agg(
    dau = ("user_id","nunique"),
    return_user = ("is_next_day","sum")
).reset_index()
retention_df["retention_rate"] = retention_df["return_user"] / retention_df["dau"]
print("\n=====次日留存结果=====")
print(retention_df)

# 留存率可视化
plt.figure(figsize=(10,4))
plt.plot(retention_df["dt_date"], retention_df["retention_rate"],marker="o",color="#A23B72")
plt.title("用户次日留存率趋势")
plt.xlabel("日期")
plt.ylabel("次日留存率")
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig("images/retention.png") # 保存到images文件夹
plt.show()
