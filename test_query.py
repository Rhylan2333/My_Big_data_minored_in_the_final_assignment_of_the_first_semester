from app import Admin_info, Area_info ,User_info, Ha_info, db  # 导入模型类、db变量

id_user=User_info.query.filter_by(username='caicai').first().id_user  # 就在这外键连接，用 filter_by()
print("id_user 是 "+str(id_user))

id_area=Area_info.query.filter_by(name_area='伊犁').first().id_area  # 就在这外键连接，用 filter_by()
print("id_area 是 "+str(id_area))