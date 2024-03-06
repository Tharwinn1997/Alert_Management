import json
import schedule
import time
import requests
import psycopg2
from datetime import datetime
from flask import Blueprint

# app_V3 = Blueprint('app_v3', __name__)


def dashboard():
    dashboard_name = None
    dashboard_uid = None
    folder_name = None
    folder_uid = None
    datasource = None
    datasource_uid = None
    panel_title = None
    panel_id = None
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"task started on :{formatted_time}")
    base_url = "http://app.autointelli.com:3000/"

    s = requests.Session()
    s.auth = ('admin', 'Wigtra@autointelli1')
    response = s.get(base_url + "api/folders", verify=False)
    folder = []
    if response.status_code == 200:
        folders = response.json()
        for f in folders:
            folder.append(f['title'])
    response = s.get(base_url + "api/search", verify=False)
    if response.status_code == 200:
        dashboards = response.json()
        for db in dashboards:
            if db['title'] not in folder:
                # print(dashboard['title'])
                data = {}
                dashboard_uid = db['uid']
                response = s.get(base_url + f"api/dashboards/uid/{dashboard_uid}", verify=False)

                if response.status_code == 200:
                    conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password='User@123',
                                            port=5432)
                    cur = conn.cursor()
                    dashboard_data = response.json()
                    dashboard_name = dashboard_data['dashboard']['title']
                    query = """delete from dashboard where dashboard_name='{0}'""".format(dashboard_name)
                    cur.execute(query)
                    folder_uid = dashboard_data['meta']['folderUid']
                    folder_name = dashboard_data['meta']['folderTitle']
                    try:
                        datasource = dashboard_data["dashboard"]["templating"]["list"][0]['datasource']['type']
                        datasource_uid = dashboard_data["dashboard"]["templating"]["list"][0]['datasource']['uid']

                    except:
                        try:
                            datasource = dashboard_data["dashboard"]["templating"]["list"][0]['query']
                            name = dashboard_data["dashboard"]["templating"]["list"][0]['current']['text']
                            response = s.get(base_url + f"api/datasources/name/{name}", verify=False)
                            if response.status_code == 200:
                                datasource_uid = response.json()['uid']
                        except:
                            pass
                    try:
                        panels = dashboard_data['dashboard']['panels']
                        for panel in panels:
                            keys = []

                            for key, val in panel.items():
                                keys.append(key)
                            if 'panels' in keys:

                                for key, val in panel.items():
                                    if key == 'panels':

                                        for i in val:

                                            try:
                                                panel_id = i['id']
                                                panel_title = i['title']
                                                if len(panel_title) < 0 or panel_title == " ":
                                                    pass
                                                else:
                                                    data.update({f"{panel_title}": f"{panel_id}"})
                                            except:
                                                pass
                            else:
                                try:

                                    panel_id = panel['id']

                                    panel_title = panel['title']

                                    if len(panel_title) < 0:
                                        pass
                                    else:
                                        data.update({f"{panel_title}": f"{panel_id}"})
                                except:
                                    pass
                    except:
                        pass
                    try:
                        data = json.dumps(data)
                        query = """INSERT INTO  dashboard(dashboard_name,dashboard_uid, folder_name, folder_uid, 
                        datasource,datasource_uid, panel_details) VALUES('{0}', '{1}','{2}','{3}','{4}','{5}',
                        '{6}');""".format(
                            dashboard_name, dashboard_uid, folder_name, folder_uid,
                            datasource,
                            datasource_uid, data)
                        cur.execute(query)
                        conn.commit()
                        print(f"dashboard-{dashboard_name} updated!!! ")
                    except Exception as e:
                        pass



                else:
                    print(f"Error code:{response.status_code} {response.text}")

        else:
            print(f"Error code:{response.status_code} {response.text}")


schedule.every(10).minutes.do(dashboard)

while True:
    schedule.run_pending()
    time.sleep(1)
