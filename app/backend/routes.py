from flask import Blueprint, render_template, request
from app.backend.routes_funcs import generate_wallet, create_product_nft, create_product_temp, handle_products_form
from app.backend.database import Wallet, ProductModel, Product, ProductStates
from app import app
from werkzeug.utils import secure_filename
import os
import shortuuid


main = Blueprint('index', __name__, url_prefix='/')

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.before_first_request(generate_wallet) # func on server initiation
@main.route('/')
def index():
    return render_template('index.html')

@main.route('/create_product', methods=['POST', 'GET'])
def create_product():
    if request.method == 'POST':
        uuid = shortuuid.uuid()
        image = request.files['image']
        if image and allowed_file(image.filename):
            split_tup = os.path.splitext(image.filename)
            file_extension = split_tup[1]
            filename = secure_filename(uuid + file_extension)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        org = request.form.get('orginization')
        name = request.form.get('product')
        return create_product_temp(org=org, product=uuid, name=name)

    products = ProductModel.query.all()
    return render_template('create_product.html', products=products)

@main.route('/products/<uuid>', methods=['POST', 'GET'])
def products(uuid):
    if request.method == 'POST':
        return handle_products_form(request=request, uuid=uuid)
    products = ProductModel.query.all()
    minted_products = Product.query.filter_by(product_uuid=uuid).all()
    current_product = ProductModel.query.filter_by(uuid=uuid).first()
    states = ProductStates.query.filter_by(product_id=uuid).all()
    return render_template('view_product_dashboard.html', products=products, uuid=uuid, current_product=current_product, states=states, minted_products=minted_products)

@main.route('/portfolio/<wallet>')
def portfolio(wallet):
    pass

@main.route('/product/<nftokenid>')
def check_product(product):
    return render_template('product_jinja.html')