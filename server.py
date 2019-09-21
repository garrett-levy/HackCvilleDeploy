from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests

app = Flask(__name__)

DWITTER_SERVER = 'http://67.207.94.120:5000'

# Twilio will call the '/sms' endpoint of our server when a text is received
@app.route('/sms', methods=['POST'])
def sms_reply():
    # Pulling the message body and number from Twilio's request
    body = request.form['Body']
    number = request.form['From']

    # Creating a response variable in the form Twilio expects
    # The contents of this will be set later
    resp = MessagingResponse()

    # If the message body is 'dweets' (ignoring case sensitivity), send them the last 10 dweets
    # Otherwise, post the message body as a new dweet
    if body.lower() == 'dweets':
        try:
            # Making a GET request to the Dwitter server at the /dweets endpoint
            # .format is used to replace {} with our already defined server IP
            r = requests.get('{}/dweets'.format(DWITTER_SERVER))
            # Will throw an exception if Dwitter sends back a failure status code (ex: 404)
            # This in theory should never happen unless Dwitter is down,
            # but it's good practice to handle errors regardless
            r.raise_for_status()
        except:
            # .message is a premade function from Twilio that can be used on MessagingResponse objects
            resp.message('Failed to fetch current dweets!')
        else:
            # Parsing the JSON response from Dwitter as a dictionary
            dweets = r.json()

            response_message = 'Here are the current dweets:\n'
            for dweet in dweets:
                response_message += '\n{}: {}'.format(
                    dweet['user']['username'], dweet['message']
                )

            resp.message(response_message)

    else:
        try:
            # Making a POST request to the Dwitter server with our dweet username and message
            r = requests.post('{}/new'.format(DWITTER_SERVER), data={
                'username': "Garrett",
                'message': body
            })
            r.raise_for_status()
        except:
            resp.message('Failed to post your dweet!')
        else:
            resp.message('Posted your dweet!')

    # str(resp) returns a specially formatted string that, when sent back to Twilio,
    # will forward our response text to the user via SMS
    # Feel free to print(str(resp)) if you're curious what this looks like
    return str(resp)
  
@app.route("/")
def hello():
  return "This is a Dwitter mobile implemtation! Add https://deploy-project1.glitch.me/sms as a webhook to a Twilio number to test."


if __name__ == '__main__':
    app.run(debug=True)
