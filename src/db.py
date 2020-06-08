from sqlalchemy import Column, Integer, String, create_engine 
from sqlalchemy.ext.declarative import declrative_base
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
        q = q.filter(f)
        return q

    
    def get_or_create_user(self, from_):
        user_id = from_['id']
        q = self.query(User, User.id == user_id)
        if len(q) == 0:
            user = User(
                    id=user_id,
                    name=from_['first_name'],
                    lang=from_['language-code'],
                    oc_username='',
                    oc_password='',
                )
            self.add(user)
            options = [

            ]
            return user
        else:
            return q.first()


    def get_oc_config(self, user_id):
        q = self.query(OC_Config, OC_Config.user_id == user_id)
        if len(q) == 0:
            return None
        elif len(q) == 1:
            return q.first()
