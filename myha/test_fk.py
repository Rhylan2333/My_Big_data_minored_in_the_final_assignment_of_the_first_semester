from app import Admin_info, Area_info, User_info, Ha_info
from formula import cal_the_complex_of_1_and_2_generation_of_Ha_0
from werkzeug.security import generate_password_hash
from datetime import date

# test1：测试 Area_info 的外键匹配上 Admin_info 没
"""Admin_info 的实例未被创建"""
admin_instance = Admin_info(
    id_admin=0,
    name_admin='管理员0',
    adminname='guanliyua',
    password_hash=generate_password_hash('123456'))  # 创建实例
print(admin_instance.list_area_info
      )  # 测试 admin_instance 实例中的 relationship 生成的list

area_instance = Area_info(
    id_area=0,
    name_area="伊犁",
    id_admin=0  # 这是外键
)  # 创建实例

admin_instance.list_area_info.append(
    area_instance
)  # 向 admin_instance 实例中的 relation 生成的 list_area_info 传入 area_instance 实例
print(admin_instance.list_area_info)  # 再次测试实例中的 relation 生成的 list
print(admin_instance.list_area_info[-1].name_area
      )  # 获取 InstrumentedList 的倒数第一个元素
print("“Area_info 的外键匹配上 Admin_info 没”？测试结果如上。\n")

# test2：测试 User_info 的外键匹配上 Area_info 没
"""Area_info 的实例已在 test1 中创建，故现在只需要创建 User_info 的实例"""
print(admin_instance.list_area_info
      )  # 测试 admin_instance 实例中的 relationship 生成的 list

user_instance = User_info(
    id_user=0,
    name_user='农户0',
    username='nonghu',
    password_hash=generate_password_hash('123'),
    id_area=0  # 这是外键
)  # 创建实例

area_instance.list_user_info.append(user_instance)
print(area_instance.list_user_info)  # 再次测试实例中的 relation 生成的 list
print(
    area_instance.list_user_info[-1].name_user)  # 获取 InstrumentedList 的倒数第一个元素
print("“User_info 的外键匹配上 Area_info 没”？测试结果如上。\n")

# test3：测试 Ha_info 的外键匹配上 User_info、Area_info 没"""
"""Area_info、User_info的实例已在 test1、test2 中创建，故现在只需要创建 Ha_info 的实例"""
print(
    area_instance.list_ha_info)  # 测试 area_instance 实例中的 relationship 生成的 list
print(
    user_instance.list_ha_info)  # 测试 area_instance 实例中的 relationship 生成的 list

ha_instance = Ha_info(
    id_ha=0,
    x1=0,
    x2=0,
    y=cal_the_complex_of_1_and_2_generation_of_Ha_0(0, 0),
    date=date.today(),
    id_user=0,  # 这是外键
    id_area=0  # 这是外键
)  # 创建实例

area_instance.list_ha_info.append(
    ha_instance
)  # 向 area_instance 实例中的 relation 生成的 list_ha_info 传入 ha_instance 实例。源自 print(area_instance.list_ha_info)

user_instance.list_ha_info.append(
    ha_instance
)  # 向 area_instance 实例中的 relation 生成的 list_ha_info 传入 ha_instance 实例。源自 print(user_instance.list_ha_info)

print(area_instance.list_ha_info)  # 再次测试实例中的 relation 生成的 list
print(
    area_instance.list_ha_info[-1].id_user)  # 获取 InstrumentedList 的倒数第一个元素
print("“Ha_info 的外键匹配上 User_info没”？测试结果如上。")
print(user_instance.list_ha_info)  # 再次测试实例中的 relation 生成的 list
print(
    user_instance.list_ha_info[-1].id_area)  # 获取 InstrumentedList 的倒数第一个元素
print("“Ha_info 的外键匹配上 Area_info 没”？测试结果如上。")
print("“Ha_info 的外键匹配上 User_info、Area_info 没”？测试结果如上。\n")

def test0():
    """测试“传入 id_area ”输出“name_area”；“传入 id_user ”输出“ name_user”。"""
    print("传入的 id_area 是 " + str(area_instance.id_area) + "；”输出“的 name_area 是 " + str(Area_info.query.filter_by(id_area=area_instance.id_area).first().name_area) + "。")
    """在 index.html 中应为“Area_info.query.filter_by(id_area=row_area.id_area).first().name_area”。"""
    user_instance.id_user
    print("传入的 id_user 是 " + str(user_instance.id_user) + "；”输出“的 name_area 是 " + str(User_info.query.filter_by(id_user=user_instance.id_user).first().name_user) + "。")
    """在 index.html 中应为“User_info.query.filter_by(id_user=row_user.id_user).first().name_user”。"""
    return None

test0()