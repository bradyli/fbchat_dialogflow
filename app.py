import os
import sys
import json
from datetime import datetime

import requests
from flask import Flask, request, render_template

try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai

app = Flask(__name__)

# dialogflow Client access token
ai = apiai.ApiAI("e51cee34d77d475081bdfdc9e59645a1")
# dialogflow Developer access token
aiDAT = 'ff17f352047e4c2daeff000ddf59d763'

@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == "ohmyfood":
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return render_template("index.html")


@app.route('/', methods=['POST'])
def webhook():
    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":   # make sure this is a page subscription

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):     # someone sent us a message
                    received_message(messaging_event)

                elif messaging_event.get("delivery"):  # delivery confirmation
                    pass
                    # received_delivery_confirmation(messaging_event)

                elif messaging_event.get("optin"):     # optin confirmation
                    pass
                    # received_authentication(messaging_event)

                elif messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    received_postback(messaging_event)

                else:    # uknown messaging_event
                    log("Webhook received unknown messaging_event: " + messaging_event)

    return "ok", 200

def received_message(event):
    
    sender_id = event["sender"]["id"]        # the facebook ID of the person sending you the message
    recipient_id = event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
    
    # could receive text or attachment but not both
    if "text" in event["message"]:
        message_text = event["message"]["text"]

        # parse message_text and give appropriate response   
        if message_text == 'image':
            send_image_message(sender_id)

        elif message_text == 'file':
            send_file_message(sender_id)

        elif message_text == 'audio':
            send_audio_message(sender_id)

        elif message_text == 'video':
            send_video_message(sender_id)

        elif message_text == 'button':
            send_button_message(sender_id)

        elif message_text == 'generic':
            send_generic_message(sender_id)

        elif message_text == 'share':
            send_share_message(sender_id)

        else: # default case
            #send_message(sender_id, "Echo: " + message_text)
            request = ai.text_request()
            request.session_id = sender_id
            request.query = message_text
            query_dialogflow(event, request)

    elif "attachments" in event["message"]:
        message_attachments = event["message"]["attachments"]
        for messaging_event in message_attachments:
            if messaging_event["type"] == 'location':
                lat = messaging_event["payload"]["coordinates"]["lat"]
                lon = messaging_event["payload"]["coordinates"]["long"]
                log("coor lot : {text}, long : {textlon}".format(text=lat, textlon=lon))
                send_button_message(sender_id)
            else:
                send_message(sender_id, "Message with attachment received")


def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    call_send_api(data)

def send_local_message(recipient_id):
    data = json.dumps({
        "recipient":{
            "id":recipient_id
          },
          "message":{
            "text": "請讓我們定位您的位置或是輸入期望用餐的地點（縣/市）",
            "quick_replies":[
              {
                "content_type":"location",
              }
            ]
          }    
    })
    call_send_api(data)

def send_quick_message(recipient_id):
    data = json.dumps({
        "recipient":{
            "id":recipient_id
          },
          "message":{
            "text": "請選擇行政區",
            "quick_replies":[
              {
                "content_type":"text",
                "title":"中正區",
                "payload":"<POSTBACK_PAYLOAD>",
                "image_url":""
              },
              {
                "content_type":"text",
                "title":"大同區",
                "payload":"<POSTBACK_PAYLOAD>",
                "image_url":""
              },
              {
                "content_type":"text",
                "title":"中山區",
                "payload":"<POSTBACK_PAYLOAD>",
                "image_url":""
              },
              {
                "content_type":"text",
                "title":"松山區",
                "payload":"<POSTBACK_PAYLOAD>",
                "image_url":""
              },
              {
                "content_type":"text",
                "title":"大安區",
                "payload":"<POSTBACK_PAYLOAD>",
                "image_url":""
              },
              {
                "content_type":"text",
                "title":"萬華區",
                "payload":"<POSTBACK_PAYLOAD>",
                "image_url":""
              },
              {
                "content_type":"text",
                "title":"信義區",
                "payload":"<POSTBACK_PAYLOAD>",
                "image_url":""
              },
              {
                "content_type":"text",
                "title":"士林區",
                "payload":"<POSTBACK_PAYLOAD>",
                "image_url":""
              },
              {
                "content_type":"text",
                "title":"北投區",
                "payload":"<POSTBACK_PAYLOAD>",
                "image_url":""
              },
              {
                "content_type":"text",
                "title":"內湖區",
                "payload":"<POSTBACK_PAYLOAD>",
                "image_url":""
              },
              {
                "content_type":"text",
                "title":"南港區",
                "payload":"<POSTBACK_PAYLOAD>",
                "image_url":""
              }
            ]
          }    
    })
    call_send_api(data)

def send_button_message(recipient_id):
    
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment": {
                "type":"template",
                "payload":{
                    "template_type":"button",
                    "text":"想吃什麼種類",
                    "buttons":[
                    {
                        "type":"postback",
                        "title":"中式",
                        "payload":"中式"
                    },
                    {
                        "type":"postback",
                        "title":"美式",
                        "payload":"美式"
                    }
                    ]
                }
            }
        }
    })

    log("sending button to {recipient}: ".format(recipient=recipient_id))

    call_send_api(data)

def send_button_category(recipient_id):
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment": {
                "type":"template",
                "payload":{
                    "template_type":"button",
                    "text":"What category of bot?",
                    "buttons":[
                    {
                        "type":"postback",
                        "title":"Games",
                        "payload":"Games"
                    },
                    {
                        "type":"postback",
                        "title":"Health",
                        "payload":"Health"
                    },
                    {
                        "type":"postback",
                        "title":"Community",
                        "payload":"Community"
                    }
                    ]
                }
            }
        }
    })

    log("sending category button to {recipient}: ".format(recipient=recipient_id))

    call_send_api(data)

def send_button_community(recipient_id):
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment": {
                "type":"template",
                "payload":{
                    "template_type":"button",
                    "text":"Here is the list of community bots",
                    "buttons":[
                    {
                        "type":"web_url",
                        "url":"https://m.me/Comrades_nature",
                        "title":"Comrades_nature"
                    },
                    {
                        "type":"web_url",
                        "url":"https://m.me/Botstore",
                        "title":"Botstore"
                    },
                    {
                        "type":"web_url",
                        "title":"Ggflaskbot",
                        "url":"https://m.me/Ggflaskbot"
                    }
                    ]
                }
            }
        }
    })

    log("sending community button to {recipient}: ".format(recipient=recipient_id))

    call_send_api(data)

def send_generic_message(recipient_id):
    
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": [{
                        "title": "Comrades_nature",
                        "subtitle": "A bot to help comrades solve their nature problems",
                        "item_url": "https://m.me/Comrades_nature",               
                        "image_url": "",
                        "buttons": [{
                            "type": "web_url",
                            "url": "https://m.me/Comrades_nature",
                            "title": "Visit the bot"
                        }],
                    }, {
                        "title": "Botstore",
                        "subtitle": "Find all bots on facebook",
                        "item_url": "https://m.me/Botstore",               
                        "image_url": "",
                        "buttons": [{
                            "type": "web_url",
                            "url": "https://m.me/Botstore",
                            "title": "Visit the bot"
                        }]
                    }]
                }
            }
        }
    })

    log("sending template with choices to {recipient}: ".format(recipient=recipient_id))

    call_send_api(data)

def send_generic_category(recipient_id):
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": [{
                        "title": "Bots category",
                        "subtitle": "Please select one of the categories",
                        "buttons": [{
                            "type": "postback",
                            "title":"Community",
                            "payload":"Community"
                        },{
                            "type": "postback",
                            "title": "Games",
                            "payload": "Games"
                        },{
                            "type": "postback",
                            "title": "Health",
                            "payload": "Health"
                        }
                        ]
                    }]
                }
            }
        }
    })

    log("sending template with choices to {recipient}: ".format(recipient=recipient_id))

    call_send_api(data)

def send_chinese_category(recipient_id):
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": [{
                        "title": "人和園雲南菜",
                        "subtitle": "雲南菜",
                        "item_url": "http://www.ohmyfood.com.tw/restaurant/16257/",               
                        "image_url": "http://www.ohmyfood.com.tw/imgHosting/post/556700.jpg",
                        "buttons": [{
                            "type": "web_url",
                            "url": "http://www.ohmyfood.com.tw/restaurant/16257/",
                            "title": "瀏覽網站"
                        }],
                    }, {
                        "title": "版納傣味",
                        "subtitle": "雲南菜",
                        "item_url": "http://www.ohmyfood.com.tw/restaurant/43233/",               
                        "image_url": "http://www.ohmyfood.com.tw/imgHosting/post/29828.jpg",
                        "buttons": [{
                            "type": "web_url",
                            "url": "http://www.ohmyfood.com.tw/restaurant/43233/",
                            "title": "瀏覽網站"
                        }]
                    }]
                }
            }
        }
    })

    log("sending template with choices to {recipient}: ".format(recipient=recipient_id))

    call_send_api(data)

def send_western_category(recipient_id):
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": [{
                        "title": "Riposo 驛",
                        "subtitle": "美式/早午餐",
                        "item_url": "http://www.ohmyfood.com.tw/restaurant/13594/",               
                        "image_url": "http://www.ohmyfood.com.tw/img/restaurant/defHeader_14_3.jpg",
                        "buttons": [{
                            "type": "web_url",
                            "url": "http://www.ohmyfood.com.tw/restaurant/13594/",
                            "title": "瀏覽網站"
                        }],
                    }, {
                        "title": "Poco Micaela 小米卡美國牛肉&比利時啤酒餐廳",
                        "subtitle": "美式/早午餐",
                        "item_url": "http://www.ohmyfood.com.tw/restaurant/13366/",               
                        "image_url": "http://www.ohmyfood.com.tw/imgHosting/restaurant/4437.jpg",
                        "buttons": [{
                            "type": "web_url",
                            "url": "http://www.ohmyfood.com.tw/restaurant/13366/",
                            "title": "瀏覽網站"
                        }]
                    }]
                }
            }
        }
    })

    log("sending template with choices to {recipient}: ".format(recipient=recipient_id))

    call_send_api(data)

def received_postback(event):

    sender_id = event["sender"]["id"]        # the facebook ID of the person sending you the message
    recipient_id = event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID

    # The payload param is a developer-defined field which is set in a postback
    # button for Structured Messages
    payload = event["postback"]["payload"]
    user_details_url = "https://graph.facebook.com/v2.6/%s"%sender_id
    user_details_params = {'fields':'first_name,last_name,profile_pic', 'access_token':'EAACTjBJFZAeUBABF4Vy4CLiostamaLSxPVW8MfVBehUM3xJTLodZAsU7X2jVEbswVubeZC2r4i7gin3sMg9BMejjvLiB4lDAKZC7hHxO3PADJkNZBynCe3q1pwmQjEwRxmso1fvsgHxxApN0ThBceA9qjtVQxydkJdDHhDJx5qoWrhZArnua1t'}
    user_details = requests.get(user_details_url, user_details_params).json()

    if payload == 'Get Started':
        # Get Started button was pressed
        send_message(sender_id, "Welcome {} {} to bot store. You will find all facebook bots here.".format(user_details['first_name'], user_details['last_name']))
        send_generic_category(sender_id)
    elif payload == 'Find a bot':
        send_button_category(sender_id)
    elif payload == 'Community':
        send_generic_message(sender_id)
    elif payload == 'Games':
        send_button_category(sender_id)
    elif payload == '中式':
        send_chinese_category(sender_id)
    elif payload == '美式':
        send_western_category(sender_id)

    else:
        # Notify sender that postback was successful
        send_message(sender_id, "Postback called")

    
def call_send_api(data):
    params = {
        "access_token": "EAACTjBJFZAeUBABF4Vy4CLiostamaLSxPVW8MfVBehUM3xJTLodZAsU7X2jVEbswVubeZC2r4i7gin3sMg9BMejjvLiB4lDAKZC7hHxO3PADJkNZBynCe3q1pwmQjEwRxmso1fvsgHxxApN0ThBceA9qjtVQxydkJdDHhDJx5qoWrhZArnua1t"
    }
    headers = {
        "Content-Type": "application/json"
    }
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)
    
def query_dialogflow(event, request):
    read = request.getresponse().read()
    response = json.loads(read)
    print("api.ai response :", read.decode("utf-8"))
    result = response['result']
    action = result.get('action')
    actionIncomplete = result.get('actionIncomplete', False)

    if action is not None:
        if action == "input.location":
            if not actionIncomplete:
                food_type = json.loads(getEntities("food_type"))
                entries = food_type['entries']
                actions = []
                for entitie in entries:
                    actions.append(entitie['value'])
                    if len(actions) >= 3:
                        break

                send_message(request.session_id, response['result']['fulfillment']['speech'])
            else:
                send_message(request.session_id, response['result']['fulfillment']['speech'])
        elif action == "input.food_type":
            if not actionIncomplete:
                price = json.loads(getEntities("price"))
                entries = price['entries']
                actions = []
                for entitie in entries:
                    actions.append(entitie['value'])
                    if len(actions) >= 4:
                        break
                send_message(request.session_id, response['result']['fulfillment']['speech'])
            else:
                send_message(request.session_id, response['result']['fulfillment']['speech'])

        else:
            send_message(request.session_id, response['result']['fulfillment']['speech'])


def getEntities(entitieName):
    url = "https://api.dialogflow.com/v1/entities/" + entitieName
    headers = {'Authorization': 'Bearer ' + '9cdd438af6454091b0429448134a0b2a', 'Content-Type': 'application/json'}
    response = requests.get(url, headers=headers)
    print(response.content.decode("utf-8"))
    return response.content

def log(message):  # simple wrapper for logging to stdout on heroku
    print (str(message))
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)