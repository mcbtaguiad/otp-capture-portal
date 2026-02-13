#!/usr/bin/python
from flask import Flask, request, send_from_directory, render_template, render_template_string, jsonify, url_for, session, flash, redirect, session
import os
import subprocess
import datetime
import os.path
import logging
import pyotp
import qrcode
from io import BytesIO
import base64
import time
from functools import wraps
import sqlite3
from werkzeug.security import check_password_hash



# version
version = "2.0"

# variables
base_dir = os.path.abspath(os.path.dirname(__file__))
web_folder = base_dir+"/web"
use_reloader = False

# load configuration file
if os.path.isfile(base_dir+'/config_custom.py'):
    import config_custom
    config = config_custom
else:
    import config

# define the web application
app = Flask(__name__, template_folder=web_folder)
app.secret_key = config.secret_key

# logging.basicConfig(filename=base_dir+'/otpspot.log', level=logging.DEBUG)

# render index if no page name is provided


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def root(path):
    return render_template("index.html", title=config.language["title"], welcome_message=config.language["welcome_message"], otp_placeholder=config.language["otp_placeholder"], register_button=config.language["register_button"], registering_message=config.language["registering_message"], registered_successfully=config.language["registered_successfully"], error_banner=config.language["error_banner"], error_invalid_parameter=config.language["error_invalid_parameter"], error_invalid_otp=config.language["error_invalid_otp"], error_term=config.language["error_term"])

# return favicon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(base_dir, 'images'), "favicon.ico")

# static folder (web)
@app.route('/web/<path:filename>')
def static_page(filename):
    return send_from_directory(web_folder, filename)

@app.route("/data/<path:filename>")
def config_static(filename):
    return send_from_directory("data", filename)



# register a new client
@app.route('/register')
def register():
    otp = mac = ip = tok = gatewayname = None
    if "otp" in request.args:
        otp = request.args.get("otp")
    if "mac" in request.args:
        mac = request.args.get("mac")
    if "ip" in request.args:
        ip = request.args.get("ip")
    if "tok" in request.args:
        tok = request.args.get("tok")
    if "gatewayname" in request.args:
        gatewayname = request.args.get("gatewayname")
    if otp is None or mac is None or ip is None or tok is None or gatewayname is None:
        return "1"
    otp_valid = verify_otp(otp)
    logging.info('['+datetime.datetime.now().isoformat()+'] '+str(gatewayname) +
                 ' '+str(ip)+' '+str(mac)+' '+str(tok)+': '+str(otp_valid))
    if config.otp["enabled"] and not otp_valid:
        return "2"
    return "0"


###### login ######

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash("Please log in to access this page.")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/admin")
def index():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        if request.is_json:
            data = request.get_json()
            username = data.get("username", "").strip()
            password = data.get("password", "").strip()

            if not username or not password:
                return jsonify({
                    "status": "fail",
                    "message": config.languagelogin["errorEmptyFields"]
                })

            if (
                username == config.ADMIN_USERNAME and
                check_password_hash(config.ADMIN_PASSWORD_HASH, password)
            ):
                session['username'] = username
                return jsonify({
                    "status": "success",
                    "message": config.languagelogin["loginSuccess"],
                    "redirect": "/token"
                })

            return jsonify({
                "status": "fail",
                "message": config.languagelogin["loginFailed"]
            })

        # Non-AJAX fallback
        else:
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "").strip()

            if (
                username == config.ADMIN_USERNAME and
                check_password_hash(config.ADMIN_PASSWORD_HASH, password)
            ):
                session['username'] = username
                return render_template(
                    "login.html",
                    **config.languagelogin,
                    success_message=config.languagelogin["loginSuccess"]
                )

            return render_template(
                "login.html",
                **config.languagelogin,
                error_message=config.languagelogin["loginFailed"]
            )

    return render_template("login.html", **config.languagelogin)


@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("You’ve been logged out.", "info")
    return redirect(url_for("login"))


##### token #####

def get_totp_secret():
    try:
        with open("data/.google_authenticator") as f:
            first_line = f.readline().strip()
            return first_line
    except Exception as e:
        app.logger.error(f"Failed to read TOTP secret: {e}")
        return None



@app.route("/token")
@login_required
def token_page():
    secret = request.args.get("secret") or get_totp_secret()
    return render_template("token.html", secret=secret)


@app.route("/totp")
@login_required
def totp_api():
    secret = request.args.get("secret") or get_totp_secret()

    if not secret:
        return jsonify({"error": "TOTP secret not available"}), 500

    totp = pyotp.TOTP(secret)
    code = totp.now()

    period = totp.interval
    now = int(time.time())
    next_update = (now // period + 1) * period

    img = qrcode.make(code)
    buf = BytesIO()
    img.save(buf, format="PNG")
    qr_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    return jsonify({
        "code": code,
        "qr_b64": qr_b64,
        "period": period,
        "next_update": next_update
    })


@app.after_request
def add_header(response):
    """Disable caching for /totp responses."""
    response.headers["Cache-Control"] = "no-store"
    return response



# policy

@app.route("/policy")
def policy():
    business_name = os.environ.get("BUSINESS_NAME", "Swamp Coffee")
    return render_template("policy.html", business_name=business_name)
    # return render_template("policy.html")

# run the web server
def run():
    app.run(debug=True, use_reloader=use_reloader,
            host='0.0.0.0', port=config.web["port"])

# run a command and return the output
def run_command(command):
    process = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = b''
    for line in process.stdout.readlines():
        output = output+line
    return output.rstrip()

# verify otp code
def verify_otp(code):
    command = "echo "+config.otp["password"]+code+" |sudo pamtester "+config.otp["pam_service"] + \
        " "+config.otp["username"] + \
        " authenticate 2>&1|grep -c 'successfully authenticated'"
    found = int(run_command(command))
    if found == 1:
        return True
    return False


# run the main app
if __name__ == '__main__':
    logging.info("Welcome to OTPspot v"+version)
    run()
