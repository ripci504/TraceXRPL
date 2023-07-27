from app.models.models import XrpNetwork
from app import db
from app.models.database import Wallet, Product, ProductModel, ProductMetadata
from app.helpers.helper_funcs import shrink_nftokenid, shrink_json
from celery import shared_task
import time

### XRPL MODULES:
from xrpl.models.transactions.nftoken_mint import NFTokenMint, NFTokenMintFlag
from xrpl.wallet import Wallet as XRPLWallet
from xrpl.clients import JsonRpcClient
from xrpl.utils import get_nftoken_id
from xrpl.transaction import submit_and_wait
###

test_net = XrpNetwork({'domain': 's.altnet.rippletest.net', 'json_rpc': 'https://s.altnet.rippletest.net:51234', 'websocket': 'wss://s.altnet.rippletest.net:51233', 'type': 'testnet' })

# SET NETWORK
network = test_net

@shared_task(bind=True)
def new_mint(self, uuid):
    product = ProductModel.query.filter_by(uuid=uuid).first()
    products_minted = Product.query.filter_by(product_uuid=uuid).all()
    # COUNT PRODUCTS MINTED TO GET MODEL NUMBER
    x = 0
    for _ in products_minted:
        x += 1
    # INITIATE WALLET
    database_wallet = Wallet.query.all()
    client=JsonRpcClient(network.to_dict()['json_rpc'])
    xrplwallet = XRPLWallet.from_seed(seed=database_wallet[0].seed)
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
        mint_tx_signed = submit_and_wait(transaction=mint_tx, wallet=xrplwallet, client=client)
        mint_tx_result = mint_tx_signed.result
        new_product = Product(product_uuid=uuid, product_name=product.name, nftokenid=get_nftoken_id.get_nftoken_id(mint_tx_result['meta']), transhash=mint_tx_result['hash'], product_stage=product.default_stage)
        db.session.add(new_product)
        db.session.commit()
    except Exception as e:
        return str(e)
    return 'DONE'

@shared_task(bind=True)
def create_stage_update(self, stage, max, id, uuid):
    # QUERY DB but there will only be one row
    # This func will take time, use celery 
    database_wallet = Wallet.query.all()
    client=JsonRpcClient(network.to_dict()['json_rpc'])
    xrplwallet = XRPLWallet.from_seed(seed=database_wallet[0].seed)
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
        mint_tx_signed = submit_and_wait(transaction=mint_tx, wallet=xrplwallet, client=client)
    except Exception as e:
        return str(e)
    return 'DONE'

@shared_task(bind=True)
def create_meta_nft(self, request_form, uuid):
    nftokenobject = {}
    metadata = ProductMetadata.query.filter_by(product_id=uuid).all()
    for x in metadata:
        nftokenobject[x.meta_name] = request_form[x.meta_name]
    nftokenobject['id']='mta' + shrink_nftokenid(request_form['nftokenid'])
    database_wallet = Wallet.query.all()
    client=JsonRpcClient(network.to_dict()['json_rpc'])
    xrplwallet = XRPLWallet.from_seed(seed=database_wallet[0].seed)
    
    mint_tx = NFTokenMint(
    account=xrplwallet.classic_address,
    nftoken_taxon=0,
    flags=NFTokenMintFlag.TF_TRANSFERABLE,
    uri=shrink_json(nftokenobject)
    )
    # SEND MINT REQUEST
    try:
        mint_tx_signed = submit_and_wait(transaction=mint_tx, wallet=xrplwallet, client=client)
    except Exception as e:
        return str(e)
    return 'DONE'
