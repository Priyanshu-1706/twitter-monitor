import requests
import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAM9K%2BQEAAAAA5mR2g2yT8Bysl%2FPmoALOLuku0ec%3DZwzxPAHGuohCm0DZQd26SxvA1ATe3t6ccXbUObzpaxOnDukGIy"
WEBHOOK_URL = "https://priyanshuagr-123.app.n8n.cloud/webhook/4b57f212-dcdd-4850-acde-16c41b668236"

ACCOUNTS = [
    "narendramodi",
    "AmitShah",
    "rajnathsingh",
    "PiyushGoyal",
    "rsprasad",
    "smritiirani",
    "nsitharaman",
    "DrSJaishankar",
    "nitin_gadkari",
    "ianuragthakur",
    "RahulGandhi",
    "priyankagandhi",
    "OfficeOfRG",
    "ArvindKejriwal",
    "MamataOfficial",
    "uddhavthackeray",
    "hd_kumaraswamy",
    "yadavakhilesh",
    "SiddaramaiahINC",
    "shahfaesal",
    "vijai_singapuram",
    "Sanjay_Dixit",
    "swamy39",
    "sardanarohit",
    "RubikaCLiaquat",
    "anjanaomkashyap",
    "navikakumar",
    "bdutt",
    "sardesairajdeep",
    "ShekharGupta",
    "PriyanshuAgr17",
]

STREAM_URL = "https://api.twitter.com/2/tweets/search/stream"
RULES_URL = "https://api.twitter.com/2/tweets/search/stream/rules"

HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "Content-Type": "application/json"
}

# == RENDER KE LIYE DUMMY SERVER ==
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Twitter Monitor Running!")
    def log_message(self, format, *args):
        pass

def run_server():
    server = HTTPServer(("0.0.0.0", 8080), Handler)
    server.serve_forever()

def delete_old_rules():
    try:
        response = requests.get(RULES_URL, headers=HEADERS)
        rules = response.json().get("data", [])
        if rules:
            ids = [rule["id"] for rule in rules]
            requests.post(RULES_URL, headers=HEADERS,
                json={"delete": {"ids": ids}})
        print("✅ Purane rules delete ho gaye")
    except Exception as e:
        print("❌ Error:", e)

def add_rules():
    try:
        rule = " OR ".join([f"from:{acc}" for acc in ACCOUNTS])
        requests.post(RULES_URL, headers=HEADERS,
            json={"add": [{"value": rule}]})
        print("✅ Accounts add ho gaye")
    except Exception as e:
        print("❌ Error:", e)

def send_to_webhook(data):
    try:
        requests.post(WEBHOOK_URL, json=data, timeout=10)
        print("✅ n8n ko bhej diya!")
    except Exception as e:
        print("❌ Webhook error:", e)

def start_stream():
    print("👀 Twitter sun raha hoon...")
    while True:
        try:
            response = requests.get(
                STREAM_URL,
                headers=HEADERS,
                stream=True,
                params={
                    "tweet.fields": "created_at,text",
                    "expansions": "author_id",
                    "user.fields": "username,name"
                },
                timeout=30
            )
            for line in response.iter_lines():
                if line:
                    tweet = json.loads(line)
                    try:
                        username = tweet["includes"]["users"][0]["username"]
                        name = tweet["includes"]["users"][0]["name"]
                        text = tweet["data"]["text"]
                        tweet_id = tweet["data"]["id"]
                        print(f"🚨 @{username}: {text}")
                        send_to_webhook({
                            "username": username,
                            "name": name,
                            "text": text,
                            "link": f"https://x.com/{username}/status/{tweet_id}"
                        })
                    except:
                        pass
        except Exception as e:
            print(f"❌ Error: {e}")
            print("🔄 5 sec mein restart...")
            time.sleep(5)

if __name__ == "__main__":
    print("🚀 Twitter Monitor Shuru!")
    # Server alag thread mein chalao
    t = threading.Thread(target=run_server)
    t.daemon = True
    t.start()
    # Stream shuru karo
    delete_old_rules()
    add_rules()
    start_stream()
