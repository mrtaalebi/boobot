from sqlalchemy import Column, Integer, String, create_engine 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()


class User(Base):
    
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

    
    def session(self):
        s = sessionmaker()
        s.configure(bind=self.engine)
        return s()

    
    def add(self, entry):
        s = self.session()
        s.add(entry)
        s.commit()

    
    def query(self, class_, filter_):
        s = self.session()
        q = s.query(class_)
        q = q.filter(filter_)
        return q

    
    def create_user(self, from_):
        user_id = from_['id']
        user = User(
                id=user_id,
                name=from_['first_name'],
                lang=from_['language_code'] or 'en',
                oc_username='',
                oc_password='',
            )
        self.add(user)
        return user


    def get_user(self, from_):
        user_id = from_['id']
        q = self.query(User, User.id == user_id)
        if q.count() == 0:
            return None
        elif q.count() == 1:
            return q.first()
