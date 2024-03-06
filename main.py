import sentry_sdk
from sentry_sdk import capture_exception
from flask import request,jsonify,flash
from flask_sqlalchemy import SQLAlchemy
from dbs import Product,app,db,Sale,User
from flask_cors import CORS
import requests
from sqlalchemy import func
import datetime
import jwt
from functools import wraps
import re
from werkzeug.security import generate_password_hash

sentry_sdk.init(
    dsn="https://523b09eaf79187c3156c08fe21297c7b@us.sentry.io/4506695594147840",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

CORS(app)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = data['username']
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)
    return decorated

password_requirement = r"^(?=.*\d)(?=.*[!@#$%^&*()])(?=.*[a-zA-Z]).{8,}$"

def is_valid_password(password):
    return bool(re.match(password_requirement, password))

@app.route("/register" ,methods=["POST"])
def register():
        try:
            data = request.json
            u = data["username"]
            p = data["password"]
            hashed_password = generate_password_hash(p)
        except KeyError:
            return jsonify({"feedback": "Please provide both 'username' and 'password' fields"}), 400

        if User.query.filter_by(username=u).first() is not None:
            return jsonify({"result": f"User '{u}' already exists"}), 409

        if len(u) == 0:
            return jsonify({"result": "ensure you have entered your username"}), 400

        if not is_valid_password(p):
            return jsonify({"result": "Password must contain at least one digit, one symbol, and one letter and be at least 8 characters long"}), 400

        new_user = User(username=u, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"result" : f"succesfully registered `{u}` ID : {str(new_user.id)}"}), 201

        
@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.json
        u=data["username"]
        p=data["password"]
    except Exception as e:
        return jsonify({"result": "invalid credentials"}),400

    if User.query.filter_by(username=u ,password=p).count()>0:
        token = jwt.encode({'username': u, 'exp': datetime.datetime.utcnow() 
                            + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
        
        return jsonify({"results" : "success" , "access tocken" : token }),200
    else:
        return jsonify({"result": "invalid credentials"}),403


@app.route("/products", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
@token_required
def prods(current_user):
    if request.method == "GET":
        
        try:
            prods = Product.query.all()
            res = []
            for i in prods:
                res.append({"id": i.id,"name": i.name, "price": i.price })
            
            return jsonify(res), 200
            
        except Exception as e:
            # capture_exception(e)
            return jsonify({"Error" : str(e)}), 500




            
    elif request.method == "POST":
        if request.is_json:
           try:
                data = request.json
                new_data = Product(name=data['name'], price= data['price'])
                db.session.add(new_data)
                db.session.commit()
                r = f'Successfully stored product id: {str(new_data.id)}'
                res = {"Result" : r}
                return jsonify(res), 201
           except Exception as e:
                return jsonify({"Error" : str(e)}), 500
        else:
            return jsonify({"Error" : "Data is not json"}), 400 
    else:
        return jsonify({"Error" : "Method not allowed."}), 403
    
@app.route('/get-product/<int:product_id>', methods=['GET'])
def get_one_product(product_id):
    try:
        product = Product.query.get(product_id)
        if product:
            return jsonify({
                "id": product.id,
                "name": product.name,
                "price": product.price
            })
        else:
            return jsonify({"error": "product does not exist."}), 404
    except Exception as e:
        print(e)
        # capture_exception(e)
        return jsonify({"error": "Internal Server Error"}), 500
    
    
@app.route("/sales",methods=["POST","GET"])
def sales():
    if request.method=="GET":
        try:
            sales=Sale.query.all()
            s_dict = []
            for sale in sales:
                s_dict.append({"id": sale.id,"pid": sale.pid, "quantity": sale.quantity,"created_at":sale.created_at })
            
            return jsonify(s_dict), 200
        except Exception as e:
            # capture_exception(e)
            return jsonify({}), 500
        
    elif request.method == "POST":
        if request.is_json:
           try:
                data = request.json
                new_sales = Sale(pid=data['pid'], quantity= data['quantity'])
                db.session.add(new_sales)
                db.session.commit()
                s = f'Successfully stored product id: {str(new_sales.id)}'
                sel = {"Result" : s}
                return jsonify(sel), 201
           except Exception as e:
                return jsonify({"Error" : str(e)}), 500
        else:
            return jsonify({"Error" : "Data is not json"}), 400 
    else:
        return jsonify({"Error" : "Method not allowed."}), 403


@app.route("/dashboard", methods=["GET"])
def dashboard():
    # response={
    #     'Realtime Currency Exchange Rate': 
    #     {'1. From_Currency Code': 'USD',
    #      '2. From_Currency Name': 'United States Dollar', 
    #      '3. To_Currency Code': 'KES', 
    #      '4. To_Currency Name': 'Kenyan Shilling', 
    #      '5. Exchange Rate': '144.98000000', 
    #      '6. Last Refreshed': '2024-02-26 15:24:53', 
    #      '7. Time Zone': 'UTC', 
    #      '8. Bid Price': '144.97500000', 
    #      '9. Ask Price': '144.98300000'}}
    
    # api_key = "JOF2V2FO9VW3I9SX"
    # url='https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=USD&to_currency=KES&apikey='+api_key
    # r = requests.get(url)
    # data = r.json()
    # to_currency_code = data['Realtime Currency Exchange Rate']['3. To_Currency Code']
    # exchange_rate = data['Realtime Currency Exchange Rate']['5. Exchange Rate']

    # output = {to_currency_code.lower(): exchange_rate}



    sales_per_day = db.session.query(
        # extracts date from created at
        func.date(Sale.created_at).label('date'),
        # calculate the total number of sales per day
        func.sum(Sale.quantity * Product.price).label('total_sales')
    ).join(Product).group_by(
        func.date(Sale.created_at)
    ).all()

    #  to JSON format
    sales_data = [{'date': str(day), 'total_sales': sales}
                  for day, sales in sales_per_day]
    #  sales per product
    sales_per_product = db.session.query(
        Product.name,
        func.sum(Sale.quantity*Product.price).label('sales_product')
    ).join(Sale).group_by(
        Product.name
    ).all()

    # to JSON format
    salesproduct_data = [{'name': name, 'sales_product': sales_product}
                         for name, sales_product in sales_per_product]

    return jsonify({'sales_data': sales_data, 'salesproduct_data': salesproduct_data})

    


@app.route("/mydata")
def mydata():
    api_key="JOF2V2FO9VW3I9SX"
    url='https://www.alphavantage.co/query?function=REAL_GDP&interval=quarterly&apikey='+api_key
    r=requests.get(url)
    data=r.json()

    print(data)
    return data

    
    

if  __name__ == "__main__":
   with app.app_context():
       db.create_all()
   app.run(debug=True)
