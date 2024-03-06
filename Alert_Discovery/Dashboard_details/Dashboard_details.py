from flask import jsonify, Flask, request, Blueprint
import requests, psycopg2

app_V2 = Blueprint('app_v2', __name__)


@app_V2.route('/get_all_dashboard', methods=['GET'])
def get_all_dashboard():
    base_url = "http://app.autointelli.com:3000/"

    s = requests.Session()
    s.auth = ('admin', 'Wigtra@autointelli1')

    response = s.get(base_url + "api/folders", verify=False)
    folder = []
    if response.status_code == 200:
        folders = response.json()
        for f in folders:
            folder.append(f['title'])
    else:
        return jsonify({"type": "error", "message": "Failed to fetch folders"})

    response = s.get(base_url + "api/search", verify=False)
    if response.status_code == 200:
        dashboards = response.json()
        dashboard_list = []
        for dashboard in dashboards:
            if dashboard['title'] not in folder:
                dashboard_title = dashboard.get('title', 'N/A')
                dashboard_id = dashboard.get('id', 'N/A')
                dashboard_uid = dashboard.get('uid', 'N/A')

                dashboard_info = {
                    'title': dashboard_title,
                    'id': dashboard_id,
                    'uid': dashboard_uid
                }

                dashboard_list.append(dashboard_info)

        return jsonify(dashboard_list)
    else:
        return jsonify({"type": "error", "message": "Failed to fetch dashboards"})


@app_V2.route("/get_all_panel_details", methods=['GET'])
def get_all_panel_details():
    data = request.get_json()
    dashboard_name = data.get('dashboard_name')

    if not dashboard_name:
        return jsonify({"type": "error", "message": "Invalid or missing 'dashboard_name' in the request"})

    try:
        conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password='User@123', port=5432)
        cur = conn.cursor()
        query = """select dashboard_uid, panel_details from dashboard where dashboard_name='{0}' """.format(
            dashboard_name)
        cur.execute(query)
        result = cur.fetchall()

        if not result:
            return jsonify({"type": "error", "message": f"Dashboard '{dashboard_name}' not found"})

        id = result[0][0]
        panel = result[0][1]
        keys = [key for key, val in panel.items()]

        query = """select count(alert_id) as alert_count, panel_title, panel_id from alerts where dashboard_uid='{0}' group by
        panel_title, panel_id """.format(id)
        cur.execute(query)
        cols = [column[0] for column in cur.description]
        rows = cur.fetchall()
        ll = []

        if len(rows) > 0:
            for eachRow in rows:
                ll.append(dict(zip(cols, eachRow)))

        alert_keys = [i['panel_title'] for i in ll]
        nonalert = list(set(keys) - set(alert_keys))

        for i in nonalert:
            for key, val in panel.items():
                if key == i:
                    data = {"alert_count": 0, "panel_title": key, "panel_id": val}
                    ll.append(data)

        return jsonify({"type": "success", "dashboard_name": dashboard_name, "panel_details": ll})

    except Exception as e:
        return jsonify({"type": "error", "message": f"Error: {str(e)}"})


@app_V2.route('/get_all_datasource', methods=['GET'])
def get_all_datasource():
    base_url = "http://app.autointelli.com:3000/"

    s = requests.Session()
    s.auth = ('admin', 'Wigtra@autointelli1')
    response = s.get(base_url + "api/datasources", verify=False)

    if response.status_code == 200:
        datasources = response.json()
        simplified_datasources = [{"datasource_name": ds["name"], "datasource_uid": ds["uid"], "type": ds["type"]} for
                                  ds in datasources]
        return jsonify(simplified_datasources)
    else:
        error_message = f"Failed to fetch datasources: {response.status_code}"
        return jsonify({"error": error_message}), response.status_code


@app_V2.route('/get_all_folders', methods=['GET'])
def get_all_folders():
    base_url = "http://app.autointelli.com:3000/"

    s = requests.Session()
    s.auth = ('admin', 'Wigtra@autointelli1')
    response = s.get(base_url + "api/folders", verify=False)
    if response.status_code == 200:
        folders = response.json()
        return jsonify(folders)
    else:
        error_message = f"Failed to fetch folders: {response.status_code}"
        return jsonify({"error": error_message}), response.status_code
