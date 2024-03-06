from flask import Blueprint, jsonify, request
import requests

app_bp = Blueprint('app_bp', __name__)


@app_bp.route("/get_alert_payload", methods=["GET"])
def get_alert_payload():
    base_url = "http://app.autointelli.com:3000/"

    s = requests.Session()
    s.auth = ('admin', 'Wigtra@autointelli1')

    try:
        resp = s.get(base_url + "api/v1/provisioning/alert-rules", verify=False)
        resp.raise_for_status()
        data = resp.json()

        if not data:
            raise Exception("No alerts found")

        return jsonify({"type": "success", "data": data})

    except Exception as e:
        return jsonify({"type": "error", "message": f"No alerts created: {str(e)}"})


@app_bp.route("/single_alert_payload", methods=["GET"])
def single_alert_payload():
    try:
        id = request.args.get('id')
        if not id:
            return jsonify({"error": "Alert ID not provided"}), 400

        base_url = "http://app.autointelli.com:3000/"

        s = requests.Session()
        s.auth = ('admin', 'Wigtra@autointelli1')
        resp = s.get(f"{base_url}api/v1/provisioning/alert-rules/{id}", verify=False)
        data = resp.json()

        return jsonify(data), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app_bp.route("/delete_alert_payload", methods=['DELETE'])
def delete_alert_payload(*args):
    id = request.args['id']
    base_url = "http://app.autointelli.com:3000/"

    s = requests.Session()
    s.auth = ('admin', 'Wigtra@autointelli1')

    response = s.delete(base_url + f"api/v1/provisioning/alert-rules/{id}")

    if response.status_code == 204:
        return jsonify({"type": "success", "message": "Alert deleted successfully"})
    else:
        return jsonify({"type": "error", "message": f"Failed to delete alert: {response.text}"})
