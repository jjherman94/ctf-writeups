import re
import socket
import time

BUFSIZE = 4096

def recv(client):    
    data = ''
    while True:
        r = client.recv(BUFSIZE)
        data += r
        if len(r) < BUFSIZE:
            break
    return data

def recon(max_streak=15, wait_duration=5):
    challenges = []
    streak = 0
    while True:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect( ('200.136.213.148', 5000) )
        c = recv(client)
        client.close()
        print c
        if c in challenges:
            streak += 1
        else:
            challenges.append(c)
            streak = 0
        if streak >= max_streak:
            break
        print '===============streak=%d==============' % streak
        time.sleep(wait_duration)
    return challenges

# challenges = recon()
# print 'Found %d challenges:\n%s' % (len(challenges), challenges)
challenges = ['Type the regex that capture: "Chips" and "code.", and it is only allowed the letter "c" (insensitive)", with max. "15" chars: ', 'Type the regex that capture: "All "Open\'s", without using that word or [Ope-], and no more than one point", with max. "11" chars: ', 'Type the regex that capture: "<knowing the truth. >, without using "line break"", with max. "8" chars: ', 'Type the regex that capture: "(BONUS) What\'s the name of the big american television channel (current days) that matchs with this regex: .(.)\\1", with max. "x" chars: ', 'Type the regex that capture: "FLY until... Fly", without wildcards or the word "fly" and using backreference", with max. "14" chars: ', 'Type the regex that capture: "the follow words: "unfolds", "within" (just one time), "makes", "inclines" and "shows" (just one time), without using hyphen, a sequence of letters (two or more) or the words itself", with max. "38" chars: ', 'Type the regex that capture: "the only word that repeat itself in the same word, using a group called "a" (and use it!), and the group expression must have a maximum of 3 chars, without using wildcards, plus signal, the word itself or letters different than [Pa]", with max. "16" chars: ', 'Type the regex that capture: "from "Drivin" until the end of phrase, without using any letter, single quotes or wildcards, and capturing "Drivin\'" in a group, and "blue." in another", with max. "16" chars: ']

responses = {
    challenges[0]: r'c.{3,4},.+ (.+)',
    challenges[1]: r'(?im)^o.\wn',
    challenges[2]: r'<[^>]*>',
    challenges[3]: r'cnn',
    challenges[4]: r'(?i)(F..).+\1',
    challenges[5]: r'[i|n][t|d] ([^F]...[i|l|s]\w{0,3})',
    challenges[6]: r'(?P<a>...)(?P=a)',
    challenges[7]: r'(.{7}).+-(.+)$'
}

def answer(responses):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect( ('200.136.213.148', 5000) )
    while True:
        q = recv(client).lstrip()
        if q in responses:
            print 'Received: %s' % q
            print 'Sending: %s' % responses[q]
            client.send(responses[q]+'\n')
            print recv(client)
        else:
            print q
            client.close()
            break
        print '==========================='

answer(responses)
