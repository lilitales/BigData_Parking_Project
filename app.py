
from flask import Flask, request, jsonify
from flask_cors import CORS
import datasource.mongodb as mongodb

app = Flask(__name__)
CORS(app)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route('/realtime_parking', methods=['GET'])
def get_realTime_parking():
    db = mongodb.obtain_db()
    realTime_col = db['RealTime_ParkingAvailability']
    res = realTime_col.find_one()
    return jsonify(res)


@app.route('/CarParkInformation', methods=['GET'])
def get_carParkInformation():
    db = mongodb.obtain_db()
    col = db['CarParkInformation']
    # condition, projection
    resList = list(col.find({}, {"_id": 0}))
    return jsonify(resList)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5100, debug=True)
