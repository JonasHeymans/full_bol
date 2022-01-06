from flask import Flask, jsonify, request
import xmltodict


from support.database.database import EdcDatabase


# create the Flask app
app = Flask(__name__)

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
        db.push_shipment_to_db(dct)

        resp = jsonify(success=True)
        resp.status_code = 200

        return resp

    except Exception as e:
        print(e)
        resp = jsonify(success=False)

        return resp







if __name__ == '__main__':
    app.run()