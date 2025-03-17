from flask import Flask
from flask import jsonify
from controller.stock_controller import stock_controller

app = Flask(__name__)
app.register_blueprint(stock_controller, url_prefix='/')

@app.errorhandler(ValueError)
def handle_value_error(error):
    response = {
        "error": str(error)
    }
    return jsonify(response), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6128)