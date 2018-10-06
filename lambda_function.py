from __future__ import print_function
from html.parser import HTMLParser
import requests, os

from local_config import *

AR_USERNAME = os.environ['AR_USERNAME']
AR_PASSWORD = os.environ['AR_PASSWORD']

class ArHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.recording = 0
        self.data = None

    def handle_starttag(self, tag, attributes):
        if tag != 'span':
            return
        if self.recording:
            self.recording += 1
            return
        for name, value in attributes:
            if name == 'id' and value == 'ctl00_ContentPlaceHolder_Content_mBox_Progress_mSpan_Points':
                break
            else:
                return

        self.recording = 1

    def handle_endtag(self, tag):
        if tag == 'span' and self.recording:
            self.recording -= 1

    def handle_data(self, data):
        if self.recording:
            self.data = data

def retrieve_ar_points():

    AR_LOGIN_DATA['mBox_Login$mTextBox_UserName']=AR_USERNAME
    AR_LOGIN_DATA['mBox_Login$mTextBox_Password']=AR_PASSWORD

    r1 = requests.post(AR_LOGIN_URL,data=AR_LOGIN_DATA,allow_redirects=False)
    r2 = requests.post(AR_LP_URL,cookies=r1.cookies)
    parser = ArHTMLParser()
    parser.feed(r2.text)
    return parser.data

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }

# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the A R Points Alexa Skill"
    reprompt_text = None
    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the Alexa Skills Kit sample. Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))

def get_ar_points(intent, session):
    session_attributes = {}
    reprompt_text = None
    speech_output = "Your current total is {}".format(retrieve_ar_points())
    should_end_session = True

    return build_response(session_attributes, build_speechlet_response(intent['name'], speech_output, reprompt_text, should_end_session))

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """
    print("on_session_started requestId=" + session_started_request['requestId'] + ", sessionId=" + session['sessionId'])

def on_launch(launch_request, session):
    # Called when the user launches the skill without specifying what they want
    print("on_launch requestId=" + launch_request['requestId'] + ", sessionId=" + session['sessionId'])
    return get_welcome_response()

def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """
    print("on_intent requestId=" + intent_request['requestId'] + ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "PointValue":
        return get_ar_points(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    print("on_session_ended requestId=" + session_ended_request['requestId'] + ", sessionId=" + session['sessionId'])

# --------------- Main handler ------------------

def lambda_handler(event, context):
    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
