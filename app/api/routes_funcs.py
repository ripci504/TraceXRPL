from app.models.database import Wallet, ProductModel, Product, ProductStates, ProductMetadata
from app.models.models import XrpNetwork, URIStageStructure
from app.helpers.helper_funcs import shrink_nftokenid, expand_nftokenid
import requests
import json

### XRPL MODULES:
from xrpl.models.requests import AccountNFTs
from xrpl.clients import JsonRpcClient
from xrpl.utils import hex_to_str, str_to_hex
###

test_net = XrpNetwork({'domain': 's.altnet.rippletest.net', 'json_rpc': 'https://s.altnet.rippletest.net:51234', 'websocket': 'wss://s.altnet.rippletest.net:51233', 'type': 'testnet' })

# SET NETWORK
network = test_net

# STAGES
def stages_from_nftokenid(nftokenid):
    stages_return = []
    product = Product.query.filter_by(nftokenid=nftokenid).first()
    states = ProductStates.query.filter_by(product_id=product.product_uuid).all()
    r = requests.post('http://clio.altnet.rippletest.net:51233/', data=json.dumps({"method": "nft_info", "params": [{"nft_id": nftokenid}]}))
    product_issuer = json.loads(r.text)['result']['issuer']
    for count, x in enumerate(states, 1):
        if count <= product.product_state:
            active = True
            date, validatingNFT = get_date_from_nftoken(nftokenid, product_issuer, count)
        else:
            active = False
            date = False
            validatingNFT = False
        stages_dict = {
            'stage_name': x.state_name,
            'stage_number': x.state_number,
            'active': active,
            'date': date,
            'validating_id': validatingNFT
        }
        stages_return.append(stages_dict)

    return stages_return

# Helper func to search issuer for product stage related NFTs and retrieve date of creation.
def get_date_from_nftoken(nftokenid, issuer, count):
    client=JsonRpcClient(network.to_dict()['json_rpc'])
    response = client.request(AccountNFTs(account=issuer))
    for nft in response.result['account_nfts']:
        try:
            URI_dict = json.loads(hex_to_str(nft['URI']).replace("\'", "\""))
            URIStageStructure(**URI_dict)
            # After this, validation is success or it will continue
            if shrink_nftokenid(URI_dict['id']) == shrink_nftokenid(nftokenid) and URI_dict['state'] == count:
                return URI_dict['date'], nft['NFTokenID']
        except:
            # Structure validation failed, continue to next NFT
            continue

# METADATA
def render_metafields_dashboard(nftokenid):
    metadata_dict = {}
    product = Product.query.filter_by(nftokenid=nftokenid).first()
    metadata = ProductMetadata.query.filter_by(product_id=product.product_uuid).all()
    r = requests.post('http://clio.altnet.rippletest.net:51233/', data=json.dumps({"method": "nft_info", "params": [{"nft_id": nftokenid}]}))
    product_issuer = json.loads(r.text)['result']['issuer']
    client=JsonRpcClient(network.to_dict()['json_rpc'])
    response = client.request(AccountNFTs(account=product_issuer))
    found_nftokenid = False
    for nft in response.result['account_nfts']:
        try:
            URI_dict = json.loads(hex_to_str(nft['URI']).replace("\'", "\""))
            if shrink_nftokenid(URI_dict['id']) == shrink_nftokenid(nftokenid) and URI_dict['id'][:3] == 'mta':
                found_nftokenid = nft['NFTokenID']
                found_uri = URI_dict
        except:
            continue
    if found_nftokenid:
        found_uri.pop('id')
        metadata_dict['type'] = 'created'
        metadata_dict['nftokenid'] = found_nftokenid
        metadata_dict['uri'] = found_uri
    else:
        metadata_dict['type']= 'not_created'
        for i in metadata:
            metadata_dict[i.id]=i.meta_name
    return json.dumps(metadata_dict)
    