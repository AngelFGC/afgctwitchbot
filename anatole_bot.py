# -*- coding: utf-8 -*-
"""
Created on Fri Dec  7 11:21:44 2018

@author: AnatoleSerial
"""

# https://github.com/joshuaskelly/twitch-observer
from twitchobserver import Observer, ChatEventType
import sys
import time
import queue

timeout = 0

running = True
isMod = False

msg_q = queue.Queue()

def on_message(event):
    print(str(event))

def setup_observer(o):
    timeout = 30/100 if isMod else 30/20
    
    @o.on_event(ChatEventType.TWITCHCHATMESSAGE)
    def handle_message(e):
        global running
        global timeout
        
        # Disconnect the bot.
        # Only available to users with moderation privileges.
        if e.message == "!goodbye":
            if any(('broadcaster' in x or
                    'mod' in x or
                    'admin' in x or
                    'global_mod' in x or
                    'staff' in x for x in 
                    e.tags['badges'].split(","))):
                o.send_message('Goodbye!', e.channel)
                o.leave_channel(e.channel)
                running = False
                print("\tBot Stopped.")
        elif e.message.startswith("!"):
            on_message(e)

def run_bot(username, token, channel):
    print("Bot Starting...")
    global timeout
    with Observer(username, 'oauth:' + token) as o:
        o.join_channel(channel)
        #o.send_message('Hello! This is MrDestructoid AnatoleBot MrDestructoid', channel)
        
        setup_observer(o)
        
        try:
            while running:
                if not msg_q.empty():
                    m = msg_q.get()
                    o.send_message(m, channel)
                    time.sleep(timeout)
                    
        except KeyboardInterrupt:
            o.send_message('MrDestructoid Je suis morte!', channel)
            o.leave_channel(channel)
            print("\tBot Stopped.")
            sys.exit(1)
            
def main():
    print("Startup?")
    if len(sys.argv) < 4:
        print("Usage: anatole_bot <username> <oauth_token> <channel>")
        sys.exit(1)
    global isMod
    username  = sys.argv[1]
    token     = sys.argv[2]
    channel   = sys.argv[3]
    if len(sys.argv) > 4:
        isMod = bool(sys.argv[4])
    
    run_bot(username, token, channel)
    
    

if __name__ == "__main__":
    main()