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
import re
import random
import operator
import math

"""
GLOBALS
"""
timeout = 0

running = True
isMod = False

msg_q = queue.Queue()

dice_re = re.compile(r"(\d*)D(\d*)(?:([<>+\/*-])(\d+))?", flags=re.IGNORECASE)
dice_ops = {"+":operator.add, "/":operator.truediv, 
            "*":operator.mul, "-":operator.sub}

vote_end = -1
vote_choices = []
vote_counts = []
voters = set()

"""
COMMAND METHODS
"""
def roll_dice(diceSpec):
    m = dice_re.match(diceSpec)
    reply = ""
    if m:
        g = m.groups()
        n = int(g[0])
        k = int(g[1])
        mod = g[2]
        x = int(g[3]) if g[3] is not None else 0
        
        rolls = []
        for i in range(n):
            rolls.append(random.randint(1, k+1))
        
        if mod is None:
            # Simple sum style roll
            s = sum(rolls)
            reply = "{0} => ({1}) = {2}".format(diceSpec, 
                     "+".join((str(r) for r in rolls)), s)
        elif mod == ">" or mod == "<":
            # Success-count style roll
            count = sum(i>=x if mod==">" else i<=x for i in rolls)
            reply = "{0} => [{1}] ({2} successes, diff {3})".format(
                    diceSpec, " ".join((str(r) for r in rolls)), count, x)
        elif mod in dice_ops:
            # Sum style roll with additional operation
            op = dice_ops[mod]
            s = sum(rolls)
            count = op(s, x)
            reply = "{0} => ({1}){2}{3} = {4}".format(diceSpec, 
                     "+".join((str(r) for r in rolls)), mod, x, count)
        else:
            # If RE is correct, this will never happen.
            reply = "Unrecognized Dice Pattern: {0}".format(diceSpec)
    else:
        reply = "Unrecognized Dice Pattern: {0}".format(diceSpec)
    return reply

def bop(source, target):
    ac_mod = [-2, -1, 0, 1, 2]
    things = ["large trout", "baseball bat", "wet noodle", "body pillow"]
    source_mod = ac_mod[sum(bytearray(source, 'utf8')) % 5] + random.choice(ac_mod)
    target_ac = 10 + ac_mod[sum(bytearray(target, 'utf8')) % 5] + random.choice(ac_mod)
    mod_text = ("" if source_mod == 0 else str(source_mod) + " " 
                   if source_mod < 0 else "+" + str(source_mod) + " ")
    target_name = "themselves" if source.lower() == target.lower() else target
    action_text = "{0} tries to bop {1} with a {2}{3}!".format(
                  source, target_name, mod_text, random.choice(things))
    
    roll_res = random.randint(1, 21)
    result_text = ""
    
    if roll_res == 20:
        # Critical hit
        result_text = "CRITICAL HIT! {0} takes {1:d} damage PogChamp !".format(
                      target, int(math.exp(random.randint(17,24))))
    elif roll_res == 1:
        # Critical miss
        result_text = "CRITICAL FAILURE! {0} hit their fkzDeezNuts for {1:d} damage NotLikeThis !".format(
                      source, int(math.exp(random.randint(17,24))))
    elif roll_res + source_mod >= target_ac:
        # Normal hit
        result_text = "{0} hits {1} for {2:d} damage!".format(
                      source, target_name, int(math.exp(random.randint(1,10))))
    else:
        # Normal miss
        result_text = "{0} misses! Boohoo!".format(source)
    
    return "{0} {1}".format(action_text, result_text)

def start_vote(choices):
    if len(choices) < 3:
        return "You need more options to call for a vote!"
    global vote_end
    global vote_choices
    global vote_counts
    
    duration = float(choices[0])
    vote_choices = choices[1:]
    vote_counts = [0] * len(vote_choices)
    
    choices_string = ", ".join(["!{0}: {1}".format(str(x+1), y) for x,y in 
                                zip(range(len(vote_choices)), vote_choices)])
    
    vote_text = ("Voting has started! Type ! + a number to vote! " +
                 "Only your first vote counts, so choose wisely. " +
                 "Here are the choices: " + choices_string + ". " +
                 "Voting ends in {0:.2f} minutes, so get going!".format(duration))
    vote_end = time.time() + duration*60
    
    return vote_text    
    
def process_vote(vote, voter):
    v_num = 0
    try:
        v_num = int(vote) - 1
    except:
        return

    global vote_counts
    global voters
    if (v_num >= 0 or v_num < len(vote_counts)) and voter not in voters:
        vote_counts[v_num] += 1
        voters.add(voter)

def end_vote():
    #msg_q.put(reply)
    global vote_end
    global voters
    global vote_choices
    global vote_counts
    # Collect Votes
    max_v, max_i = max((v,i) for i,v in enumerate(vote_counts))
    vote_str = ", ".join("{0} = {1}".format(x,y) 
                         for x,y in zip(vote_choices, vote_counts))
    vote_wins = vote_choices[max_i] + " wins!"
    ret_str = ("Voting has ended! The results are: " +
               vote_str + ". " + vote_wins)
    msg_q.put(ret_str)
    # Clean up
    vote_end = -1
    voters.clear()
    vote_choices.clear()
    vote_counts.clear()

def managed_timed_events():
    global vote_end
    c_time = time.time()
    if vote_end != -1 and c_time >= vote_end:
        end_vote()

"""
CHAT CONNECTION & INTERACTION METHODS
"""
def is_privileged(badges):
    return ('broadcaster' in badges 
            or 'mod' in badges 
            or 'admin' in badges 
            or 'staff' in badges)

def on_message(event):
    uname = event.tags['display-name']
    # Will be used for some commands.
    privileged = is_privileged(event.tags['badges'])
    
    full_cmd = event.message[1:].split(" ")
    main_cmd = full_cmd[0]
    parm_cmd = full_cmd[1:]
    
    print("{0}: {1}".format(uname, main_cmd))
    
    reply = None
    if main_cmd == "roll":
        p = "".join(parm_cmd)
        roll = roll_dice(p)
        if "Unrecognized" in roll:
            reply = "Unknown dice roll: {0}".format(p)
        else:
            reply = "{0} rolled {1}".format(uname, roll)
    elif main_cmd == "bop":
        target = parm_cmd[0] if len(parm_cmd) != 0 else uname
        reply = bop(uname, target)
    elif main_cmd == "vote":
        if not privileged:
            reply = "You cannot call for a vote! Only mods or higher can call for a vote."
        else:
            reply = start_vote(parm_cmd)
    elif main_cmd == "about":
        reply = ("I am AnatoleBot! For info + source code + commands " 
                 + "+ updates, check https://github.com/AngelFGC/fko-waifubot")
    else:
        # TODO: manage votes
        global vote_end
        if vote_end != -1:
            voter = event.tags['display-name']
            process_vote(main_cmd, voter)
            return
        reply = "Unknown command: {0}".format(main_cmd)
    
    if reply is not None:
        msg_q.put(reply)

def setup_observer(o):
    global timeout
    timeout = 30/100 if isMod else 30/20
    
    @o.on_event(ChatEventType.TWITCHCHATMESSAGE)
    def handle_message(e):
        global running
        global timeout
        
        # Disconnect the bot.
        # Only available to users with moderation privileges.
        if e.message == "!goodbye":
            if (is_privileged(e.tags['badges']) or 
                e.tags['display-name'] == "AnatoleSerial"):
                o.send_message('Goodbye!', e.channel)
                o.leave_channel(e.channel)
                running = False
                print("\tBot Stopped.")
        elif e.message.startswith("!"):
            on_message(e)

def run_bot(username, token, channel):
    print("Bot Starting...")
    global timeout
    global running
    with Observer(username, 'oauth:' + token) as o:
        o.join_channel(channel)
        
        setup_observer(o)
        
        try:
            while running:
                if not msg_q.empty():
                    m = msg_q.get()
                    o.send_message(m, channel)
                    time.sleep(timeout)
                managed_timed_events()
                    
        except KeyboardInterrupt:
            o.send_message('MrDestructoid Je suis morte!', channel)
            o.leave_channel(channel)
            print("\tBot Stopped.")
            sys.exit(1)
"""
MAIN METHOD
"""
def main():
    print("Startup?")
    if len(sys.argv) < 4:
        print("Usage: python anatole_bot.py <username> <oauth_token> <channel> <is_bot_mod>")
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