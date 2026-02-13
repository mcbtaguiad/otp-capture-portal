#!/usr/bin/python
import os
from werkzeug.security import generate_password_hash


ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME")
ADMIN_PASSWORD_HASH = generate_password_hash(os.environ.get("ADMIN_PASSWORD"))

secret_key = "imasuperduperextremesupersecretkey"

# web portal related configuration
web = {
	# listen on this port
	"port": 8000,
}


# otp verification related configuration
otp = {
	# the username of the user to test the OTP against
	"username": "hotspot",
	# the password of the user
	"password": "password",
	# the name of the pam service to be used for verifying the authentication
	"pam_service": "otpspot",
	# if true the OTP is verified, if false any OTP will be accepted
	"enabled": True,
}

# HTML template locale
language = {
	'title': os.environ.get("BUSINESS_NAME", 'Swamp Coffee') + ' Guest Login',
	'welcome_message': 'Please call staff for Voucher',
	'otp_placeholder': 'Voucher',
	'register_button': 'Connect',
	'registering_message': 'Connecting...',
	'registered_successfully': 'Connected',
	'error_banner': 'ERROR',
	'error_invalid_parameter': 'Missing required parameter',
	'error_invalid_otp': 'Invalid voucher provided',	
	'error_term': 'Please accept the Terms of Use before connecting.'

}

languagelogin = {
	"welcome_message": "Don’t share credentials with non-employees.",
	"errorBanner": "Error",
	"errorEmptyFields": "Please enter both username and password.",
	"loggingIn": "Logging in...",
	"loginSuccess": "Login successful!",
	"loginFailed": "Invalid username or password.",
	"connectButton": "Login"
}

