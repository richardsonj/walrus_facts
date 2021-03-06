import os
import time
from slackclient import SlackClient
from pprint import pprint
import random
import boto3

ssm_client = boto3.client('ssm', region_name='us-east-2')
ssm_response = ssm_client.get_parameters(Names=["walrus_facts_api_key", "walrus_facts_bot_id"],WithDecryption=True)

API_KEY = ""
BOT_ID = ""

for parameter in ssm_response["Parameters"]:
    if parameter["Name"] == "walrus_facts_api_key":
        API_KEY = parameter["Value"]
    elif parameter["Name"] == "walrus_facts_bot_id":
        BOT_ID = parameter["Value"]

# constants
AT_BOT = "<@" + BOT_ID
WALRUS_USER_ID = 'U1M01JH4M'

walrus_facts = ['Walruses are dumb',
                'Walruses can\'t feel love',
                'Walruses are a major contributor to the extinction of polar bears',
                'Myth Buster Jamie Hyneman is not actually a walrus. However, his parents were both killed by walruses, so those jokes hurt more than anyone knows',
                'All walruses are racist against white people',
                'The walrus\'s favorite software design pattern is singleton',
                'When a young walrus comes of age, it must either kill a baby seal or face banishment',
                'A group of walruses is called an "orgy"',
                'The walrus is Hitler\'s spirit animal',
                'Walruses aren\'t born with tusks. Their tusks are actually aquired through the illegal ivory trade, and originated from murdered elephants',
                'Evidence suggests that President Kennedy was actually assassinated by a walrus, who later killed Lee Harvey Oswald to cover it up',
                'Historians believe Joseph Stalin may have been a walrus wearing a Super Mario costume',
                'Walruses all voted for Trump.',
                'All walruses are conceived from the left nut, making them all left nut sons of bitches.',
                'Why won\'t you love me, Joseph?',
                'Joseph, I am your father.',
                'Walruses are fat bitches',
                'Cold case investigators have uncovered evidence that a massive walrus human trafficking conspirancy was responsible for 90% of unsolved missing persons cases in the 1970s. It is believed that the bodies were never found, because they are kept in secret underwater "bang caves" that have yet to be discovered']

fact_weights = [1]*len(walrus_facts)

walrus_ifs = []
walrus_thens = []

weight_multiplier = .1

slack_client = SlackClient(API_KEY)

def create_ranges():
    ranges = [0]*len(walrus_facts)
    last_range = 1
    for x in range(len(walrus_facts)):
        ranges[x] = last_range - fact_weights[x]/sum(fact_weights)
        last_range = ranges[x]
    ranges[len(walrus_facts)-1] = 0
    return ranges

def get_index_from_ranges(ranges):
    max_value = sum(fact_weights)
    number = random.random()
    for x in range(len(walrus_facts)):
        if number >= ranges[x]:
            return x
    
def normalize_fact_weights():
    for weight in fact_weights:
        if weight >= 1:
            return
    for x in range(len(fact_weights)):
        fact_weights[x] /= weight_multiplier

def get_fact_index():
    ranges = create_ranges()
    index = get_index_from_ranges(ranges)
    fact_weights[index] *= weight_multiplier
    normalize_fact_weights()
    return index

def get_walrus_fact_text():
    return walrus_facts[get_fact_index()]

def post_walrus_fact(channel, contract):
    response = get_walrus_fact_text()
    walrus_fact_number = random.randint(1, 1000)
    while walrus_fact_number == 3:
        walrus_fact_number = random.randint(1, 1000)
    response = "Walrus Fact #" + str(walrus_fact_number) + ": " + response
    if contract:
        response = response.replace('a', "'").replace('e', "'").replace('i', "'").replace('o', "'").replace('u', "'")
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)

def post_full_walrus_fact(channel):
    post_walrus_fact(channel, False)

def post_contracted_walrus_fact(channel):
    post_walrus_fact(channel, True)

def post_not_jacob(channel):
    slack_client.api_call("chat.postMessage", channel=channel,
                          text='Disclaimer: Jacob Richardson is not obligated to attend game night when other users post that emoji', as_user=True)

def post_die(channel):
    slack_client.api_call("chat.postMessage", channel=channel,
                          text='You\'ve gone and killed me! You\'re working for walrus, aren\'t you?', as_user=True)
    raise Exception('Kill command received')

def post_nice_try(channel):
    slack_client.api_call("chat.postMessage", channel=channel,
                          text='Nice try! Only <@U11K1E7MG> can kill me', as_user=True)
    

def get_request_handler(requests):
    handlers = []
    if requests and len(requests) > 0:
        for request in requests:
            if request and 'type' in request and request['type'] == 'message':
                if 'user' in request and request['user'] == WALRUS_USER_ID:
                    return post_full_walrus_fact

                contract = 'text' in request and 'contract' in request['text'].lower()
                if 'text' in request and AT_BOT in request['text'] \
                   and 'fact' in request['text'].lower():
                    if contract:
                        handlers.append(post_contracted_walrus_fact)
                    else:
                        handlers.append(post_full_walrus_fact)
                if 'text' in request and ':an-even-longer-emoji-name-for-jacob-richardson-agreeing-to-attend-game-night-because-joseph-is-dumb:' in request['text'] \
                   and 'user' in request and request['user'] != 'U11K1E7MG':
                    handlers.append(post_not_jacob)
                if 'text' in request and 'kill yourself' in request['text']:
                    if 'user' in request and request['user'] == 'U11K1E7MG':
                        handlers.append(post_die)
                    else:
                        handlers.append(post_nice_try)
    return handlers

def get_response_channel(requests):
    if requests and len(requests) > 0:
        for request in requests:
            if 'channel' in request:
                return request['channel']

if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("Walrus Facts connected and running!")
        while True:
            request = slack_client.rtm_read()
            handlers = get_request_handler(request)
            for handler in handlers:
                channel = get_response_channel(request)
                handler(channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
