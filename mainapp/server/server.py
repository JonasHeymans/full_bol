from flask import Flask, jsonify, request
import xmltodict


from support.database.database import EdcDatabase


# create the Flask mainapp
app = Flask(__name__)

@app.route("/")
def home_view():
        return "<h1>Welcome</h1>"

@app.route("/edc_shipment", methods=['POST'])
def main():
    try:
        xml_data = request.get_data()
        content_dict = xmltodict.parse(xml_data)['order']

        dct = {}
        dct['ordernumber'] = content_dict['ordernumber']
        dct['own_ordernumber'] = content_dict['own_ordernumber']
        dct['new_ordernumber'] = content_dict['own_ordernumber'] if hasattr(content_dict, 'new_ordernumber') else None
        dct['tracktrace'] = content_dict['tracktrace']
        dct['shipper'] = content_dict['shipper']
        dct['status'] = content_dict['status']



        db = EdcDatabase(connection_type='fill')
        db.add_shipment(dct)

        resp = jsonify(success=True)
        resp.status_code = 200

        return resp

    except Exception as e:
        print(e)
        resp = jsonify(success=False)

        return resp

