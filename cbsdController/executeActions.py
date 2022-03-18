from models.models import CBSD

def executeAction(session):
    cbsds = session.query(CBSD).filter(CBSD.cbsd_action != None).all()


    for cbsd in cbsds:
        print(cbsd)