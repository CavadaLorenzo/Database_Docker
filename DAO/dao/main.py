import sys
import os
import datetime
import hashlib
from flask import Flask, redirect, send_from_directory, request
from flask_sqlalchemy import SQLAlchemy
from safrs import SAFRSAPI, SAFRSRestAPI  # api factory
from safrs import SAFRSBase  # db Mixin
from safrs import jsonapi_rpc  # rpc decorator
from safrs.api_methods import startswith  # rpc methods
from flask import url_for, jsonify

# This html will be rendered in the swagger UI
description = """
API used to talk with the database which keeps track of all the online servers
"""

db = SQLAlchemy()

POSTGRES_USER = os.environ['POSTGRES_USER']
POSTGRES_PASSWORD = os.environ['POSTGRES_PASSWORD']
POSTGRES_IP = os.environ['POSTGRES_IP'] 
POSTGRES_PORT = os.environ['POSTGRES_PORT'] 
POSTGRES_DB_NAME = os.environ['POSTGRES_DB_NAME'] 

# debug only
"""
POSTGRES_USER = 'admin'
POSTGRES_PASSWORD = 'admin'
POSTGRES_IP = '0.0.0.0'
POSTGRES_PORT = '54320'
POSTGRES_DB_NAME = 'servers'
"""

# Example sqla database object
class Servers(SAFRSBase, db.Model):
    """
        description: The server object represent a real FTP server running somewhere. Each FTP server has an unique ID and a server_name.
    """

    __tablename__ = "Servers"
    id = db.Column(db.String, primary_key=True)
    server_name = db.Column(db.String, nullable=False, unique=True)
    server_ip = db.Column(db.String, nullable=False)
    server_port = db.Column(db.String, nullable=False)
    server_ssh_port = db.Column(db.String, nullable=False)
    __table_args__ = (db.UniqueConstraint('server_ip', 'server_port'), )

    

    # Following method is exposed through the REST API
    # This means it can be invoked with a HTTP POST
    """
    @classmethod
    @jsonapi_rpc(http_methods=["POST"])
    def send_mail(self, **args):
 
        description : Send an email
        args:
            email:
                type : string
                example : test email

        return {"result": args}
    """

class Uploads(SAFRSBase, db.Model):
    """
        description: The server object represent a real FTP server running somewhere. Each FTP server has an unique ID and a server_name.
    """

    __tablename__ = "File_list"
    id = db.Column(db.String, primary_key=True)
    server_id = db.Column(db.String, nullable=False, unique=True)
    filename = db.Column(db.String, nullable=False)
    upload_date = db.Column(db.String, nullable=False)


    


def start_api(swagger_host="0.0.0.0", PORT=None):

    # Add startswith methods so we can perform lookups from the frontend
    SAFRSBase.startswith = startswith
    # Needed because we don't want to implicitly commit when using flask-admin
    SAFRSBase.db_commit = False

    with app.app_context():
        db.init_app(app)
        db.create_all()
        # populate the database

        api = SAFRSAPI(
            app,
            host=swagger_host,
            port=PORT,
            prefix=API_PREFIX,
            api_spec_url=API_PREFIX + "/swagger",
            schemes=["http", "https"],
            description=description,
        )

        api.expose_object(Servers)
        api.expose_object(Uploads)

API_PREFIX = "/api"  # swagger location
app = Flask("Server Info")
app.config.update(SQLALCHEMY_DATABASE_URI=f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_IP}:{POSTGRES_PORT}/{POSTGRES_DB_NAME}", DEBUG=True)

@app.route("/")
def goto_api():
    return redirect(API_PREFIX)


if __name__ == "__main__":
    HOST = "0.0.0.0"
    PORT = "5000"
    start_api(HOST, PORT)
    app.run(host=HOST, port=PORT, threaded=False)
    
