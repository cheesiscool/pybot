from slackclient import SlackClient
import re, time
from json import loads
print("Ready to connect to Slack.")

token = "xoxb-17040427299-bEqyZsrwKAusn6rpLmc7jeln"
sc = SlackClient(token)

def createlists():
    #Get the user list
    userlist = loads(str(sc.api_call("users.list").decode("utf-8")))['members']
    #Parse for user IDs
    for i in range(0, len(userlist)):
        userID = userlist[i]["id"]
        userIDs.append(userID)
        #Find the user's name
        try:
            #Find the user's username if they haven't set a name
            userName = userlist[i]["profile"]["first_name"]
        except:
            userName = userlist[i]["name"]
        userNames.append(userName)
        if userName == "pybot":
            #Remove the bot from the user list
            userIDs.pop()
            userNames.pop()
    for n in range(0, len(userIDs)):
        #Find the DM channels for each user
        openstring = str((sc.api_call("im.open", user=userIDs[n])))
        searchObj = re.search(r'"id":"(.*?)"', openstring)
        userchannel = searchObj.group(1)
        userchannels.append(userchannel)

def send(msgchannel, msgtext):
    sc.api_call("chat.postMessage", as_user="true:", channel=msgchannel, text=msgtext)

def debug(msg):
    send("#pybotdebug", msg)

userIDs = []
userNames = []
userchannels = []

if sc.rtm_connect():
    print("Connected to Slack.")
    createlists()
    debug("Bot started.")
    while True:
        #Get new information from the channel
        channelstatus = sc.rtm_read()
        if (channelstatus == []):
            #Discard empty channel status
            print("No activity, doing nothing.")
        else:
            #Do literally everything
            #Find the status type
            statustype = channelstatus[0]["type"]
            if statustype:
                statustype = str(statustype)
                if statustype == "hello":
                    #Filter out hello message from server
                    print("Hello message recieved from server.")
                else:
                    #Find the user ID of the active user
                    try:
                        userID = channelstatus[0]["user"]
                    except:
                        debug("Unknown status! Here are the details:\n" + str(channelstatus))
                    if not (userID == "U0H16CK8T" or userID == "USLACKBOT"):
                        #Only run if the user is not pybot or Slackbot
                        if statustype == "presence_change":
                            #Handle presence changes
                            presencestatus = channelstatus[0]["presence"]
                            if userID in userIDs:
                                userName = userNames[userIDs.index(userID)]
                                print(userName + " is now " + presencestatus + ".")
                        elif statustype == "user_typing":
                            #Handle typing
                            if userID in userIDs:
                                userName = userNames[userIDs.index(userID)]
                                print(userName + " is typing.")
                            else:
                                debug("User not found in list! Here are the details:\n" + str(channelstatus))
                        elif statustype == "message":
                            if userID in userIDs:
                                #Find where the user is in the lists
                                userpos = userIDs.index(userID)
                                #Find the user's name and channel
                                userName = userNames[userpos]
                                userchannel = userchannels[userpos]
                                #This regex doesn't work if the message contains an apostrophe.
                                message = channelstatus[0]['text']
                                print(userName + " says: " + message)
                                if channelstatus[0]['channel'] == userchannel:
                                    if message.lower()[:5] == "hello":
                                        send(userchannel, "Hi!")
                                        
                            else:
                                debug("User not found in list! Here are the details:\n" + str(channelstatus) + "\nNote: User may have joined between bot restarts. Problem will be fixed next time bot restarts.")
                        else:
                            debug("Unimplemented status! Here are the details:\n" + str(channelstatus))
                    else:
                        print("Pybot and/or Slackbot did something.")
            else:
                debug("This error should never happen. Here are the details:\n" + str(channelstatus))
        time.sleep(1)
#'text': (["'])(.*?)\1
#print(sc.api_call("im.open", user=userID))
#'text': 'This is my legit "test" \'message\' with "lots" of \'quotation marks\''}]