from flask import Blueprint, render_template, request, abort
from app.api.routes_funcs import stages_from_nftokenid
from app.models.database import Wallet, ProductModel, Product, ProductStates
from app import app
import os
import json
import shortuuid

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/get_product_stages/<nftokenid>')
def get_product_stages(nftokenid):
    return stages_from_nftokenid(nftokenid)