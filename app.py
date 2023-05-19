import json
from flask import Flask, jsonify, Response, request, abort
from flask_restx import Api, Resource, fields

def create_app():
    app = Flask(__name__)
    api = Api(app)
    products = api.namespace('products', description="Product API")

    f = open("./dataSource.json", "r")
    loaded_json = json.load(f)
    product_info = {
        f'{dct["title"]} - {dct["price"]}': dct
        for dct in loaded_json.get("products_list")
    }

    product_data = api.model(
        'Product Model', {
            "title": fields.String(description="Title of Product", required=True),
            "price": fields.Integer(description="Price of Product", required=True),
            "description": fields.String(description="Description", required=False)
        }
    )

    @products.route("/")
    class Products(Resource):
        def get(self):
            return jsonify(product_info)

        @api.expect(product_data)
        def post(self):
            params = request.get_json()
            t = params.get("title", "")
            p = params.get("price", "")

            if t and p:
                try:
                    new_id = f'{t} - {p}'
                    if new_id in product_info.keys():
                        abort(409, description='Already Exists')
                    product_info[new_id] = params
                    for p_key in params:
                        if p_key not in product_info[new_id].keys():
                            raise KeyError
                except:
                    abort(400, description='Bad parameters')
            else:
                abort(400, description='Missing Title or Price')
            return Response(status=200)

        @products.doc(params={'id': 'ID of the product'}, description="Delete a product by ID")
        def delete(self):
            id = request.args.get('id')
            if id is None:
                abort(400, description='Missing Id')
            try:
                del product_info[id]
            except KeyError:
                abort(code = 404, description = f"Movie '{id}' doesn't exists.")
            return Response(code = 200)

    api.add_resource(Products, '/')

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
