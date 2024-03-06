from flask import jsonify, Flask, request, json, Blueprint
import requests, psycopg2

app_d = Blueprint('app_d', __name__)


@app_d.route("/create_alert", methods=['POST'])
def create_alert():
    try:
        data = request.get_json()
        conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password='User@123', port=5432)
        cur = conn.cursor()
        range = data.get('range')

        summary = data.get('summary')
        metric = data.get('metric')
        title = data.get('title')
        dashboard_name = data.get('dashboard_name')

        if metric == "CPU Usage":

            panel_title = "$job\uff1aOverall total 5m load & average CPU used%"

            metric_browser1 = "count(node_cpu_seconds_total{origin_prometheus=~\"\",job=~\"node\", mode='system'})"
            metric_browser2 = "sum(node_load5{origin_prometheus=~\"\",job=~\"node\"})"
            metric_browser3 = ("avg(1 - avg(rate(node_cpu_seconds_total{origin_prometheus=~\"\",job=~\"node\","
                               "mode=\"idle\"}[2m])) by (instance)) * 100")
            legendFormat1 = "CPU Cores"
            legendFormat2 = "Total 5m load"
            legendFormat3 = "Overall average used%"


        elif metric == "Total Memory Usage":

            panel_title = "$job\uff1aOverall total memory & average memory used%"

            metric_browser1 = "sum(node_memory_MemTotal_bytes{origin_prometheus=~\"\",job=~\"node\"})"
            metric_browser2 = ("sum(node_memory_MemTotal_bytes{origin_prometheus=~\"\",job=~\"node\"} - "
                               "node_memory_MemAvailable_bytes{origin_prometheus=~\"\",job=~\"node\"})")
            metric_browser3 = ("(sum(node_memory_MemTotal_bytes{origin_prometheus=~\"\",job=~\"node\"} - "
                               "node_memory_MemAvailable_bytes{origin_prometheus=~\"\",job=~\"node\"}) / sum("
                               "node_memory_MemTotal_bytes{origin_prometheus=~\"\",job=~\"node\"}))*100")
            legendFormat1 = "Total"
            legendFormat2 = "Total Used"
            legendFormat3 = "Overall Average Used%"

        elif metric == "Over All Disk Usage":

            panel_title = "$job\uff1aOverall total disk & average disk used%"

            metric_browser1 = ("sum(avg(node_filesystem_size_bytes{origin_prometheus=~\"\",job=~\"node\","
                               "fstype=~\"xfs|ext.*\"})by(device,instance))")
            metric_browser2 = ("sum(avg(node_filesystem_size_bytes{origin_prometheus=~\"\",job=~\"node\","
                               "fstype=~\"xfs|ext.*\"})by(device,instance)) - sum(avg(node_filesystem_free_bytes{"
                               "origin_prometheus=~\"\",job=~\"node\",fstype=~\"xfs|ext.*\"})by(device,instance))")
            metric_browser3 = ("(sum(avg(node_filesystem_size_bytes{origin_prometheus=~\"\",job=~\"node\","
                               "fstype=~\"xfs|ext.*\"})by(device,instance)) - sum(avg(node_filesystem_free_bytes{"
                               "origin_prometheus=~\"\",job=~\"node\",fstype=~\"xfs|ext.*\"})by(device,instance))) "
                               "*100/("
                               "sum(avg(node_filesystem_avail_bytes{origin_prometheus=~\"\",job=~\"node\","
                               "fstype=~\"xfs|ext.*\"})by(device,instance))+(sum(avg(node_filesystem_size_bytes{"
                               "origin_prometheus=~\"\",job=~\"node\",fstype=~\"xfs|ext.*\"})by(device,instance)) - "
                               "sum("
                               "avg(node_filesystem_free_bytes{origin_prometheus=~\"\",job=~\"node\","
                               "fstype=~\"xfs|ext.*\"})by(device,instance))))")

            legendFormat1 = "Total"
            legendFormat2 = "Total Used"
            legendFormat3 = "Overall Average Used%"
        else:
            return jsonify({"message": f"Unsupported metric: {metric}"})

        base_url = "http://app.autointelli.com:3000/"
        username = "admin"
        password = "Wigtra@autointelli1"
        headers = {
            'Content-Type': 'application/json',
            'X-Disable-Provenance': "true"
        }

        response = requests.get(base_url + "api/v1/provisioning/contact-points", auth=(username, password),
                                headers=headers)
        contacts = response.json()
        cuid = None
        for d in contacts:
            if d['name'] == data['contact']:
                cuid = d['uid']
        if cuid == None:
            return ({"message": "Contact not found", "type": "error"})

        conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password='User@123', port=5432)
        cur = conn.cursor()

        query = """SELECT labels FROM contactpoints WHERE name = %s"""
        cur.execute(query, (data['contact'],))
        labels_result = cur.fetchone()

        if not labels_result:
            return jsonify({"message": "Labels not found", "type": "error"})

        labels = labels_result[0]

        query = """select * from dashboard where dashboard_name='{0}' """.format(dashboard_name)
        conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password='User@123', port=5432)
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        if rows == []:
            return jsonify({"message": "dashboard not found", "type": "error"})
        ll = []
        cols = [column[0] for column in cur.description]
        if len(rows) > 0:
            for eachRow in rows:
                ll.append(dict(zip(cols, eachRow)))
            data = ll[0]['panel_details']
            for key, val in data.items():
                if key == panel_title:
                    panel_id = val
            dashboard_uid = ll[0]['dashboard_uid']
            folder_uid = ll[0]['folder_uid']
            datasource_uid = ll[0]['datasource_uid']

            alert_payload = {
                "annotations": {
                    "__dashboardUid__": dashboard_uid,
                    "__panelId__": panel_id,
                    "summary": summary
                },
                "condition": "D",
                "data": [
                    {
                        "datasourceUid": datasource_uid,
                        "model": {
                            "datasource": {
                                "type": "prometheus",
                                "uid": datasource_uid
                            },
                            "expr": metric_browser1,
                            "format": "time_series",
                            "instant": False,
                            "interval": "30m",
                            "intervalFactor": 1,
                            "intervalMs": 15000,
                            "legendFormat": legendFormat1,
                            "maxDataPoints": 43200,
                            "refId": "A",
                            "step": 4
                        },
                        "queryType": "",
                        "refId": "A",
                        "relativeTimeRange": {
                            "from": 43200,
                            "to": 0
                        }
                    },
                    {
                        "datasourceUid": datasource_uid,
                        "model": {
                            "datasource": {
                                "type": "prometheus",
                                "uid": datasource_uid
                            },
                            "expr": metric_browser2,
                            "format": "time_series",
                            "interval": "30m",
                            "intervalFactor": 1,
                            "intervalMs": 15000,
                            "legendFormat": legendFormat2,
                            "maxDataPoints": 43200,
                            "refId": "B",
                            "step": 4
                        },
                        "queryType": "",
                        "refId": "B",
                        "relativeTimeRange": {
                            "from": 43200,
                            "to": 0
                        }
                    },
                    {
                        "datasourceUid": datasource_uid,
                        "model": {
                            "datasource": {
                                "type": "prometheus",
                                "uid": datasource_uid
                            },
                            "expr": metric_browser3,
                            "format": "time_series",
                            "interval": "30m",
                            "intervalFactor": 1,
                            "intervalMs": 15000,
                            "legendFormat": legendFormat3,
                            "maxDataPoints": 43200,
                            "refId": "H"
                        },
                        "queryType": "",
                        "refId": "H",
                        "relativeTimeRange": {
                            "from": 43200,
                            "to": 0
                        }
                    },
                    {
                        "datasourceUid": "__expr__",
                        "model": {
                            "conditions": [
                                {
                                    "evaluator": {
                                        "params": [],
                                        "type": "gt"
                                    },
                                    "operator": {
                                        "type": "and"
                                    },
                                    "query": {
                                        "params": [
                                            "C"
                                        ]
                                    },
                                    "reducer": {
                                        "params": [],
                                        "type": "last"
                                    },
                                    "type": "query"
                                }
                            ],
                            "datasource": {
                                "type": "__expr__",
                                "uid": "__expr__"
                            },
                            "expression": "A",
                            "intervalMs": 1000,
                            "maxDataPoints": 43200,
                            "reducer": "last",
                            "refId": "C",
                            "type": "reduce"
                        },
                        "queryType": "",
                        "refId": "C",
                        "relativeTimeRange": {
                            "from": 600,
                            "to": 0
                        }
                    },
                    {
                        "datasourceUid": "__expr__",
                        "model": {
                            "conditions": [
                                {
                                    "evaluator": {
                                        "params": [
                                            range
                                        ],
                                        "type": "gt"
                                    },
                                    "operator": {
                                        "type": "and"
                                    },
                                    "query": {
                                        "params": [
                                            "D"
                                        ]
                                    },
                                    "reducer": {
                                        "params": [],
                                        "type": "last"
                                    },
                                    "type": "query"
                                }
                            ],
                            "datasource": {
                                "type": "__expr__",
                                "uid": "__expr__"
                            },
                            "expression": "C",
                            "intervalMs": 1000,
                            "maxDataPoints": 43200,
                            "refId": "D",
                            "type": "threshold"
                        },
                        "queryType": "",
                        "refId": "D",
                        "relativeTimeRange": {
                            "from": 600,
                            "to": 0
                        }
                    }
                ],
                "execErrState": "Error",
                "folderUID": folder_uid,
                "for": "5m",
                "isPaused": False,
                "labels": {
                    f"{labels[0]}": f"{labels[2]}"
                },
                "notifications": [
                    {
                        "uid": f"channel-{cuid}"
                    }
                ],
                "noDataState": "NoData",
                "orgID": 1,
                "ruleGroup": panel_title,
                "title": title
            }

            base_url = "http://app.autointelli.com:3000/"
            username = "admin"
            password = "Wigtra@autointelli1"
            headers = {
                'Content-Type': 'application/json',
                'X-Disable-Provenance': "true"
            }

            try:
                response = requests.post(base_url + "api/v1/provisioning/alert-rules", auth=(username, password),
                                         headers=headers, data=json.dumps(alert_payload))

                query = """SELECT * FROM alerts WHERE alert_title='{0}'""".format(title)
                cur.execute(query)
                existing_alert = cur.fetchone()

                if existing_alert:
                    return jsonify({"type": "error", "message": "Alert with the same title already exists"})
                if response.status_code == 201:
                    data = response.json()
                    try:

                        conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                                                password='User@123',
                                                port=5432)
                        cur = conn.cursor()
                        query = """INSERT INTO alerts(alert_title, alert_uid, dashboard_uid, panel_id, summary,
                        range, panel_title,dashboard_name,metric) VALUES('{0}', '{1}', '{2}','{3}','{4}','{5}','{6}','{7}','{8}');""".format(
                            title, data['uid'], dashboard_uid, panel_id, summary, range, panel_title, dashboard_name,
                            metric)
                        cur.execute(query)
                        conn.commit()
                        return jsonify({"result": "Success", "message": "Alert created successfully!!"})

                    except Exception as e:
                        response = requests.delete(base_url + f"api/v1/provisioning/alert-rules/{data['uid']}",
                                                   auth=(username, password),
                                                   headers=headers)
                        return jsonify({"type": "error", "message": f"Database insertion error: {str(e)}"})

            except requests.exceptions.RequestException as e:
                return jsonify({"type": "error", "message": f"Error making external API request: {str(e)}"})

    except Exception as e:
        return jsonify({"type": "error", "message": f"Error: {str(e)}"})


@app_d.route("/update_alert", methods=['PUT'])
def update_alert():
    try:
        data = request.get_json()
        alert_id = request.args.get('id')

        if not alert_id:
            return {"message": "Alert ID is missing"}, 400

        conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password='User@123', port=5432)
        cur = conn.cursor()
        query = "SELECT * FROM alerts WHERE alert_id = {0}".format(alert_id)
        cur.execute(query)
        existing_alert = cur.fetchone()
        alert_uid = existing_alert[2]
        dashboard_uid = existing_alert[3]
        panel_title = existing_alert[7]
        if not existing_alert:
            return jsonify({"type": "error", "message": "Alert ID not found"}), 404

        conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password='User@123', port=5432)
        cur = conn.cursor()
        range = data.get('range')
        summary = data.get('summary')
        title = data.get('title')

        if panel_title == "$job\uff1aOverall total 5m load & average CPU used%":

            metric_browser1 = "count(node_cpu_seconds_total{origin_prometheus=~\"\",job=~\"node\", mode='system'})"
            metric_browser2 = "sum(node_load5{origin_prometheus=~\"\",job=~\"node\"})"
            metric_browser3 = ("avg(1 - avg(rate(node_cpu_seconds_total{origin_prometheus=~\"\",job=~\"node\","
                               "mode=\"idle\"}[2m])) by (instance)) * 100")
            legendFormat1 = "CPU Cores"
            legendFormat2 = "Total 5m load"
            legendFormat3 = "Overall average used%"


        elif panel_title == "$job\uff1aOverall total memory & average memory used%":

            metric_browser1 = "sum(node_memory_MemTotal_bytes{origin_prometheus=~\"\",job=~\"node\"})"
            metric_browser2 = ("sum(node_memory_MemTotal_bytes{origin_prometheus=~\"\",job=~\"node\"} - "
                               "node_memory_MemAvailable_bytes{origin_prometheus=~\"\",job=~\"node\"})")
            metric_browser3 = ("(sum(node_memory_MemTotal_bytes{origin_prometheus=~\"\",job=~\"node\"} - "
                               "node_memory_MemAvailable_bytes{origin_prometheus=~\"\",job=~\"node\"}) / sum("
                               "node_memory_MemTotal_bytes{origin_prometheus=~\"\",job=~\"node\"}))*100")
            legendFormat1 = "Total"
            legendFormat2 = "Total Used"
            legendFormat3 = "Overall Average Used%"

        elif panel_title == "$job\uff1aOverall total disk & average disk used%":

            metric_browser1 = ("sum(avg(node_filesystem_size_bytes{origin_prometheus=~\"\",job=~\"node\","
                               "fstype=~\"xfs|ext.*\"})by(device,instance))")
            metric_browser2 = ("sum(avg(node_filesystem_size_bytes{origin_prometheus=~\"\",job=~\"node\","
                               "fstype=~\"xfs|ext.*\"})by(device,instance)) - sum(avg(node_filesystem_free_bytes{"
                               "origin_prometheus=~\"\",job=~\"node\",fstype=~\"xfs|ext.*\"})by(device,instance))")
            metric_browser3 = ("(sum(avg(node_filesystem_size_bytes{origin_prometheus=~\"\",job=~\"node\","
                               "fstype=~\"xfs|ext.*\"})by(device,instance)) - sum(avg(node_filesystem_free_bytes{"
                               "origin_prometheus=~\"\",job=~\"node\",fstype=~\"xfs|ext.*\"})by(device,instance))) "
                               "*100/("
                               "sum(avg(node_filesystem_avail_bytes{origin_prometheus=~\"\",job=~\"node\","
                               "fstype=~\"xfs|ext.*\"})by(device,instance))+(sum(avg(node_filesystem_size_bytes{"
                               "origin_prometheus=~\"\",job=~\"node\",fstype=~\"xfs|ext.*\"})by(device,instance)) - "
                               "sum("
                               "avg(node_filesystem_free_bytes{origin_prometheus=~\"\",job=~\"node\","
                               "fstype=~\"xfs|ext.*\"})by(device,instance))))")

            legendFormat1 = "Total"
            legendFormat2 = "Total Used"
            legendFormat3 = "Overall Average Used%"

        else:
            return jsonify({"message": f"Unsupported panel_title: {panel_title}"})

        base_url = "http://app.autointelli.com:3000/"
        username = "admin"
        password = "Wigtra@autointelli1"
        headers = {
            'Content-Type': 'application/json',
            'X-Disable-Provenance': "true"
        }

        response = requests.get(base_url + "api/v1/provisioning/contact-points", auth=(username, password),
                                headers=headers)
        contacts = response.json()
        cuid = None
        for d in contacts:
            if d['name'] == data['contact']:
                cuid = d['uid']
        if cuid == None:
            return ({"message": "Contact not found", "type": "error"})

        conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password='User@123', port=5432)
        cur = conn.cursor()

        query = """SELECT labels FROM contactpoints WHERE name = %s"""
        cur.execute(query, (data['contact'],))
        labels_result = cur.fetchone()

        if not labels_result:
            return jsonify({"message": "Labels not found", "type": "error"})

        labels = labels_result[0]

        query = """select * from dashboard where dashboard_uid='{0}' """.format(dashboard_uid)
        conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password='User@123', port=5432)
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        ll = []
        cols = [column[0] for column in cur.description]
        if len(rows) > 0:
            for eachRow in rows:
                ll.append(dict(zip(cols, eachRow)))
            data = ll[0]['panel_details']
            for key, val in data.items():
                if key == panel_title:
                    panel_id = val
            folder_uid = ll[0]['folder_uid']
            datasource_uid = ll[0]['datasource_uid']

            alert_payload = {
                "annotations": {
                    "__dashboardUid__": dashboard_uid,
                    "__panelId__": f"{panel_id}",
                    "summary": summary
                },
                "condition": "D",
                "data": [
                    {
                        "datasourceUid": f"{datasource_uid}",
                        "model": {
                            "datasource": {
                                "type": "prometheus",
                                "uid": f"{datasource_uid}"
                            },
                            "expr": metric_browser1,
                            "format": "time_series",
                            "instant": False,
                            "interval": "30m",
                            "intervalFactor": 1,
                            "intervalMs": 15000,
                            "legendFormat": legendFormat1,
                            "maxDataPoints": 43200,
                            "refId": "A",
                            "step": 4
                        },
                        "queryType": "",
                        "refId": "A",
                        "relativeTimeRange": {
                            "from": 43200,
                            "to": 0
                        }
                    },
                    {
                        "datasourceUid": f"{datasource_uid}",
                        "model": {
                            "datasource": {
                                "type": "prometheus",
                                "uid": f"{datasource_uid}"
                            },
                            "expr": metric_browser2,
                            "format": "time_series",
                            "interval": "30m",
                            "intervalFactor": 1,
                            "intervalMs": 15000,
                            "legendFormat": legendFormat2,
                            "maxDataPoints": 43200,
                            "refId": "B",
                            "step": 4
                        },
                        "queryType": "",
                        "refId": "B",
                        "relativeTimeRange": {
                            "from": 43200,
                            "to": 0
                        }
                    },
                    {
                        "datasourceUid": f"{datasource_uid}",
                        "model": {
                            "datasource": {
                                "type": "prometheus",
                                "uid": f"{datasource_uid}"
                            },
                            "expr": metric_browser3,
                            "format": "time_series",
                            "interval": "30m",
                            "intervalFactor": 1,
                            "intervalMs": 15000,
                            "legendFormat": legendFormat3,
                            "maxDataPoints": 43200,
                            "refId": "H"
                        },
                        "queryType": "",
                        "refId": "H",
                        "relativeTimeRange": {
                            "from": 43200,
                            "to": 0
                        }
                    },
                    {
                        "datasourceUid": "__expr__",
                        "model": {
                            "conditions": [
                                {
                                    "evaluator": {
                                        "params": [],
                                        "type": "gt"
                                    },
                                    "operator": {
                                        "type": "and"
                                    },
                                    "query": {
                                        "params": [
                                            "C"
                                        ]
                                    },
                                    "reducer": {
                                        "params": [],
                                        "type": "last"
                                    },
                                    "type": "query"
                                }
                            ],
                            "datasource": {
                                "type": "__expr__",
                                "uid": "__expr__"
                            },
                            "expression": "A",
                            "intervalMs": 1000,
                            "maxDataPoints": 43200,
                            "reducer": "last",
                            "refId": "C",
                            "type": "reduce"
                        },
                        "queryType": "",
                        "refId": "C",
                        "relativeTimeRange": {
                            "from": 600,
                            "to": 0
                        }
                    },
                    {
                        "datasourceUid": "__expr__",
                        "model": {
                            "conditions": [
                                {
                                    "evaluator": {
                                        "params": [
                                            range
                                        ],
                                        "type": "gt"
                                    },
                                    "operator": {
                                        "type": "and"
                                    },
                                    "query": {
                                        "params": [
                                            "D"
                                        ]
                                    },
                                    "reducer": {
                                        "params": [],
                                        "type": "last"
                                    },
                                    "type": "query"
                                }
                            ],
                            "datasource": {
                                "type": "__expr__",
                                "uid": "__expr__"
                            },
                            "expression": "C",
                            "intervalMs": 1000,
                            "maxDataPoints": 43200,
                            "refId": "D",
                            "type": "threshold"
                        },
                        "queryType": "",
                        "refId": "D",
                        "relativeTimeRange": {
                            "from": 600,
                            "to": 0
                        }
                    }
                ],
                "execErrState": "Error",
                "folderUID": f"{folder_uid}",
                "for": "5m",
                "isPaused": False,
                "labels": {
                    f"{labels[0]}": f"{labels[2]}"
                },
                "notifications": [
                    {
                        "uid": f"channel-{cuid}"
                    }
                ],
                "noDataState": "NoData",
                "orgID": 1,
                "ruleGroup": panel_title,
                "title": title

            }

            base_url = "http://app.autointelli.com:3000/"
            username = "admin"
            password = "Wigtra@autointelli1"
            headers = {
                'Content-Type': 'application/json',
                'X-Disable-Provenance': "true"
            }

            try:
                response = requests.put(base_url + f"api/v1/provisioning/alert-rules/{alert_uid}",
                                        auth=(username, password),
                                        headers=headers, data=json.dumps(alert_payload))
                if response.status_code == 200:
                    data = response.json()
                    try:
                        query = "UPDATE alerts SET alert_title = %s, summary = %s, range = %s WHERE alert_id = %s"
                        cur.execute(query, (title, summary, range, alert_id))
                        conn.commit()
                        return jsonify({"result": "Success", "message": "Alert updated successfully!!"})

                    except Exception as e:
                        return jsonify({"type": "error", "message": f"Database update error: {str(e)}"})
                else:
                    return jsonify({"type": "error", "message": response.json()['message']})


            except Exception as e:
                return jsonify({"type": "error", "message": f"Error making external API request: {str(e)}"})

    except Exception as e:
        return jsonify({"type": "error", "message": f"Error: {str(e)}"})


@app_d.route("/updown_create", methods=['POST'])
def updown_create():
    try:
        data = request.get_json()
        conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password='User@123', port=5432)
        cur = conn.cursor()
        range = data.get('range')

        summary = data.get('summary')
        metric = data.get('metric')
        title = data.get('title')
        dashboard_name = data.get('dashboard_name')

        if metric == "Internet":
            legendFormat1 = "{{device}}_receive"
            legendFormat2 = "{{device}}_transmit"
            panel_title = "Internet traffic per hour $device"

        else:
            return jsonify({"message": f"Unsupported metric: {metric}"})

        base_url = "http://app.autointelli.com:3000/"
        username = "admin"
        password = "Wigtra@autointelli1"
        headers = {
            'Content-Type': 'application/json',
            'X-Disable-Provenance': "true"
        }

        response = requests.get(base_url + "api/v1/provisioning/contact-points", auth=(username, password),
                                headers=headers)
        contacts = response.json()
        cuid = None
        for d in contacts:
            if d['name'] == data['contact']:
                cuid = d['uid']
        if cuid == None:
            return ({"message": "Contact not found", "type": "error"})

        conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password='User@123', port=5432)
        cur = conn.cursor()

        query = """SELECT labels FROM contactpoints WHERE name = %s"""
        cur.execute(query, (data['contact'],))
        labels_result = cur.fetchone()

        if not labels_result:
            return jsonify({"message": "Labels not found", "type": "error"})

        labels = labels_result[0]

        query = """select * from dashboard where dashboard_name='{0}' """.format(dashboard_name)
        conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password='USer@123', port=5432)
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        if rows == []:
            return jsonify({"message": "dashboard not found", "type": "error"})
        ll = []
        cols = [column[0] for column in cur.description]
        if len(rows) > 0:
            for eachRow in rows:
                ll.append(dict(zip(cols, eachRow)))
            data = ll[0]['panel_details']
            for key, val in data.items():
                if key == panel_title:
                    panel_id = val
            dashboard_uid = ll[0]['dashboard_uid']
            folder_uid = ll[0]['folder_uid']
            datasource_uid = ll[0]['datasource_uid']

            alert_payload = {
                "annotations": {
                    "__dashboardUid__": dashboard_uid,
                    "__panelId__": f"{panel_id}",
                    "summary": summary
                },
                "condition": "D",
                "data": [
                    {
                        "datasourceUid": f"{datasource_uid}",
                        "model": {
                            "datasource": {
                                "type": "prometheus",
                                "uid": f"{datasource_uid}"
                            },
                            "expr": "increase(node_network_receive_bytes_total{instance=~\"localhost:9100\","
                                    "device=~\"eth0\"}[60m])",
                            "interval": "60m",
                            "intervalFactor": 1,
                            "intervalMs": 15000,
                            "legendFormat": legendFormat1,
                            "maxDataPoints": 43200,
                            "metric": "",
                            "refId": "A",
                            "step": 600,
                            "target": ""
                        },
                        "queryType": "",
                        "refId": "A",
                        "relativeTimeRange": {
                            "from": 43200,
                            "to": 0
                        }
                    },
                    {
                        "datasourceUid": f"{datasource_uid}",
                        "model": {
                            "datasource": {
                                "type": "prometheus",
                                "uid": f"{datasource_uid}"
                            },
                            "expr": "increase(node_network_transmit_bytes_total{instance=~\"localhost:9100\","
                                    "device=~\"eth0\"}[60m])",
                            "interval": "60m",
                            "intervalFactor": 1,
                            "intervalMs": 15000,
                            "legendFormat": legendFormat2,
                            "maxDataPoints": 43200,
                            "refId": "B",
                            "step": 600
                        },
                        "queryType": "",
                        "refId": "B",
                        "relativeTimeRange": {
                            "from": 43200,
                            "to": 0
                        }
                    },
                    {
                        "datasourceUid": "__expr__",
                        "model": {
                            "conditions": [
                                {
                                    "evaluator": {
                                        "params": [],
                                        "type": "gt"
                                    },
                                    "operator": {
                                        "type": "and"
                                    },
                                    "query": {
                                        "params": [
                                            "C"
                                        ]
                                    },
                                    "reducer": {
                                        "params": [],
                                        "type": "last"
                                    },
                                    "type": "query"
                                }
                            ],
                            "datasource": {
                                "type": "__expr__",
                                "uid": "__expr__"
                            },
                            "expression": "A",
                            "intervalMs": 1000,
                            "maxDataPoints": 43200,
                            "reducer": "last",
                            "refId": "C",
                            "type": "reduce"
                        },
                        "queryType": "",
                        "refId": "C",
                        "relativeTimeRange": {
                            "from": 600,
                            "to": 0
                        }
                    },
                    {
                        "datasourceUid": "__expr__",
                        "model": {
                            "conditions": [
                                {
                                    "evaluator": {
                                        "params": [
                                            range
                                        ],
                                        "type": "gt"
                                    },
                                    "operator": {
                                        "type": "and"
                                    },
                                    "query": {
                                        "params": [
                                            "D"
                                        ]
                                    },
                                    "reducer": {
                                        "params": [],
                                        "type": "last"
                                    },
                                    "type": "query"
                                }
                            ],
                            "datasource": {
                                "type": "__expr__",
                                "uid": "__expr__"
                            },
                            "expression": "C",
                            "intervalMs": 1000,
                            "maxDataPoints": 43200,
                            "refId": "D",
                            "type": "threshold"
                        },
                        "queryType": "",
                        "refId": "D",
                        "relativeTimeRange": {
                            "from": 600,
                            "to": 0
                        }
                    }
                ],
                "execErrState": "Error",
                "folderUID": f"{folder_uid}",
                "for": "5m",
                "isPaused": False,
                "labels": {
                    f"{labels[0]}": f"{labels[2]}"
                },
                "notifications": [
                    {
                        "uid": f"channel-{cuid}"
                    }
                ],
                "noDataState": "NoData",
                "orgID": 1,
                "ruleGroup": panel_title,
                "title": title
            }

            base_url = "http://app.autointelli.com:3000/"
            username = "admin"
            password = "Wigtra@autointelli1"
            headers = {
                'Content-Type': 'application/json',
                'X-Disable-Provenance': "true"
            }

            try:
                response = requests.post(base_url + "api/v1/provisioning/alert-rules", auth=(username, password),
                                         headers=headers, data=json.dumps(alert_payload))

                query = """SELECT * FROM alerts WHERE alert_title='{0}'""".format(title)
                cur.execute(query)
                existing_alert = cur.fetchone()

                if existing_alert:
                    return jsonify({"type": "error", "message": "Alert with the same title already exists"})
                if response.status_code == 201:
                    data = response.json()
                    try:

                        conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                                                password='User@123',
                                                port=5432)
                        cur = conn.cursor()
                        query = """INSERT INTO alerts(alert_title, alert_uid, dashboard_uid, panel_id, summary,
                                        range, panel_title,dashboard_name,metric) VALUES('{0}', '{1}', '{2}','{3}','{4}','{5}','{6}','{7}','{8}');""".format(
                            title, data['uid'], dashboard_uid, panel_id, summary, range, panel_title, dashboard_name,
                            metric)
                        cur.execute(query)
                        conn.commit()
                        return jsonify({"result": "Success", "message": "Alert created successfully!!"})

                    except Exception as e:
                        response = requests.delete(base_url + f"api/v1/provisioning/alert-rules/{data['uid']}",
                                                   auth=(username, password),
                                                   headers=headers)
                        return jsonify({"type": "error", "message": f"Database insertion error: {str(e)}"})

            except requests.exceptions.RequestException as e:
                return jsonify({"type": "error", "message": f"Error making external API request: {str(e)}"})

    except Exception as e:
        return jsonify({"type": "error", "message": f"Error: {str(e)}"})


@app_d.route("/updown_update", methods=['PUT'])
def updown_update():
    try:
        data = request.get_json()
        alert_id = request.args.get('id')

        if not alert_id:
            return {"message": "Alert ID is missing"}, 400

        conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password='User@123', port=5432)
        cur = conn.cursor()
        query = "SELECT * FROM alerts WHERE alert_id = {0}".format(alert_id)
        cur.execute(query)
        existing_alert = cur.fetchone()
        alert_uid = existing_alert[2]
        dashboard_uid = existing_alert[3]
        panel_title = existing_alert[7]
        if not existing_alert:
            return jsonify({"type": "error", "message": "Alert ID not found"}), 404

        conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password='User@123', port=5432)
        cur = conn.cursor()
        range = data.get('range')
        summary = data.get('summary')
        title = data.get('title')

        if panel_title == "Internet traffic per hour $device":
            legendFormat1 = "{{device}}_receive"
            legendFormat2 = "{{device}}_transmit"


        else:
            return jsonify({"message": f"Unsupported panel_title: {panel_title}"})

        base_url = "http://app.autointelli.com:3000/"
        username = "admin"
        password = "Wigtra@autointelli1"
        headers = {
            'Content-Type': 'application/json',
            'X-Disable-Provenance': "true"
        }

        response = requests.get(base_url + "api/v1/provisioning/contact-points", auth=(username, password),
                                headers=headers)
        contacts = response.json()
        cuid = None
        for d in contacts:
            if d['name'] == data['contact']:
                cuid = d['uid']
        if cuid == None:
            return ({"message": "Contact not found", "type": "error"})

        conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password='User@123', port=5432)
        cur = conn.cursor()

        query = """SELECT labels FROM contactpoints WHERE name = %s"""
        cur.execute(query, (data['contact'],))
        labels_result = cur.fetchone()

        if not labels_result:
            return jsonify({"message": "Labels not found", "type": "error"})

        labels = labels_result[0]

        query = """select * from dashboard where dashboard_uid='{0}' """.format(dashboard_uid)
        conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password='User@123', port=5432)
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        ll = []
        cols = [column[0] for column in cur.description]
        if len(rows) > 0:
            for eachRow in rows:
                ll.append(dict(zip(cols, eachRow)))
            data = ll[0]['panel_details']
            for key, val in data.items():
                if key == panel_title:
                    panel_id = val
            folder_uid = ll[0]['folder_uid']
            datasource_uid = ll[0]['datasource_uid']

            alert_payload = {
                "annotations": {
                    "__dashboardUid__": dashboard_uid,
                    "__panelId__": f"{panel_id}",
                    "summary": summary
                },
                "condition": "D",
                "data": [
                    {
                        "datasourceUid": f"{datasource_uid}",
                        "model": {
                            "datasource": {
                                "type": "prometheus",
                                "uid": f"{datasource_uid}"
                            },
                            "expr": "increase(node_network_receive_bytes_total{instance=~\"localhost:9100\","
                                    "device=~\"eth0\"}[60m])",
                            "interval": "60m",
                            "intervalFactor": 1,
                            "intervalMs": 15000,
                            "legendFormat": legendFormat1,
                            "maxDataPoints": 43200,
                            "metric": "",
                            "refId": "A",
                            "step": 600,
                            "target": ""
                        },
                        "queryType": "",
                        "refId": "A",
                        "relativeTimeRange": {
                            "from": 43200,
                            "to": 0
                        }
                    },
                    {
                        "datasourceUid": f"{datasource_uid}",
                        "model": {
                            "datasource": {
                                "type": "prometheus",
                                "uid": f"{datasource_uid}"
                            },
                            "expr": "increase(node_network_transmit_bytes_total{instance=~\"localhost:9100\","
                                    "device=~\"eth0\"}[60m])",
                            "interval": "60m",
                            "intervalFactor": 1,
                            "intervalMs": 15000,
                            "legendFormat": legendFormat2,
                            "maxDataPoints": 43200,
                            "refId": "B",
                            "step": 600
                        },
                        "queryType": "",
                        "refId": "B",
                        "relativeTimeRange": {
                            "from": 43200,
                            "to": 0
                        }
                    },
                    {
                        "datasourceUid": "__expr__",
                        "model": {
                            "conditions": [
                                {
                                    "evaluator": {
                                        "params": [],
                                        "type": "gt"
                                    },
                                    "operator": {
                                        "type": "and"
                                    },
                                    "query": {
                                        "params": [
                                            "C"
                                        ]
                                    },
                                    "reducer": {
                                        "params": [],
                                        "type": "last"
                                    },
                                    "type": "query"
                                }
                            ],
                            "datasource": {
                                "type": "__expr__",
                                "uid": "__expr__"
                            },
                            "expression": "A",
                            "intervalMs": 1000,
                            "maxDataPoints": 43200,
                            "reducer": "last",
                            "refId": "C",
                            "type": "reduce"
                        },
                        "queryType": "",
                        "refId": "C",
                        "relativeTimeRange": {
                            "from": 600,
                            "to": 0
                        }
                    },
                    {
                        "datasourceUid": "__expr__",
                        "model": {
                            "conditions": [
                                {
                                    "evaluator": {
                                        "params": [
                                            range
                                        ],
                                        "type": "gt"
                                    },
                                    "operator": {
                                        "type": "and"
                                    },
                                    "query": {
                                        "params": [
                                            "D"
                                        ]
                                    },
                                    "reducer": {
                                        "params": [],
                                        "type": "last"
                                    },
                                    "type": "query"
                                }
                            ],
                            "datasource": {
                                "type": "__expr__",
                                "uid": "__expr__"
                            },
                            "expression": "C",
                            "intervalMs": 1000,
                            "maxDataPoints": 43200,
                            "refId": "D",
                            "type": "threshold"
                        },
                        "queryType": "",
                        "refId": "D",
                        "relativeTimeRange": {
                            "from": 600,
                            "to": 0
                        }
                    }
                ],
                "execErrState": "Error",
                "folderUID": f"{folder_uid}",
                "for": "5m",
                "isPaused": False,
                "labels": {
                    f"{labels[0]}": f"{labels[2]}"
                },
                "notifications": [
                    {
                        "uid": f"channel-{cuid}"
                    }
                ],
                "noDataState": "NoData",
                "orgID": 1,
                "ruleGroup": panel_title,
                "title": title
            }

            base_url = "http://app.autointelli.com:3000/"
            username = "admin"
            password = "Wigtra@autointelli1"
            headers = {
                'Content-Type': 'application/json',
                'X-Disable-Provenance': "true"
            }

            try:
                response = requests.put(base_url + f"api/v1/provisioning/alert-rules/{alert_uid}",
                                        auth=(username, password),
                                        headers=headers, data=json.dumps(alert_payload))
                if response.status_code == 200:
                    data = response.json()
                    try:
                        query = "UPDATE alerts SET alert_title = %s, summary = %s, range = %s WHERE alert_id = %s"
                        cur.execute(query, (title, summary, range, alert_id))
                        conn.commit()
                        return jsonify({"result": "Success", "message": "Alert updated successfully!!"})

                    except Exception as e:
                        return jsonify({"type": "error", "message": f"Database update error: {str(e)}"})
                else:
                    return jsonify({"type": "error", "message": response.json()['message']})


            except Exception as e:
                return jsonify({"type": "error", "message": f"Error making external API request: {str(e)}"})

    except Exception as e:
        return jsonify({"type": "error", "message": f"Error: {str(e)}"})
