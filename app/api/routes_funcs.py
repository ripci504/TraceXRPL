from flask import request
from app.models.database import ProductModel, Product, ProductStages, ProductMetadata
from app.models.models import XrpNetwork, URIStageStructure
from app.helpers.helper_funcs import shrink_nftokenid
from ..backend.routes_tasks import new_mint, create_stage_update, create_meta_nft

import requests
import json
from app import db

### XRPL MODULES:
from xrpl.models.requests import AccountNFTs
from xrpl.clients import JsonRpcClient
from xrpl.utils import hex_to_str
###

test_net = XrpNetwork({'domain': 's.altnet.rippletest.net', 'json_rpc': 'https://s.altnet.rippletest.net:51234', 'websocket': 'wss://s.altnet.rippletest.net:51233', 'type': 'testnet' })

# SET NETWORK
network = test_net

# STAGES
def stages_from_nftokenid(nftokenid):
    stages_return = []
    product = Product.query.filter_by(nftokenid=nftokenid).first()
    stages = ProductStages.query.filter_by(product_id=product.product_uuid).all()
    r = requests.post('http://clio.altnet.rippletest.net:51233/', data=json.dumps({"method": "nft_info", "params": [{"nft_id": nftokenid}]}))
    product_issuer = json.loads(r.text)['result']['issuer']
    for count, x in enumerate(stages, 1):
        if count <= product.product_stage:
            active = True
            date, validatingNFT = get_date_from_nftoken(nftokenid, product_issuer, count)
        else:
            active = False
            date = False
            validatingNFT = False
        stages_dict = {
            'stage_name': x.stage_name,
            'stage_number': x.stage_number,
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
            if shrink_nftokenid(URI_dict['id']) == shrink_nftokenid(nftokenid) and URI_dict['stage'] == count:
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
    
def gather_product_information(nftokenid):
    # Variables to build master dict
    product = Product.query.filter_by(nftokenid=nftokenid).first()
    product_model = ProductModel.query.filter_by(uuid=product.product_uuid).first()
    r = requests.post('http://clio.altnet.rippletest.net:51233/', data=json.dumps({"method": "nft_info", "params": [{"nft_id": nftokenid}]}))
    product_stages = stages_from_nftokenid(nftokenid)
    product_data = json.loads(r.text)['result']['uri']
    product_owner = json.loads(r.text)['result']['owner']
    validated_metadata = json.loads(render_metafields_dashboard(nftokenid))
    if validated_metadata['type'] != 'created':
        validated_metadata = False
    else:
        validated_metadata.pop('type')
        validated_metadata['validating_id'] = validated_metadata.pop('nftokenid')

    
    
    master = {
        'nftokenid': nftokenid,
        'transaction_hash': product.transhash,
        'owner': product_owner,
        'data': {
            'product_stages': product_stages,
            'product_data': json.loads(hex_to_str(product_data)),
            'product_metadata': validated_metadata,
            'product_image': product_model.image,
            'product_image_url': request.url_root + 'static/uploads/' + product_model.image
        }
    }
    return master

# FORM SUBMIT ALTERNATIVES

def new_stage_route_func(content):
    stages = ProductStages.query.filter_by(product_id=content['uuid']).all()
    x = 0
    for _ in stages:
        x += 1
    newstage = ProductStages(product_id=content['uuid'], stage_name=content['stage_name'], stage_number=str(x+1))
    db.session.add(newstage)
    db.session.commit()
    return 'success'

def new_meta_field_func(content):
    metadata = ProductMetadata.query.filter_by(product_id=content['uuid']).all()
    x = 0
    for _ in metadata:
        x += 1
    if x >= 5:
        pass
        #return redirect('/products/' + uuid)
    newfield = ProductMetadata(product_id=content['uuid'], meta_name=content['meta_name'])
    db.session.add(newfield)
    db.session.commit()
    return 'success'

def next_stage_func(content):
    nftokenid = request.form.get('nftokenid')
    product_minted = Product.query.filter_by(nftokenid=nftokenid).first()
    stages = ProductStages.query.filter_by(product_id=content['uuid']).all()
    x = 0
    for _ in stages:
        x += 1
    if product_minted.product_stage < x:
        product_minted.product_stage += 1
        db.session.commit()
        task = create_stage_update.delay(product_minted.product_stage, x, nftokenid, content['uuid'])
        return 'success'
    else:
        return 'failure'