from flask import Blueprint, render_template, request, abort
from app.api.routes_funcs import stages_from_nftokenid, render_metafields_dashboard, gather_product_information
from app.models.database import Wallet, ProductModel, Product, ProductStages
from app import app
import os
import json
import shortuuid

api = Blueprint('api', __name__, url_prefix='/api')

# TO DO: COMBINE BOTH OF THESE ROUTES/FUNCTIONS

@api.route('/get_product_stages/<nftokenid>')
def get_product_stages(nftokenid):
    return stages_from_nftokenid(nftokenid)

@api.route('/get_metafield_dashboard/<nftokenid>')
def get_metafield_dashboard(nftokenid):
    return render_metafields_dashboard(nftokenid)

@api.route('/get_product_information/<nftokenid>')
def get_product_information(nftokenid):
    # Return ALL on-chain/off-chain information about a product
    return gather_product_information(nftokenid)
