# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_python37_app]
from flask import Flask, jsonify, request
from random import choice
import json
import requests
import config



# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)

# Slack API access token
BOT_ACCESS_TOKEN=config.SLACK_API_CONFIG["BOT_ACCESS_TOKEN"]

# Stored for the duration of the instance to handle multiple requests from Slack of the same mention
PREVIOUS_REQ=""

# Static list of lunch options
OPTIONS = ["Hop", "Thai Express", "Paradice Slice", "M&S Chicken", "Shoryu", "On the Bab", "Korean BBQ Dosirak",
               "The Posh Burger Co", "Tas Firin", "Wagamama", "Farmer J", "Chilango", "Shake Shack",
               "Xian Biang Biang Noodles", "Rosa's Thai Café"]


@app.route("/", methods=["GET", "POST"])
def picker():
    """Responds to request with a suggestion for where to eat lunch from the Gobal list of options"""
    try:
        global PREVIOUS_REQ

        # Gets message from the request. If it is not JSON from a Slack channel mention then will fail and do the exception
        data=json.loads(request.data)
        msg=data["event"]["text"]
        print(PREVIOUS_REQ)
        print(data)
        # Check for Slack sending the same request data.
        if data==PREVIOUS_REQ:
            return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
        else:
            PREVIOUS_REQ=data

        # Construct reply to mention
        if "lunch" in msg or "food" in msg or "eat" in msg:
            reply="I think you should go with "+choice(OPTIONS)
        elif "add" in msg:
            reply="Okay added to the list"
        else:
            reply="Sorry I'm pretty simple and can't understand that. But I am pretty " \
                  "good at lunch recommendations. How about "+choice(OPTIONS)

        # Build and send request to send reply to channel through Slack API
        url = "https://slack.com/api/chat.meMessage"
        channel = data["event"]["channel"]
        headers={"Authorization": "Bearer %s" %BOT_ACCESS_TOKEN, "Content-Type": "application/json; charset=utf-8"}
        payload={"channel":channel, "text":reply}
        requests.post(url, headers=headers, json=payload)

        return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

    except:
        return jsonify(text=choice(OPTIONS))



if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python37_app]
