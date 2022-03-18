from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# from models import cbsd
# # from models.models import cbsd
from contextlib import contextmanager


# an Engine, which the Session will use for connection resources
# some_engine = create_engine("mysql+pymysql://root:N3wPr1vateNw@127.0.0.1:3306/domain_proxy?charset=utf8mb4")
class dbSession:
    def __init__(self):
        self.some_engine = create_engine("mysql+pymysql://root:N3wPr1vateNw@127.0.0.1:3306/domain_proxy?charset=utf8mb4")
        self.Session = sessionmaker(bind=self.some_engine)

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        session = self.Session()
        try:
            yield session
        except Exception as e:
            print(f"session Exception: {e}")
            session.rollback()
            raise
        finally:
            session.close()



# session = dbSession()

# with session.session_scope() as s:
#     a = s.query(cbsd).filter(cbsd.state_id == 3).all()

#     print(a)
# print(a[1].cbsd_id)