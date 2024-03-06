from flask import Flask
from Alert_Discovery.Alert_details.Alert_Payload import app_bp
from Alert_Discovery.Alert_details.Alert_Thresholds import app_r
from Alert_Discovery.Alert_CRUD.Amazon_EC2 import app_a
from Alert_Discovery.Alert_CRUD.Network_Device_Dashboard import app_b
from Alert_Discovery.Alert_CRUD.Network_Utilization_Dashboard import app_c
from Alert_Discovery.Alert_CRUD.Operating_System_Metrics import app_d
from Alert_Discovery.Alert_CRUD.Ping_Network_Uptime import app_e
from Alert_Discovery.Contact_details.Contact_details import app_V1
from Alert_Discovery.Dashboard_details.Dashboard_details import app_V2
# from Alert_Discovery.Dashboard_details.Dashboard_table import app_V3
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

app.register_blueprint(app_bp, url='/payload')
app.register_blueprint(app_r, url='/thresholds')
app.register_blueprint(app_a, url='/alert')
app.register_blueprint(app_b, url='/create_alert,/update_alert')
app.register_blueprint(app_c, url='/update_alert,create_alert')
app.register_blueprint(app_d, url='/create_alert,update_alert,updown_create,updown_update')
app.register_blueprint(app_e, url='/update_alert,create_alert')
app.register_blueprint(app_V1, url='/delete_contact_point,single_contact_point,get_all_contact_point')
app.register_blueprint(app_V2, url='/get_all_dashboard,get_all_panel_details,get_all_datasource,get_all_folders')
# app.register_blueprint(app_V3, url='/dashboard')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
