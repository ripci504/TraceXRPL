from app.models.models import XrpNetwork
from app import db, app
from app.models.database import Wallet, Product, ProductStages, ProductModel, ProductMetadata
from .routes_tasks import new_mint, create_stage_update, create_meta_nft
from flask import redirect

### XRPL MODULES:
from xrpl.clients import JsonRpcClient
from xrpl.wallet import generate_faucet_wallet
###

test_net = XrpNetwork({'domain': 's.altnet.rippletest.net', 'json_rpc': 'https://s.altnet.rippletest.net:51234', 'websocket': 'wss://s.altnet.rippletest.net:51233', 'type': 'testnet' })

# SET NETWORK
network = test_net

# Create testnet wallet on server initiation
def generate_wallet(*args):
    # Wait for app context
    with app.app_context():
        db.create_all()
        query = Wallet.query.all()
        if query:
            pass
        else:
            network = XrpNetwork({'domain': 's.altnet.rippletest.net', 'json_rpc': 'https://s.altnet.rippletest.net:51234', 'websocket': 'wss://s.altnet.rippletest.net:51233', 'type': 'testnet' })
            network = network.to_dict()
            wallet = generate_faucet_wallet(client=JsonRpcClient(network['json_rpc']))
            wallet = Wallet(seed=wallet.seed, address=wallet.classic_address, net=network['type'])
            db.session.add(wallet)
            db.session.commit()

def create_product_temp(org, product_uuid, name, filename, default_stage):
    product = ProductModel(uuid=product_uuid, org=org, name=name, image=filename, default_stage=default_stage)
    db.session.add(product)
    db.session.commit()
    return redirect('/products/' + product_uuid)

def handle_products_form(request, uuid):
    if request.form.get('type') == 'new_stage':
        stages = ProductStages.query.filter_by(product_id=uuid).all()
        x = 0
        for _ in stages:
            x += 1
        newstage = ProductStages(product_id=uuid, stage_name=request.form.get('new_stage'), stage_number=str(x+1))
        db.session.add(newstage)
        db.session.commit()
        return redirect('/products/' + uuid)
    elif request.form.get('type') == 'new_meta':
        metadata = ProductMetadata.query.filter_by(product_id=uuid).all()
        x = 0
        for _ in metadata:
            x += 1
        if x >= 5:
            return redirect('/products/' + uuid)
        newfield = ProductMetadata(product_id=uuid, meta_name=request.form.get('new_meta'))
        db.session.add(newfield)
        db.session.commit()
        return redirect('/products/' + uuid)
    elif request.form.get('type') == 'next_stage':
        nftokenid = request.form.get('nftokenid')
        product_minted = Product.query.filter_by(nftokenid=nftokenid).first()
        stages = ProductStages.query.filter_by(product_id=uuid).all()
        x = 0
        for _ in stages:
            x += 1
        if product_minted.product_stage < x:
            product_minted.product_stage += 1
            db.session.commit()
            task = create_stage_update.delay(product_minted.product_stage, x, nftokenid, uuid)
            return redirect('/products/' + uuid)
        else:
            return redirect(request.url)
    elif request.form.get('type') == 'new_mint':
        task = new_mint.delay(uuid)
        return redirect('/products/' + uuid)
    elif request.form.get('type') == 'create_meta':
        task = create_meta_nft.delay(request.form, uuid)
        return redirect('/products/' + uuid)

def get_stage_dict(nftokenid):
    product = Product.query.filter_by(nftokenid=nftokenid).first()
    stages = ProductStages.query.filter_by(product_id=product.product_uuid).all()
    product_stages_list = []
    for x, _ in enumerate(stages, 1):
        product_stages_list.append(False)
    if x != 0:
        for n in range(product.product_stage):
            product_stages_list[n] = True
        per = 1 / x
        percentage = 0
        stage = 0
        for y in product_stages_list:
            if y == True:
                percentage += per
                stage += 1
        stage_dict ={
            'percentage': int(percentage * 100),
            'stage': stage,
            'max_stage': x
        }
    else:
        stage_dict ={
            'percentage': 100,
            'stage': '0',
            'max_stage': '0'
        }
    return stage_dict
