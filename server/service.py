from flask import Flask , request, jsonify
import os
import json

from applescript import tell


import dao
import driver_drowsiness


app = Flask(__name__)

#@app.route('/drowsy', methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/login', methods=['GET', 'POST', 'PUT', 'DELETE'])
def call_login():
    #out = os.popen('/Users/harishsagar/PycharmProjects/Driver_Drowsy_Master/server/driver_drowsiness.py').read()
    #pid = os.fork()
    #print(pid)
    #os.system("gnome-terminal 'sudo apt-get update'")
    yourCommand = 'ls'
    #tell.app( 'Terminal', 'do script "' + yourCommand + '"')
    #driver_drowsiness.fork()
    uid = request.form.get("pid")
    taxi = request.form.get("taxi")
    password = request.form.get("password")
    print(uid)
    print(taxi)
    print(password)
    dao.login(uid, taxi, password)
    out = "Driver with id : "+uid +" has been successfully assigned taxi : "+taxi
    return jsonify(out)

@app.route('/admlogin', methods=['GET', 'POST', 'PUT', 'DELETE'])
def call_admlogin():
    uid = request.args.get("pid")
    password = request.args.get("password")
    print(uid + "   "+ password)
    jsp = request.args.get("jsonp")
    print(jsp)
    res = json.dumps(dao.admlogin(uid, password))
    res2 = jsp+"("+res+")"
    print(res2)
    return res2



@app.route('/session', methods=['GET', 'POST', 'PUT', 'DELETE'])
def call_session():
    jsp = request.args.get("jsonp")
    print(jsp)
    res = json.dumps(dao.session_details())
    res2 = jsp+"("+res+")"
    print(res2)
    return res2


@app.route('/sos', methods=['GET', 'POST', 'PUT', 'DELETE'])
def call_sos():
    sosid = request.args.get("sosid")
    print(sosid)
    res = json.dumps(dao.sos_details(sosid))
    jsp = request.args.get("jsonp")
    print(jsp)
    res2 = jsp+"("+res+")"
    print(res2)
    return res2


@app.route("/")
def index():
    return "Homepage of GeeksForGeeks"


app.run(host="0.0.0.0", port=6060)
