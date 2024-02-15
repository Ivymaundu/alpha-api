import sentry_sdk
from sentry_sdk import capture_exception
from flask import request,jsonify
from flask_sqlalchemy import SQLAlchemy
from dbs import Product,app,db

sentry_sdk.init(
    dsn="https://523b09eaf79187c3156c08fe21297c7b@us.sentry.io/4506695594147840",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)






@app.route("/products", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
def prods():
    if request.method == "GET":
        try:
            prods = Product.query.all()
            res = []
            for i in prods:
                res.append({"id": i.id,"name": i.name, "price": i.price })
                break
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
    
    
if  __name__ == "__main__":
   with app.app_context():
       db.create_all()
   app.run(debug=True)
