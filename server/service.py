from flask import Flask, request, jsonify
import os
import json
import threading
from datetime import datetime
import dao
import driver_drowsiness

app = Flask(__name__)

def start_drowsiness_detection():
    try:
        driver_drowsiness.exec_program()
    except Exception as e:
        print(f"Error starting drowsiness detection: {e}")

@app.route('/start', methods=['POST'])
def start_detection():
    try:
        # Start drowsiness detection in a separate thread
        detection_thread = threading.Thread(target=start_drowsiness_detection)
        detection_thread.daemon = True
        detection_thread.start()
        return jsonify({"message": "Drowsiness detection started successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/login', methods=['POST'])
def call_login():
    try:
        uid = request.form.get("pid")
        taxi = request.form.get("taxi")
        password = request.form.get("password")
        
        if not all([uid, taxi, password]):
            return jsonify({"error": "Missing required parameters"}), 400
            
        dao.login(uid, taxi, password)
        return jsonify({
            "message": f"Driver with id: {uid} has been successfully assigned taxi: {taxi}",
            "status": "success"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/admlogin', methods=['GET'])
def call_admlogin():
    try:
        uid = request.args.get("pid")
        password = request.args.get("password")
        jsp = request.args.get("jsonp")
        
        if not all([uid, password, jsp]):
            return jsonify({"error": "Missing required parameters"}), 400
            
        res = json.dumps(dao.admlogin(uid, password))
        return f"{jsp}({res})"
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/session', methods=['GET'])
def call_session():
    try:
        jsp = request.args.get("jsonp")
        if not jsp:
            return jsonify({"error": "Missing jsonp parameter"}), 400
            
        res = json.dumps(dao.session_details())
        return f"{jsp}({res})"
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/sos', methods=['GET'])
def call_sos():
    try:
        res = dao.sos_details()
        return jsonify(res)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        print("Received signup data:", data)
        db = connect()
        result = db.user.insert_one(data)
        return jsonify({"success": True})
    except Exception as e:
        print("Signup error:", str(e))
        return jsonify({"error": str(e)}), 400
    
@app.route("/")
def index():
    return jsonify({
        "message": "Driver Drowsiness Detection API",
        "version": "1.0",
        "endpoints": [
            "/start - Start drowsiness detection",
            "/login - Driver login",
            "/admlogin - Admin login",
            "/session - Session management",
            "/sos - SOS alerts"
        ]
    })
    
    
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6060, debug=False)