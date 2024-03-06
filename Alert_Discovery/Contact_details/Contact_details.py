from flask import jsonify, Flask, request, json, Blueprint
import requests, psycopg2

app_V1 = Blueprint('app_v1', __name__)

@app_V1.route("/create_contact_point", methods=['POST'])
def create_contact():
    try:
        data = request.get_json()
        conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password='User@123',
                                port=5432)
        cur = conn.cursor()

        query = "select * from contactpoints where name='{0}'".format(data['name'])
        cur.execute(query)
        out = cur.fetchall()

        if out:
            return ({"type": "failed", "message": "name should be unique!!!"})

        type = data['type']
        if type == 'email':
            addresses = data['address']
            url = None
            token = None
            channel = None
            chatid = None
            bottoken = None
        elif type == 'slack':
            addresses = None
            url = data['url']
            token = None
            channel = data['channel']
            chatid = None
            bottoken = None
        elif type == 'telegram':
            addresses = None
            url = None
            token = None
            channel = None
            chatid = data['chatid']
            bottoken = data['bottoken']
        elif type == 'webhook' or type == 'discord':
            addresses = None
            url = data['url']
            token = None
            channel = None
            chatid = None
            bottoken = None
        else:
            return ({"result": "failure", "message": "unsupported type"})

        base_url = "http://app.autointelli.com:3000/"

        s = requests.Session()
        s.auth = ('admin', 'Wigtra@autointelli1')
        headers = {
            'Content-Type': 'application/json',
            'X-Disable-Provenance': "true"
        }
        payload = {

            "name": data['name'],
            "type": data['type'],
            "isDefault": False,
            "sendReminder": False,
            "secureSettings": {
                "bottoken": bottoken
            },
            "settings": {
                "addresses": addresses,
                "url": url,
                "token": token,
                "channel": channel,
                "chatid": chatid
            }
        }
        response = s.post(base_url + "api/v1/provisioning/contact-points", headers=headers, data=json.dumps(payload))
        if response.status_code == 202:

            contact = response.json()
            uid = contact['uid']
            name = contact['name']
            type = contact['type']
            settings = contact['settings']

            try:

                query = ("insert into contactpoints(uid,name,type,settings,labels) VALUES('{0}', '{1}','{2}',"
                         "'{3}', ARRAY{4})").format(
                    uid, name, type, json.dumps(settings), data.get('object_matchers')[0])
                cur.execute(query)
                conn.commit()
            except Exception as e:
                s.delete(base_url + f"api/v1/provisioning/contact-points/{uid}")
                print(e)
                return ({"result": "failure", "message": "Something Went Wrong... Try After Somtimes!!!"})

            result = create_policies(data['name'], data['object_matchers'])
            if result['result'] == "success":
                return ({"result": "success", "message": "Contact-Point and policies Created!!!"})
            else:
                s.delete(base_url + f"api/v1/provisioning/contact-points/{uid}")
                return ({"result": "failure", "message": "Something Went Wrong... Try After Somtimes!!!"})
    except Exception as e:
        return ({"result": "failure", "message": e})


def create_policies(name, object):
    try:
        base_url = "http://app.autointelli.com:3000/"

        s = requests.Session()
        s.auth = ('admin', 'Wigtra@autointelli1')
        headers = {
            'Content-Type': 'application/json',
            'X-Disable-Provenance': "true"
        }

        payload = {'receiver': name, 'object_matchers': object}

        response = s.get(base_url + "api/v1/provisioning/policies", headers=headers, data=json.dumps(payload))
        datas = response.json()

        if 'routes' not in datas:
            l = [payload]
            datas['routes'] = l
        else:
            datas['routes'].append(payload)
        response = s.put(base_url + "api/v1/provisioning/policies", headers=headers, data=json.dumps(datas))

        return ({"result": "success", "message": response.text})
    except:
        return ({"result": "failure", "message": "Something Went Wrong!!!"})


def delete_policies(name):
    try:

        base_url = "http://app.autointelli.com:3000/"

        s = requests.Session()
        s.auth = ('admin', 'Wigtra@autointelli1')
        headers = {
            'Content-Type': 'application/json',
            'X-Disable-Provenance': "true"
        }

        response = s.get(base_url + "api/v1/provisioning/policies", headers=headers)
        datas = response.json()
        if 'routes' not in datas:
            return ({"result": "success"})
        else:
            data = datas['routes']

            for i in range(len(data)):
                if data[i]['receiver'] == name:
                    del data[i]

            if len(data) > 0:

                del datas['routes']
                l = data
                datas['routes'] = l
                response = s.put(base_url + "api/v1/provisioning/policies", headers=headers, data=json.dumps(datas))

                if response.status_code == 202:
                    return ({"result": "success", "message": response.text})
                else:
                    return ({"result": "failure", "message": response.text})
            else:
                del datas['routes']
                response = s.put(base_url + "api/v1/provisioning/policies", headers=headers, data=json.dumps(datas))

                if response.status_code == 202:
                    return ({"result": "success", "message": response.text})
                else:
                    return ({"result": "failure", "message": response.text})


    except Exception as e:
        return ({"result": "failure", "message": e})


def getall_contactPoints():
    try:
        base_url = "http://app.autointelli.com:3000/"

        s = requests.Session()
        s.auth = ('admin', 'Wigtra@autointelli1')
        response = s.get(base_url + "api/v1/provisioning/contact-points", verify=False)
        data = response.json()

        return ({"result": "success", "data": data})
    except:
        return ({"result": "failure", "message": "Something Went Wrong!!!"})


@app_V1.route("/update_contact_point", methods=['PUT'])
def update_contactPoints():
    global settings
    try:
        data = request.get_json()
        conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password='User@123',
                                port=5432)
        cur = conn.cursor()
        cur.execute("select * from contactpoints where contact_id={0}".format(data['id']))
        out = cur.fetchone()
        uid = out[1]
        name = out[3]
        if name == data['name']:
            pass
        else:

            query = "SELECT * from contactpoints where name = '{0}' AND contact_id != {1}".format(data['name'],
                                                                                                  data['id'])
            cur.execute(query)
            res = cur.fetchall()
            if res:
                return ({"type": "failed", "message": "name should be unique!!!"})
        type = data['type']
        if type == 'email':
            addresses = data['address']
            url = None
            token = None
            channel = None
            chatid = None
            bottoken = None
        elif type == 'slack':
            addresses = None
            url = data['url']
            token = None
            channel = data['channel']
            chatid = None
            bottoken = None
        elif type == 'telegram':
            addresses = None
            url = None
            token = None
            channel = None
            chatid = data['chatid']
            bottoken = data['bottoken']
        elif type == 'webhook' or type == 'discord':
            addresses = None
            url = data['url']
            token = None
            channel = None
            chatid = None
            bottoken = None
        else:
            return ({"result": "failure", "message": "unsupported type"})

        base_url = "http://app.autointelli.com:3000/"

        s = requests.Session()
        s.auth = ('admin', 'Wigtra@autointelli1')
        headers = {
            'Content-Type': 'application/json',
            'X-Disable-Provenance': "true"
        }
        payload = {

            "name": data['name'],
            "type": data['type'],
            "isDefault": False,
            "sendReminder": False,
            "secureSettings": {
                "bottoken": bottoken
            },
            "settings": {
                "addresses": addresses,
                "url": url,
                "token": token,
                "channel": channel,
                "chatid": chatid
            }
        }
        response = s.put(base_url + f"api/v1/provisioning/contact-points/{uid}", headers=headers,
                         data=json.dumps(payload))

        if response.status_code == 202:

            name = data['name']
            type = data['type']
            all = getall_contactPoints()
            if all['result'] == 'success':
                contacts = all['data']
                for i in contacts:
                    if i['uid'] == uid:
                        settings = i['settings']

            try:
                query = "update contactpoints  set name='{0}',type='{1}',settings='{2}' where contact_id={3};".format(
                    name, type, json.dumps(settings), data['id'])
                cur.execute(query)
                conn.commit()
            except Exception as e:

                return ({"result": "failure", "message": "Something Went Wrong... Try After Somtimes!!!"})

            result = create_policies(data['name'], data['object_matchers'])
            if result['result'] == "success":
                return ({"result": "success", "message": "Contact-Point and policies Created!!!"})
            else:

                return ({"result": "failure", "message": "Something Went Wrong... Try After Somtimes!!!"})
    except Exception as e:
        return ({"result": "failure", "message": "Something Went Wrong"})


@app_V1.route("/get_all_contact_point", methods=['GET'])
def get_all_contact_points():
    try:
        conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password='User@123', port=5432)
        cur = conn.cursor()

        query = "SELECT * FROM contactpoints"
        cur.execute(query)
        cols = [column[0] for column in cur.description]
        rows = cur.fetchall()
        ll = []

        if len(rows) > 0:
            for eachRow in rows:
                ll.append(dict(zip(cols, eachRow)))

        if ll != []:
            return jsonify({"type": "success", "contactpoints": ll})
        else:
            return jsonify({"type": "error", "message": "No alert contact points found"})

    except Exception as e:
        return jsonify({"type": "error", "message": f"Error: {str(e)}"})


@app_V1.route("/single_contact_point", methods=['GET'])
def get_contact_point():
    try:
        id = request.args.get('id')

        if not id:
            return jsonify({"message": "Alert ID is missing"}), 400

        conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password='User@123', port=5432)
        cur = conn.cursor()

        query = "SELECT * FROM contactpoints WHERE contact_id = %s"
        cur.execute(query, (id,))
        cols = [column[0] for column in cur.description]
        rows = cur.fetchall()
        ll = []

        if len(rows) > 0:
            for eachRow in rows:
                ll.append(dict(zip(cols, eachRow)))

        if ll != []:
            return jsonify({"type": "success", "contact_details": ll})
        else:
            return jsonify({"type": "error", "message": f"No contact points found with ID {id}"}), 404

    except Exception as e:
        return jsonify({"type": "error", "message": f"Error: {str(e)}"}), 500


@app_V1.route("/delete_contact_point", methods=['DELETE'])
def delete_contact_point(*args):
    id = request.args.get('id')

    if not id:
        return jsonify({"message": "contact ID is missing"}), 400

    base_url = "http://app.autointelli.com:3000/"
    s = requests.Session()
    s.auth = ('admin', 'Wigtra@autointelli1')
    conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password='User@123', port=5432)
    cur = conn.cursor()

    try:
        query = """SELECT * from contactpoints WHERE contact_id='{0}' """.format(id)
        cur.execute(query)
        res = cur.fetchone()
        uid = res[1]
        name = res[3]
        del_policies = delete_policies(name)

        if del_policies['result'] == 'success':

            query = """DELETE from contactpoints WHERE contact_id={0}""".format(id)
            cur.execute(query)
            conn.commit()

            response = s.delete(base_url + f"api/v1/provisioning/contact-points/{uid}")
            if response.status_code == 202:
                return jsonify({"result": "Success", "message": "contact deleted successfully!!"})
            else:
                return ({"type": "Failed", "message": "try after sometimes"})
        else:
            return del_policies
    except Exception as e:
        return jsonify({"type": "error", "message": f"Error: {str(e)}"})





