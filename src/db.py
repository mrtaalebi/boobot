import logging

from sqlalchemy import Column, Integer, String, create_engine 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()


class BooUser(Base):
    
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    lang = Column(String(5))
    oc_username = Column(String(20))
    oc_password = Column(String(64))


    def __init__(self, id, name, lang, oc_username=None, oc_password=None):
        self.id = id
        self.name = name
        self.lang = lang
        self.oc_username = oc_username
        self.oc_password = oc_password


class DB:

    def __init__(self, uri):
        self.engine = create_engine(uri)
        Base.metadata.create_all(self.engine)


    def db_transact(func):
        def wrapper(*args, **kwargs):
            try:
                x = func(*args, **kwargs)
                return x
            except Exception as e:
                logging.debug(e)
                logging.info('DB TRANSACTION ERROR')
        return wrapper

    
    @db_transact
    def session(self):
        s = sessionmaker()
        s.configure(bind=self.engine)
        return s()

    
    @db_transact
    def add(self, entry):
        s = self.session()
        s.add(entry)
        s.commit()
        s.close()
    
    
    @db_transact
    def delete(self, user_id):
        s = self.session()
        user = s.query(BooUser).filter(BooUser.id == user_id).first()
        oc_username = user.oc_username
        s.delete(user)
        s.commit()
        s.close()
        return oc_username
    
    
    @db_transact
    def query(self, class_, filter_):
        s = self.session()
        q = s.query(class_)
        q = q.filter(filter_)
        return q

    
    @db_transact
    def create_user(self, from_):
        user_id = from_['id']
        lang = 'en'
        name = from_['first_name']
        if 'last_name' in from_:
            name = name + ' ' + from_['last_name']
        user = BooUser(
                id=user_id,
                name=name,
                lang=lang,
                oc_username='',
                oc_password='',
            )
        self.add(user)
        return user

    
    @db_transact
    def get_user(self, from_):
        user_id = from_['id']
        q = self.query(BooUser, BooUser.id == user_id)
        if q.count() == 0:
            return None
        elif q.count() == 1:
            return q.first()


    @db_transact
    def all_users(self):
        return self.query(BooUser, BooUser.id > 0).all()
