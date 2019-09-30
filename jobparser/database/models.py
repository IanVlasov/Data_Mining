from sqlalchemy import Table, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Vacancy(Base):
    __tablename__ = 'vacancy'
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    spider = Column(String, nullable=True)
    name = Column(String, nullable=True)
    url = Column(String, nullable=True)
    min_salary = Column(Integer, nullable=True)
    max_salary = Column(Integer, nullable=True)
    employer = Column(String, nullable=True)
    employer_url = Column(String, nullable=True)

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.url = kwargs.get('url')
        self.min_salary = kwargs.get('min_salary')
        self.max_salary = kwargs.get('max_salary')
        self.employer = kwargs.get('employer')
        self.employer_url = kwargs.get('employer_url')