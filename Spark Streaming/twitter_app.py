import socket
import sys
import requests
import requests_oauthlib
import json

ACCESS_TOKEN = '*****'
ACCESS_SECRET = '*****'
CONSUMER_KEY = '*****'
CONSUMER_SECRET = '*****'

my_auth = requests_oauthlib.OAuth1(CONSUMER_KEY, CONSUMER_SECRET,ACCESS_TOKEN,
ACCESS_SECRET)

def get_tweets():
    url = 'https://stream.twitter.com/1.1/statuses/filter.json'
    query_data = [('language', 'en'),('locations', '-75, 39.88, -72.60, 41.50'),('track','Verizon')]
    query_url = url + '?' + '&'.join([str(t[0]) + '=' + str(t[1]) for t in query_data])
    response = requests.get(query_url, auth=my_auth, stream=True)
    print(query_url, response)
    return response

def send_tweets_to_spark(http_resp, tcp_connection):
    for line in http_resp.iter_lines():
        try:
            full_tweet = json.loads(line)
            user_id = full_tweet['user']['screen_name']
            tweet_text = full_tweet['text']
            data = (user_id + " " + tweet_text)
            data = data.encode('utf-8')
            print("User ID + Tweet:")
            print(data)
            print ("------------------------------------------")
            tcp_connection.send(data + '\n')
        except:
            e = sys.exc_info()[0]
            print("Error: %s" % e)

TCP_IP = "localhost"
TCP_PORT = 9595
conn = None
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
print("Waiting for TCP connection...")
conn, addr = s.accept()
print("Connected... Starting getting tweets.")
resp = get_tweets()
send_tweets_to_spark(resp, conn)
