#!venv/bin/python3
#https://docs.sqlalchemy.org/en/20/tutorial/engine.html

from venv import logger
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import Table, Column, Integer, String 
from sqlalchemy import select, insert, update

from sqlalchemy.orm import Session

import logging
logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.WARNING)

engine = create_engine(url='sqlite+pysqlite:///database.db', echo=True)

metadata_obj = MetaData()
user_table = Table(
    'users',
    metadata_obj,
    Column('id', Integer, primary_key=True),
    Column('user_id', String, unique=True),
    Column('name', String),
    Column('city', String)
    )

def _select(uid='test_id'):
    stmt = select(user_table).where(user_table.c.user_id == uid)
    logging.debug(stmt)
    name = None
    city = None
        
    with engine.connect() as conn:
        for row in conn.execute(stmt):
            logging.debug(len(row))
            name = row[2]
            city = row[3]
        conn.commit()
    return name, city


def _insert(user_id='test_id', name='test_name', city=None):
    stmt = insert(user_table).values(user_id=user_id, name=name, city=city)
    logging.debug(stmt)

    #insert into db
    with engine.connect() as conn:
        r = conn.execute(stmt)
        conn.commit()


def _update_city(city=None, uid=None):
    stmt = update(user_table).where(user_table.c.user_id == uid).values(city=city)
    logging.debug(stmt)
    with engine.connect() as conn:
        r = conn.execute(stmt)
        conn.commit()

#metadata_obj.drop_all(bind=engine)
#metadata_obj.create_all(bind=engine)
#update_city(city='new_city', uid='test_id')

