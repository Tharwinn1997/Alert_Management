from flask import Flask, request, jsonify, json, Blueprint
import requests, psycopg2

app_b = Blueprint('app_b', __name__)

@app_b.route("/create_alert", methods=['POST'])
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

        if metric == "CPU_Load":
            measurement = "ciscoCPU"
            panel_title = "CPU Load"
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

        conn = psycopg2.connect(host="localhost", dbname="Alert_Rules", user="postgres", password='1234', port=5432)
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
                    "__panelId__": f"{panel_id}",
                    "summary": summary
                },
                "condition": "E",
                "data": [
                    {
                        "datasourceUid": f"{datasource_uid}",
                        "model": {
                            "adhocFilters": [],
                            "alias": "5sec",
                            "datasource": {
                                "type": "influxdb",
                                "uid": f"{datasource_uid}"
                            },
                            "groupBy": [
                                {
                                    "params": [
                                        "$__interval"
                                    ],
                                    "type": "time"
                                },
                                {
                                    "params": [
                                        "none"
                                    ],
                                    "type": "fill"
                                }
                            ],
                            "intervalMs": 1000,
                            "limit": "",
                            "maxDataPoints": 43200,
                            "measurement": measurement,
                            "orderByTime": "ASC",
                            "policy": "default",
                            "query": "",
                            "refId": "A",
                            "resultFormat": "time_series",
                            "select": [
                                [
                                    {
                                        "params": [
                                            "cpmCPUTotal5secRev"
                                        ],
                                        "type": "field"
                                    },
                                    {
                                        "params": [],
                                        "type": "mean"
                                    }
                                ]
                            ],
                            "slimit": "",
                            "tags": [
                                {
                                    "key": "sysName",
                                    "operator": "=~",
                                    "value": "/^ACE-INTERNET-RTR\\.acedesigners\\.co\\.in$/"
                                }
                            ],
                            "tz": ""
                        },
                        "queryType": "",
                        "refId": "A",
                        "relativeTimeRange": {
                            "from": 10800,
                            "to": 0
                        }
                    },
                    {
                        "datasourceUid": f"{datasource_uid}",
                        "model": {
                            "adhocFilters": [],
                            "alias": "1min",
                            "datasource": {
                                "type": "influxdb",
                                "uid": f"{datasource_uid}"
                            },
                            "groupBy": [
                                {
                                    "params": [
                                        "$__interval"
                                    ],
                                    "type": "time"
                                },
                                {
                                    "params": [
                                        "none"
                                    ],
                                    "type": "fill"
                                }
                            ],
                            "intervalMs": 1000,
                            "limit": "",
                            "maxDataPoints": 43200,
                            "measurement": measurement,
                            "orderByTime": "ASC",
                            "policy": "default",
                            "query": "",
                            "refId": "B",
                            "resultFormat": "time_series",
                            "select": [
                                [
                                    {
                                        "params": [
                                            "cpmCPUTotal1minRev"
                                        ],
                                        "type": "field"
                                    },
                                    {
                                        "params": [],
                                        "type": "mean"
                                    }
                                ]
                            ],
                            "slimit": "",
                            "tags": [
                                {
                                    "key": "sysName",
                                    "operator": "=~",
                                    "value": "/^ACE-INTERNET-RTR\\.acedesigners\\.co\\.in$/"
                                }
                            ],
                            "tz": ""
                        },
                        "queryType": "",
                        "refId": "B",
                        "relativeTimeRange": {
                            "from": 10800,
                            "to": 0
                        }
                    },
                    {
                        "datasourceUid": f"{datasource_uid}",
                        "model": {
                            "adhocFilters": [],
                            "alias": "5min",
                            "datasource": {
                                "type": "influxdb",
                                "uid": f"{datasource_uid}"
                            },
                            "groupBy": [
                                {
                                    "params": [
                                        "$__interval"
                                    ],
                                    "type": "time"
                                },
                                {
                                    "params": [
                                        "none"
                                    ],
                                    "type": "fill"
                                }
                            ],
                            "intervalMs": 1000,
                            "limit": "",
                            "maxDataPoints": 43200,
                            "measurement": measurement,
                            "orderByTime": "ASC",
                            "policy": "default",
                            "query": "",
                            "refId": "C",
                            "resultFormat": "time_series",
                            "select": [
                                [
                                    {
                                        "params": [
                                            "cpmCPUTotal5minRev"
                                        ],
                                        "type": "field"
                                    },
                                    {
                                        "params": [],
                                        "type": "mean"
                                    }
                                ]
                            ],
                            "slimit": "",
                            "tags": [
                                {
                                    "key": "sysName",
                                    "operator": "=",
                                    "value": "cx.home"
                                }
                            ],
                            "tz": ""
                        },
                        "queryType": "",
                        "refId": "C",
                        "relativeTimeRange": {
                            "from": 10800,
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
                            "expression": "A",
                            "intervalMs": 1000,
                            "maxDataPoints": 43200,
                            "reducer": "last",
                            "refId": "D",
                            "type": "reduce"
                        },
                        "queryType": "",
                        "refId": "D",
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
                                            "E"
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
                            "expression": "D",
                            "intervalMs": 1000,
                            "maxDataPoints": 43200,
                            "refId": "E",
                            "type": "threshold"
                        },
                        "queryType": "",
                        "refId": "E",
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


@app_b.route("/update_alert", methods=['PUT'])
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

        if panel_title == "CPU Load":
            measurement = "ciscoCPU"
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
                "condition": "E",
                "data": [
                    {
                        "datasourceUid": f"{datasource_uid}",
                        "model": {
                            "adhocFilters": [],
                            "alias": "5sec",
                            "datasource": {
                                "type": "influxdb",
                                "uid": f"{datasource_uid}"
                            },
                            "groupBy": [
                                {
                                    "params": [
                                        "$__interval"
                                    ],
                                    "type": "time"
                                },
                                {
                                    "params": [
                                        "none"
                                    ],
                                    "type": "fill"
                                }
                            ],
                            "intervalMs": 1000,
                            "limit": "",
                            "maxDataPoints": 43200,
                            "measurement": measurement,
                            "orderByTime": "ASC",
                            "policy": "default",
                            "query": "",
                            "refId": "A",
                            "resultFormat": "time_series",
                            "select": [
                                [
                                    {
                                        "params": [
                                            "cpmCPUTotal5secRev"
                                        ],
                                        "type": "field"
                                    },
                                    {
                                        "params": [],
                                        "type": "mean"
                                    }
                                ]
                            ],
                            "slimit": "",
                            "tags": [
                                {
                                    "key": "sysName",
                                    "operator": "=~",
                                    "value": "/^ACE-INTERNET-RTR\\.acedesigners\\.co\\.in$/"
                                }
                            ],
                            "tz": ""
                        },
                        "queryType": "",
                        "refId": "A",
                        "relativeTimeRange": {
                            "from": 10800,
                            "to": 0
                        }
                    },
                    {
                        "datasourceUid": f"{datasource_uid}",
                        "model": {
                            "adhocFilters": [],
                            "alias": "1min",
                            "datasource": {
                                "type": "influxdb",
                                "uid": f"{datasource_uid}"
                            },
                            "groupBy": [
                                {
                                    "params": [
                                        "$__interval"
                                    ],
                                    "type": "time"
                                },
                                {
                                    "params": [
                                        "none"
                                    ],
                                    "type": "fill"
                                }
                            ],
                            "intervalMs": 1000,
                            "limit": "",
                            "maxDataPoints": 43200,
                            "measurement": measurement,
                            "orderByTime": "ASC",
                            "policy": "default",
                            "query": "",
                            "refId": "B",
                            "resultFormat": "time_series",
                            "select": [
                                [
                                    {
                                        "params": [
                                            "cpmCPUTotal1minRev"
                                        ],
                                        "type": "field"
                                    },
                                    {
                                        "params": [],
                                        "type": "mean"
                                    }
                                ]
                            ],
                            "slimit": "",
                            "tags": [
                                {
                                    "key": "sysName",
                                    "operator": "=~",
                                    "value": "/^ACE-INTERNET-RTR\\.acedesigners\\.co\\.in$/"
                                }
                            ],
                            "tz": ""
                        },
                        "queryType": "",
                        "refId": "B",
                        "relativeTimeRange": {
                            "from": 10800,
                            "to": 0
                        }
                    },
                    {
                        "datasourceUid": f"{datasource_uid}",
                        "model": {
                            "adhocFilters": [],
                            "alias": "5min",
                            "datasource": {
                                "type": "influxdb",
                                "uid": f"{datasource_uid}"
                            },
                            "groupBy": [
                                {
                                    "params": [
                                        "$__interval"
                                    ],
                                    "type": "time"
                                },
                                {
                                    "params": [
                                        "none"
                                    ],
                                    "type": "fill"
                                }
                            ],
                            "intervalMs": 1000,
                            "limit": "",
                            "maxDataPoints": 43200,
                            "measurement": measurement,
                            "orderByTime": "ASC",
                            "policy": "default",
                            "query": "",
                            "refId": "C",
                            "resultFormat": "time_series",
                            "select": [
                                [
                                    {
                                        "params": [
                                            "cpmCPUTotal5minRev"
                                        ],
                                        "type": "field"
                                    },
                                    {
                                        "params": [],
                                        "type": "mean"
                                    }
                                ]
                            ],
                            "slimit": "",
                            "tags": [
                                {
                                    "key": "sysName",
                                    "operator": "=",
                                    "value": "cx.home"
                                }
                            ],
                            "tz": ""
                        },
                        "queryType": "",
                        "refId": "C",
                        "relativeTimeRange": {
                            "from": 10800,
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
                            "expression": "A",
                            "intervalMs": 1000,
                            "maxDataPoints": 43200,
                            "reducer": "last",
                            "refId": "D",
                            "type": "reduce"
                        },
                        "queryType": "",
                        "refId": "D",
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
                                            "E"
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
                            "expression": "D",
                            "intervalMs": 1000,
                            "maxDataPoints": 43200,
                            "refId": "E",
                            "type": "threshold"
                        },
                        "queryType": "",
                        "refId": "E",
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
