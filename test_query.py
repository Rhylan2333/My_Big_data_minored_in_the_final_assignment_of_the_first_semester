from app import Admin_info, Area_info ,User_info, Ha_info, db  # 导入模型类、db变量

id_user=User_info.query.filter_by(username='caicai').first().id_user  # 就在这外键连接，用 filter_by()
print("id_user 是 "+str(id_user))

id_area=Area_info.query.filter_by(name_area='伊犁').first().id_area  # 就在这外键连接，用 filter_by()
print("id_area 是 "+str(id_area))

list_area_name_area = []
list_area=Area_info.query.order_by(db.desc(Area_info.id_area)).filter(Area_info.name_area.like("%{}%".format('伊'))).all()  # 返回一个 包含“满足检索要求”的所有记录的 list
for row_area in list_area:
    list_area_name_area.append(row_area.name_area)
print("\n模糊查询结果： ")
for row_area in list_area:
    print(row_area)
    print("\t" + str(row_area.name_area))

print('伊犁' in list_area_name_area)