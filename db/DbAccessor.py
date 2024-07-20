# 设置编码，支持中文
# -*- coding: utf-8 -*-


# 导入必要的库
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text, select, delete
import csv
from pathlib import Path
from db.SentenceDataORM import SentencesDataORM
from sqlalchemy import func

# 配置SQL Server连接信息
database = 'Data'  # 数据库名称
server = 'localhost,1433'  # 服务器地址和端口
username = 'sa'  # 用户名
password = '123456'  # 密码
driver = 'ODBC+Driver+17+for+SQL+Server'  # SQL Server驱动

# 创建数据库引擎并建立Session
engine = create_engine(f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver}')
session = Session(engine)


# 插入数据到数据库
def insert_data(data_list):
    for temp_list in data_list:
        # 处理temp_list并准备数据
        sentence_data = SentencesDataORM.create_sentence_data_from_list(temp_list)
        session.add(sentence_data)  # 添加数据到Session

    try:
        session.commit()  # 提交事务
    except Exception as e:
        session.rollback()  # 发生错误时回滚
        print(f"处理数据时出错: {temp_list}, 错误信息: {e}")
    finally:
        session.close()  # 关闭Session


# 清空SentenceDataORM对应的数据表
def clear_table():
    try:
        with session.begin():
            session.execute(delete(SentencesDataORM))  # 执行删除
            session.execute(text("DBCC CHECKIDENT ('SENTENCES_DATA', RESEED, 0);"))  # 重置标识列
            session.commit()
            print("数据表已成功清空并重置标识列。")
    except Exception as e:
        session.rollback()
        print(f"清空表数据时出错: {e}")
    finally:
        session.close()


# 查询表中所有数据并保存到CSV
def query_and_save_all_to_csv(model, filepath):
    try:
        query = select(model.__table__)  # 构造查询
        result = session.execute(query)
        headers = result.keys()  # 获取列名

        # 确保目录存在
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        # 写入CSV
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)  # 写入标题行
            writer.writerows(result.fetchall())  # 写入数据行

        print(f"数据已成功保存到 {filepath}")
    except Exception as e:
        print(f"保存到CSV时出错: {e}")
    finally:
        session.close()


def query_and_save_to_list(model):
    try:
        query = select(model.__table__)  # 构造查询
        result = session.execute(query)
        headers = result.keys()  # 获取列名

        # 将查询结果转换为列表字典形式
        data_list = [dict(zip(headers, row)) for row in result.fetchall()]

        print("数据已成功保存到内存中的列表")
        return data_list

    except Exception as e:
        print(f"查询或处理数据时出错: {e}")
        return None
    finally:
        session.close()


def count_rows_by_conditions(conditions_str):
    # 使用SQLAlchemy构造查询，直接计算行数
    query = select(func.count()).select_from(SentencesDataORM).where(
        text(conditions_str))
    # 执行查询并获取行数
    with session as sess:  # 确保session可以当作上下文管理器使用，如使用scoped_session
        row_count = sess.execute(query).scalar()

    return row_count
