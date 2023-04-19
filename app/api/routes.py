from flask import Blueprint, abort, request
from app.api.routes_funcs import stages_from_nftokenid, render_metafields_dashboard, gather_product_information, \
new_stage_route_func, new_meta_field_func, next_stage_func
from ..backend.routes_tasks import new_mint, create_stage_update, create_meta_nft
from celery.result import AsyncResult

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/task_status/<task_id>')
def task_status(task_id):
    result = AsyncResult(task_id)
    return result.state

# DASHBOARD FUNCTIONS
@api.route('/get_metafield_dashboard/<nftokenid>')
def get_metafield_dashboard(nftokenid):
    return render_metafields_dashboard(nftokenid)

# MAIN APIs
@api.route('/get_product_information/<nftokenid>')
def get_product_information(nftokenid):
    # Return ALL on-chain/off-chain information about a product
    try:
        return gather_product_information(nftokenid)
    except:
        return abort(404)
    
@api.route('/get_product_stages/<nftokenid>')
def get_product_stages(nftokenid):
    try:
        return stages_from_nftokenid(nftokenid)
    except:
        return abort(404)

# Form submit alternatives

@api.route('/new_stage', methods=['POST'])
def new_stage_route():
    # uuid: product uuid 
    # stage_name: name of new stage
    return new_stage_route_func(request.json)

@api.route('/new_meta_field', methods=['POST'])
def new_meta_field_route():
    # uuid: product uuid 
    # meta_name: name of new meta field
    return new_meta_field_func(request.json)

@api.route('/next_stage', methods=['POST'])
def next_state_route():
    # uuid
    return next_stage_func(request.json)

@api.route('/new_product_mint', methods=['POST'])
def new_mint_route():
    # uuid
    content = request.json
    task = new_mint.delay(content['uuid'])
    return 'success'

@api.route('/create_meta_nft', methods=['POST'])
def new_meta_route():
    # meta object, from form: 'request.form' & uuid
    pass


