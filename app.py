import json
import os
import logging
from requests_oauthlib import OAuth1Session
from flask import Flask, render_template_string, redirect, url_for, request, flash
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random string

# File to save credentials
CREDENTIALS_FILE = "twitter_credentials.json"

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def authenticate():
    consumer_key = os.getenv("CONSUMER_KEY")
    consumer_secret = os.getenv("CONSUMER_SECRET")

    if not consumer_key or not consumer_secret:
        logging.error("Consumer key or consumer secret is missing.")
        return None

    logging.debug("Consumer key and secret found, proceeding with authentication.")

    # Check if credentials file exists
    if os.path.exists(CREDENTIALS_FILE):
        logging.debug(f"Credentials file {CREDENTIALS_FILE} found.")
        with open(CREDENTIALS_FILE, 'r') as file:
            creds = json.load(file)
            return creds["consumer_key"], creds["consumer_secret"], creds["access_token"], creds["access_token_secret"]

    # If credentials file doesn't exist, proceed with authentication
    try:
        request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
        oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)
        fetch_response = oauth.fetch_request_token(request_token_url)

        resource_owner_key = fetch_response.get("oauth_token")
        resource_owner_secret = fetch_response.get("oauth_token_secret")
        logging.debug("Request token obtained.")

        base_authorization_url = "https://api.twitter.com/oauth/authorize"
        authorization_url = oauth.authorization_url(base_authorization_url)

        logging.info("Redirecting user to Twitter for authorization.")
        print("Please go here and authorize:", authorization_url)
        verifier = input("Paste the PIN here: ")

        access_token_url = "https://api.twitter.com/oauth/access_token"
        oauth = OAuth1Session(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=resource_owner_key,
            resource_owner_secret=resource_owner_secret,
            verifier=verifier,
        )
        oauth_tokens = oauth.fetch_access_token(access_token_url)

        access_token = oauth_tokens["oauth_token"]
        access_token_secret = oauth_tokens["oauth_token_secret"]

        with open(CREDENTIALS_FILE, 'w') as file:
            json.dump({
                "consumer_key": consumer_key,
                "consumer_secret": consumer_secret,
                "access_token": access_token,
                "access_token_secret": access_token_secret
            }, file)
        
        logging.info("Access token and secret saved.")
        return consumer_key, consumer_secret, access_token, access_token_secret

    except Exception as e:
        logging.error(f"Error during authentication: {e}")
        return None

@app.route('/')
def home():
    html_content = '''
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Twitter Authorization</title>
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
    </head>
    <body>
        <div class="container mt-5">
            <h1>Authorize with Twitter</h1>
            <form method="post" action="{{ url_for('authorize') }}">
                <button type="submit" class="btn btn-primary">Authorize</button>
            </form>
            {% with messages = get_flashed_messages(with_categories=true) %}
              {% if messages %}
                <div class="mt-3">
                  {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                  {% endfor %}
                </div>
              {% endif %}
            {% endwith %}
        </div>
    </body>
    </html>
    '''
    return render_template_string(html_content)

@app.route('/authorize', methods=['POST'])
def authorize():
    creds = authenticate()
    if creds:
        flash("Authorization successful!", "success")
        logging.info("User authorized successfully.")
    else:
        flash("Authorization failed. Check logs for details.", "danger")
        logging.error("Authorization failed.")
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
