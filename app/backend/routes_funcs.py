from app.models.models import XrpNetwork
from app import db, app
from app.models.database import Wallet, Product, ProductStages, ProductModel, ProductMetadata
from app.helpers.helper_funcs import shrink_nftokenid, shrink_json
from flask import redirect, request
import time
import requests
import json


### XRPL MODULES:
from xrpl.models.transactions.nftoken_mint import NFTokenMint, NFTokenMintFlag
from xrpl.wallet import Wallet as XRPLWallet
from xrpl.clients import JsonRpcClient
from xrpl.wallet import generate_faucet_wallet
from xrpl.utils import hex_to_str, str_to_hex, datetime_to_ripple_time, get_nftoken_id
from xrpl.transaction import safe_sign_and_autofill_transaction, send_reliable_submission, safe_sign_and_submit_transaction, get_transaction_from_hash
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
    if request.form.get('type') == 'new_meta':
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
    elif request.form.get('type') == 'new_mint':
        product = ProductModel.query.filter_by(uuid=uuid).first()
        products_minted = Product.query.filter_by(product_uuid=uuid).all()
        # COUNT PRODUCTS MINTED TO GET MODEL NUMBER
        x = 0
        for _ in products_minted:
            x += 1
        # INITIATE WALLET
        database_wallet = Wallet.query.all()
        client=JsonRpcClient(network.to_dict()['json_rpc'])
        xrplwallet = XRPLWallet(seed=database_wallet[0].seed, sequence=0)
        # BUILD DICT URI
        nftokenobject = {
            'org': product.org, # MAX 30
            'product': product.name, # MAX 20
            'model': x, # MAX 10
            'creation': int(time.time()) # MAX 12
        }
        # CREATE MINT REQUEST
        mint_tx = NFTokenMint(
            account=xrplwallet.classic_address,
            nftoken_taxon=0,
            flags=NFTokenMintFlag.TF_TRANSFERABLE,
            uri=shrink_json(nftokenobject)
        )
        # SEND MINT REQUEST
        try:
            mint_tx_signed = safe_sign_and_autofill_transaction(transaction=mint_tx, wallet=xrplwallet, client=client)
            mint_tx_signed = send_reliable_submission(transaction=mint_tx_signed, client=client)
            mint_tx_result = mint_tx_signed.result
            new_product = Product(product_uuid=uuid, product_name=product.name, nftokenid=get_nftoken_id.get_nftoken_id(mint_tx_result['meta']), transhash=mint_tx_result['hash'], product_stage=product.default_stage)
            db.session.add(new_product)
            db.session.commit()
        except Exception as e:
            return str(e)
        return redirect('/products/' + uuid)
    elif request.form.get('type') == 'next_stage':
        nftokenid = request.form.get('nftokenid')
        product = ProductModel.query.filter_by(uuid=uuid).first()
        product_minted = Product.query.filter_by(nftokenid=nftokenid).first()
        stages = ProductStages.query.filter_by(product_id=uuid).all()
        x = 0
        for _ in stages:
            x += 1
        if product_minted.product_stage < x:
            product_minted.product_stage += 1
            db.session.commit()
            return create_stage_update(product_minted.product_stage, x, nftokenid, uuid)
    elif request.form.get('type') == 'create_meta':
        return create_meta_nft(request, uuid)

def create_meta_nft(request, uuid):
    nftokenobject = {}
    metadata = ProductMetadata.query.filter_by(product_id=uuid).all()
    for x in metadata:
        nftokenobject[x.meta_name] = request.form.get(x.meta_name)
    nftokenobject['id']='mta' + shrink_nftokenid(request.form.get('nftokenid'))
    database_wallet = Wallet.query.all()
    client=JsonRpcClient(network.to_dict()['json_rpc'])
    xrplwallet = XRPLWallet(seed=database_wallet[0].seed, sequence=0)
    
    mint_tx = NFTokenMint(
    account=xrplwallet.classic_address,
    nftoken_taxon=0,
    flags=NFTokenMintFlag.TF_TRANSFERABLE,
    uri=shrink_json(nftokenobject)
    )

    # SEND MINT REQUEST
    try:
        mint_tx_signed = safe_sign_and_autofill_transaction(transaction=mint_tx, wallet=xrplwallet, client=client)
        mint_tx_signed = send_reliable_submission(transaction=mint_tx_signed, client=client)
        mint_tx_result = mint_tx_signed.result
    except Exception as e:
        return str(e)
    return redirect('/products/' + uuid)
        



def create_stage_update(stage, max, id, uuid):
    # QUERY DB but there will only be one row
    # This func will take time, use celery 
    database_wallet = Wallet.query.all()
    client=JsonRpcClient(network.to_dict()['json_rpc'])
    xrplwallet = XRPLWallet(seed=database_wallet[0].seed, sequence=0)
    nftokenobject = {
        'date': int(time.time()), # MAX 12
        'stage': stage, # MAX 3
        'max': max, # MAX 3
        'id': shrink_nftokenid(id) # MAX 16 (SHRUNK NFTOKENID)
    }
    mint_tx = NFTokenMint(
        account=xrplwallet.classic_address,
        nftoken_taxon=0,
        flags=NFTokenMintFlag.TF_TRANSFERABLE,
        uri=shrink_json(nftokenobject)
    )
    # SEND MINT REQUEST
    try:
        mint_tx_signed = safe_sign_and_autofill_transaction(transaction=mint_tx, wallet=xrplwallet, client=client)
        mint_tx_signed = send_reliable_submission(transaction=mint_tx_signed, client=client)
        mint_tx_result = mint_tx_signed.result
    except Exception as e:
        return str(e)
    return redirect('/products/' + uuid)

def get_nftoken_data(nftokenid):
    product = Product.query.filter_by(nftokenid=nftokenid).first()
    product_model = ProductModel.query.filter_by(uuid=product.product_uuid).first()
    # Connect to altnet clio server to access special nft_info method
    r = requests.post('http://clio.altnet.rippletest.net:51233/', data=json.dumps({"method": "nft_info", "params": [{"nft_id": nftokenid}]}))
    product_xrpl = json.loads(r.text)['result']['uri'].replace("\'", "\"")
    product_owner = json.loads(r.text)['result']['owner']

    ## CREATE PRODUCT STAGES & LISTS
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
        product_history = []
    else:
        stage_dict ={
            'percentage': 100,
            'stage': '0',
            'max_stage': '0'
        }
        product_history = []
    ## GET VALIDATED PRODUCT HISTORY FROM XRPL
    r = requests.get(request.host_url + '/api/get_product_stages/' + nftokenid)
    validated_history = json.loads(r.text)
    ## GET VALIDATED PRODUCT METADATA FROM XRPL
    res = requests.get(request.host_url + '/api/get_metafield_dashboard/' + nftokenid)
    validated_metadata = json.loads(res.text)
    if validated_metadata['type'] != 'created':
        validated_metadata = False
        
    return product, product_model, product_xrpl, product_owner, product_history, stage_dict, validated_history, validated_metadata
