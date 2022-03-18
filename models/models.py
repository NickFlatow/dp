from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, String, CHAR
from sqlalchemy.sql.functions import now

Base = declarative_base()


class CBSD(Base):
    __tablename__ = 'cbsd'

    id = Column(Integer,primary_key=True)
    state_id = Column(Integer)
    cbsd_id = Column(String)
    cbsd_category = Column(CHAR)
    user_id = Column(String)
    fcc_id = Column(String)
    cbsd_serial_number = Column(String)
    cbsd_action = Column(String)
    time_updated = Column(DateTime(timezone=True), server_default=now(), onupdate=now())


    def __repr__(self):
        return f"cbsd_id: {self.cbsd_id} user_id: {self.user_id} fcc_id: {self.fcc_id} cbsd_serial_number: {self.cbsd_serial_number} last updated: {self.time_updated}"
