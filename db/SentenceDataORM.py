# -*- coding: utf-8 -*-
import json

from sqlalchemy import Column, Integer, String, Boolean, create_engine
from sqlalchemy.orm import declarative_base
Base = declarative_base()


class SentencesDataORM(Base):
    __tablename__ = 'SENTENCES_DATA'

    ID = Column(Integer, primary_key=True, autoincrement=True)
    SENTENCE = Column(String(255))
    SAME_QS_WORD = Column(Boolean)
    SAME_DEPENDENCY = Column(Boolean)
    DEPENDENCY_PATH = Column(String(255))
    SENTENCE_PATTERN = Column(String(255))
    SENTENCE_STRUCTURE_WORD = Column(String(255))
    SENTENCE_STRUCTURE_WORD_POS = Column(String(255))
    QUESTION_WORD = Column(String(255))
    QUESTION_WORD_POS = Column(String(255))

    SENTENCE_NUMMOD = Column(Integer)
    SENTENCE_OBL_TMOD = Column(Integer)
    SENTENCE_ADVCL = Column(Integer)
    SENTENCE_OBL_AGENT = Column(Integer)
    SENTENCE_CONJ = Column(Integer)
    SENTENCE_OBL = Column(Integer)
    SENTENCE_CC = Column(Integer)
    SENTENCE_OBL_NPMOD = Column(Integer)
    SENTENCE_CC_PRECONJ = Column(Integer)
    SENTENCE_COP = Column(Integer)
    SENTENCE_NMOD_POSSESS = Column(Integer)
    SENTENCE_PUNCT = Column(Integer)
    SENTENCE_XCOMP = Column(Integer)
    SENTENCE_EXPL = Column(Integer)
    SENTENCE_AUX = Column(Integer)
    SENTENCE_OBJ = Column(Integer)
    SENTENCE_ACL = Column(Integer)
    SENTENCE_CCOMP = Column(Integer)
    SENTENCE_ACL_RELCL = Column(Integer)
    SENTENCE_DEP = Column(Integer)
    SENTENCE_APPOS = Column(Integer)
    SENTENCE_NSUBJ_PASS = Column(Integer)
    SENTENCE_FLAT = Column(Integer)
    SENTENCE_CASE = Column(Integer)
    SENTENCE_AMOD = Column(Integer)
    SENTENCE_ROOT = Column(Integer)
    SENTENCE_NMOD_NPMOD = Column(Integer)
    SENTENCE_AUX_PASS = Column(Integer)
    SENTENCE_MARK = Column(Integer)
    SENTENCE_ADVCL_RELCL = Column(Integer)
    SENTENCE_ADVMOD = Column(Integer)
    SENTENCE_NMOD = Column(Integer)
    SENTENCE_IOBJ = Column(Integer)
    SENTENCE_DET_PREDET = Column(Integer)
    SENTENCE_FIXED = Column(Integer)
    SENTENCE_DET = Column(Integer)
    SENTENCE_COMPOUND = Column(Integer)
    SENTENCE_NSUBJ = Column(Integer)

    # 以下是问题相关的列，类型与上述句子部分的列相同
    QUESTION_NUMMOD = Column(Integer)
    QUESTION_OBL_TMOD = Column(Integer)
    QUESTION_ADVCL = Column(Integer)
    QUESTION_OBL_AGENT = Column(Integer)
    QUESTION_CONJ = Column(Integer)
    QUESTION_OBL = Column(Integer)
    QUESTION_CC = Column(Integer)
    QUESTION_OBL_NPMOD = Column(Integer)
    QUESTION_CC_PRECONJ = Column(Integer)
    QUESTION_COP = Column(Integer)
    QUESTION_NMOD_POSSESS = Column(Integer)
    QUESTION_PUNCT = Column(Integer)
    QUESTION_XCOMP = Column(Integer)
    QUESTION_EXPL = Column(Integer)
    QUESTION_AUX = Column(Integer)
    QUESTION_OBJ = Column(Integer)
    QUESTION_ACL = Column(Integer)
    QUESTION_CCOMP = Column(Integer)
    QUESTION_ACL_RELCL = Column(Integer)
    QUESTION_DEP = Column(Integer)
    QUESTION_APPOS = Column(Integer)
    QUESTION_NSUBJ_PASS = Column(Integer)
    QUESTION_FLAT = Column(Integer)
    QUESTION_CASE = Column(Integer)
    QUESTION_AMOD = Column(Integer)
    QUESTION_ROOT = Column(Integer)
    QUESTION_NMOD_NPMOD = Column(Integer)
    QUESTION_AUX_PASS = Column(Integer)
    QUESTION_MARK = Column(Integer)
    QUESTION_ADVCL_RELCL = Column(Integer)
    QUESTION_ADVMOD = Column(Integer)
    QUESTION_NMOD = Column(Integer)
    QUESTION_IOBJ = Column(Integer)
    QUESTION_DET_PREDET = Column(Integer)
    QUESTION_FIXED = Column(Integer)
    QUESTION_DET = Column(Integer)
    QUESTION_COMPOUND = Column(Integer)
    QUESTION_NSUBJ = Column(Integer)

    @classmethod
    def create_sentence_data_from_list(cls, temp_list):
        """
        根据temp_list中的数据创建SentenceDataORM实例。
        假设temp_list的元素顺序与SentenceDataORM的字段顺序一致。
        """
        # 移除ID字段，确保temp_list中不包含ID且长度匹配
        field_names = [c_attr.key for c_attr in cls.__table__.columns if c_attr.key != 'ID']
        assert len(temp_list) == len(field_names), "temp_list的长度与字段数量不匹配"

        # 使用类方法处理特殊字段
        processed_temp_list = cls.process_special_fields(temp_list, field_names)

        # 使用zip函数将字段名与值配对，然后转换为字典
        data_dict = dict(zip(field_names, processed_temp_list))

        # 使用字典解包创建SentenceDataORM实例
        return cls(**data_dict)

    @staticmethod
    def process_special_fields(temp_list, field_names):
        """
        处理temp_list中需要特殊处理的字段，目前仅处理将列表转换为JSON字符串的情况。
        """
        # 直接定位到需要特殊处理的字段索引，这里假设是"DEPENDENCY_PATH"
        dependency_path_index = field_names.index('DEPENDENCY_PATH')
        if isinstance(temp_list[dependency_path_index], list):
            temp_list[dependency_path_index] = json.dumps(temp_list[dependency_path_index], ensure_ascii=False)

        return temp_list
    def to_string(self):
        """
        Returns a formatted string with all fields of the SentenceDataORM instance.
        This is useful for logging or displaying all details of a sentence's data.
        """
        field_values = [
            (field.name, getattr(self, field.name))
            for field in self.__table__.columns
            if field.name != 'ID'  # Excluding the ID for readability
        ]
        return "\n".join([f"{name}: {value}" for name, value in field_values])

