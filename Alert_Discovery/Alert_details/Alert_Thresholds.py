from flask import Blueprint, jsonify, request
import requests, psycopg2

app_r = Blueprint('app_r', __name__)


@app_r.route("/get_alert_thresholds", methods=["GET"])
def get_all_alert_thresholds():
    try:
        conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password='User@123', port=5432)
        cur = conn.cursor()
        query = f"""select * from alerts"""
        cur.execute(query)
        cols = [column[0] for column in cur.description]
        rows = cur.fetchall()
        ll = []

        if len(rows) > 0:
            for eachRow in rows:
                ll.append(dict(zip(cols, eachRow)))

            return jsonify({"type": "success", "alert_thresholds": ll})
        else:
            return jsonify({"type": "error", "message": "No alert thresholds found"})

    except Exception as e:
        return jsonify({"type": "error", "message": f"Error: {str(e)}"})


@app_r.route("/single_alert_thresholds", methods=["GET"])
def single_alert_thresholds():
    id = request.args.get('id')

    if not id:
        return jsonify({"message": "Alert ID is missing"}), 400

    try:
        conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password='User@123', port=5432)
        cur = conn.cursor()
        query = f"""select * from alerts where alert_id={id}"""
        cur.execute(query)
        cols = [column[0] for column in cur.description]
        rows = cur.fetchall()
        ll = []

        if len(rows) > 0:
            for eachRow in rows:
                ll.append(dict(zip(cols, eachRow)))

            return jsonify({"type": "success", "alert_details": ll})
        else:
            return jsonify({"type": "error", "message": f"No alert found with ID {id}"})

    except Exception as e:
        return jsonify({"type": "error", "message": f"Error: {str(e)}"})


@app_r.route("/delete_alert_thresholds", methods=['DELETE'])
def delete_alert_thresholds(*args):
    id = request.args.get('id')

    if not id:
        return jsonify({"message": "Alert ID is missing"}), 400

    base_url = "http://app.autointelli.com:3000/"
    s = requests.Session()
    s.auth = ('admin', 'Wigtra@autointelli1')
    conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password='User@123', port=5432)
    cur = conn.cursor()

    try:
        query = """SELECT alert_uid from alerts WHERE alert_id='{0}' """.format(id)
        cur.execute(query)
        uid = cur.fetchone()[0]

        query = """DELETE from alerts WHERE alert_id={0}""".format(id)
        cur.execute(query)
        conn.commit()

        response = s.delete(base_url + f"api/v1/provisioning/alert-rules/{uid}")

        if response.status_code == 204:
            return jsonify({"result": "Success", "message": "Alert deleted successfully!!"})
        else:
            raise Exception(f"Failed to delete alert: External API returned status code {response.status_code}")

    except Exception as e:
        return jsonify({"type": "error", "message": f"Error: {str(e)}"})
