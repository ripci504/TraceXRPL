from app.backend.models import XrpNetwork
from app import db, app
from app.backend.database import Wallet, Product, ProductStates, ProductModel
from flask import redirect
import time

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


def create_product_temp(org, product, name):
    product = ProductModel(uuid=product, org=org, name=name)
    db.session.add(product)
    db.session.commit()
    return 'success'

def handle_products_form(request, uuid):
    if request.form.get('type') == 'new_stage':
        states = ProductStates.query.filter_by(product_id=uuid).all()
        x = 0
        for _ in states:
            x += 1
        newstate = ProductStates(product_id=uuid, state_name=request.form.get('new_stage'), state_number=str(x+1))
        db.session.add(newstate)
        db.session.commit()
        return redirect('/products/' + uuid)
    else:
        product = ProductModel.query.filter_by(uuid=uuid).first()
        products_minted = Product.query.filter_by(product_uuid=uuid).all()
        # COUNT PRODUCTS MINTED TO GET MODEL NUMBER
        x = 0
        for _ in products_minted:
            x += 1
        # INITIATE WALLET
        database_wallet = Wallet.query.all()
        client=JsonRpcClient(network['json_rpc'])
        xrplwallet = XRPLWallet(seed=database_wallet[0].seed, sequence=0)
        # BUILD DICT URI
        nftokenobject = {
            'org': product.org, # MAX 32
            'product': product.name, # MAX 20
            'model': x, # MAX 10
            'creation': time.time() # MAX 12
        }
        nftokenuri = str_to_hex(nftokenobject)
        if len(nftokenuri > 256):
            return 'object too big'
        # CREATE MINT REQUEST
        mint_tx = NFTokenMint(
            account=xrplwallet,
            nftoken_taxon=0,
            flags=NFTokenMintFlag.TF_TRANSFERABLE,
            uri=nftokenuri
        )
        # SEND MINT REQUEST
        try:
            mint_tx_signed = safe_sign_and_autofill_transaction(transaction=mint_tx, wallet=xrplwallet, client=client)
            mint_tx_signed = send_reliable_submission(transaction=mint_tx_signed, client=client)
            mint_tx_result = mint_tx_signed.result
            new_product = Product(product_uuid=uuid, product_name=product.name, nftokenid=get_nftoken_id(mint_tx_result['meta']), transhash=mint_tx_result['hash'], product_state=0)
            db.session.add(new_product)
            db.session.commit()
        except:
            pass


def create_state_update(date, state, max, id):
    # QUERY DB but there will only be one row
    # This func will take time, use celery 
    database_wallet = Wallet.query.all()
    client=JsonRpcClient(network['json_rpc'])
    xrplwallet = XRPLWallet(seed=database_wallet[0].seed, sequence=0)
    nftokenobject = {
        'date': date, # MAX 12
        'state': state, # MAX 3
        'max': max, # MAX 3
        'id': id # MAX 64 (NFTOKENID OF PARENT)
    }
    nftokenuri = str_to_hex(nftokenobject)
    if len(nftokenuri > 256):
        return 'object too big'
    mint_tx = NFTokenMint(
        account=xrplwallet,
        nftoken_taxon=0,
        flags=NFTokenMintFlag.TF_TRANSFERABLE,
        uri=nftokenuri
    )




#from xrpl.utils import hex_to_str, str_to_hex

#dictionary = {
#    'org': 'Louis Vuitton 12345678910123456', # MAX 32,
#    'product': 'Hand Bag 1 2 3 4 5 6', # MAX 20
#    'model': '1234567890', # MAX 10,
#    'creation': '167927492700' # MAX 12
#}

#nftokenobject = {
#    'date': '1234567890__', # MAX 12
#    'state': '10', # MAX 3
#    'max': '10', # MAX 3
#    'id': '000100004819DB6461BF1BC2D18B511DE0A2799EE3FCC2E90000099B00000000' # MAX 64
#}

#dictionary = str(dictionary)
#print(len(str_to_hex(dictionary)))
#print(str_to_hex(dictionary))