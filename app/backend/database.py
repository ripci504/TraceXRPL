from app import db

class Base(db.Model):
    __abstract__  = True
    id            = db.Column(db.Integer, primary_key=True)
    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(),
                                           onupdate=db.func.current_timestamp())
    
class Wallet(Base):
    __tablename__ = 'wallet'

    seed = db.Column(db.Text)
    address = db.Column(db.Text)
    net = db.Column(db.Text)

    def __init__(self, seed, address, net):
        self.seed = seed
        self.address = address
        self.net = net

    def create_wallet():
        pass


class Product(Base):
    __tablename__ = 'product'

    product_uuid = db.Column(db.Text)
    product_name = db.Column(db.Text)
    nftokenid = db.Column(db.Text)
    transhash = db.Column(db.Text)
    product_state = db.Column(db.Integer)

    
    def __init__(self, product_uuid, product_name, nftokenid, transhash, product_state):
        self.product_uuid = product_uuid
        self.product_name = product_name
        self.nftokenid = nftokenid
        self.transhash = transhash
        self.product_state = product_state

class ProductModel(Base):
    __tablename__ = 'product_model'

    uuid = db.Column(db.Text)
    name = db.Column(db.Text)
    org = db.Column(db.Text)
    
    def __init__(self, uuid, name, org):
        self.uuid = uuid
        self.name = name
        self.org = org
    

class ProductStates(Base):
    __tablename__ = 'product_states'

    product_id = db.Column(db.Integer)
    state_name = db.Column(db.Text)
    state_number = db.Column(db.Integer)

    
    def __init__(self, product_id, state_name, state_number):
        self.product_id = product_id
        self.state_name = state_name
        self.state_number = state_number
    