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
    # Transaction hash can be used to create sell offer for physical product owner
    transhash = db.Column(db.Text)
    product_stage = db.Column(db.Integer)

    
    def __init__(self, product_uuid, product_name, nftokenid, transhash, product_stage):
        self.product_uuid = product_uuid
        self.product_name = product_name
        self.nftokenid = nftokenid
        self.transhash = transhash
        self.product_stage = product_stage

class ProductModel(Base):
    __tablename__ = 'product_model'

    uuid = db.Column(db.Text)
    name = db.Column(db.Text)
    org = db.Column(db.Text)
    image = db.Column(db.Text)
    default_stage = db.Column(db.Text)
    
    def __init__(self, uuid, name, org, image, default_stage):
        self.uuid = uuid
        self.name = name
        self.org = org
        self.image = image
        self.default_stage = default_stage
    

class ProductStages(Base):
    __tablename__ = 'product_stages'

    product_id = db.Column(db.Text)
    stage_name = db.Column(db.Text)
    stage_number = db.Column(db.Integer)
    
    def __init__(self, product_id, stage_name, stage_number):
        self.product_id = product_id
        self.stage_name = stage_name
        self.stage_number = stage_number

class ProductMetadata(Base):
    __tablename__ = 'product_metadata'

    product_id = db.Column(db.Text)
    meta_name = db.Column(db.Text)
    
    def __init__(self, product_id, meta_name):
        self.product_id = product_id
        self.meta_name = meta_name
    