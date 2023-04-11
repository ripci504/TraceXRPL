from flask import Blueprint, abort
from app.api.routes_funcs import stages_from_nftokenid, render_metafields_dashboard, gather_product_information

api = Blueprint('api', __name__, url_prefix='/api')

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