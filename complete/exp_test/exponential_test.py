from concurrent.futures import ThreadPoolExecutor
import os
import requests
import time
import base64
from kubernetes import client
from flask import Flask, Response, jsonify, request
from prometheus_client import Gauge, start_http_server, generate_latest
import threading

app = Flask(__name__)

# the address that is reachable within the pod
server = f"https://{os.environ['KUBERNETES_SERVICE_HOST']}:{os.environ['KUBERNETES_SERVICE_PORT']}"
# server = "https://127.0.0.1:50357"
client_certificate_data = "LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURJVENDQWdtZ0F3SUJBZ0lJRVdpUjRjTXJTa0V3RFFZSktvWklodmNOQVFFTEJRQXdGVEVUTUJFR0ExVUUKQXhNS2EzVmlaWEp1WlhSbGN6QWVGdzB5TXpBNE1UY3hNek13TlRKYUZ3MHlOREE0TVRZeE16TXhNREJhTURReApGekFWQmdOVkJBb1REbk41YzNSbGJUcHRZWE4wWlhKek1Sa3dGd1lEVlFRREV4QnJkV0psY201bGRHVnpMV0ZrCmJXbHVNSUlCSWpBTkJna3Foa2lHOXcwQkFRRUZBQU9DQVE4QU1JSUJDZ0tDQVFFQTFpUnlDZjBhR0VOSTdHa1gKUjJYSStUbHBKWGk5TWM5WWxtOTFSTi9adVRzbG83L000NkxBZkprWTZ2UGltbktNYjI3N1FpbHczTVc5M2ZYTgpWdU0vRFdvamFtTWoxeUF6cWQvSURBQTVyNnZLZWZKdXdwbkx6N3MvalJDQzBHTVVzZnhPb2JubHR2VTh3MGhQCmhOL1R0S2wvbGVwUE5aYXJQTG9kM3o0alVLYklLaDVKL3VOZGMyNEpSei9MVWxHUDYvZ3B3cFFhcUkwSkdoZzUKKzF4YnpZSUpCRXlnV1pmTTNNS2xaUDJLdWNEVjAwL01tVFVUbXB0T1RuaFh5SFJnSnRzS29Gem5SOURNVitRSwppa0xJaERIYWFpOW5iK0Jta0I1U2FTZzlOd3VUZVdZajNaTXRlandTS21kT01KcUtyU2tRRlhpdGhlWnNUaXhFCjFoUW9Nd0lEQVFBQm8xWXdWREFPQmdOVkhROEJBZjhFQkFNQ0JhQXdFd1lEVlIwbEJBd3dDZ1lJS3dZQkJRVUgKQXdJd0RBWURWUjBUQVFIL0JBSXdBREFmQmdOVkhTTUVHREFXZ0JTdXZzaEhTU2YxQ0d2dEo4aXg1dVhCeDBqUAp5REFOQmdrcWhraUc5dzBCQVFzRkFBT0NBUUVBVFlocHMyU1dwUXBKNWZuZGowckRGMDZpK0UrSE1hYWVwWTVLCitwdTc0YVFML2gzLy9CVlQrczA2Zk44UHVRQU5pcCs2Z1pYZVk4TkxoY2dha252TlNGMnpqbllZSDEydmovWXMKZU1EVG5Xdzl5WjQxUklieHVSQUduUzA4MzdOZXhwWWhjL3Q1M25SelkzYVdTTVFZcTVQQldJMHhQNXNMc1VaTQpwYnA2cXBucEh1OG45WHdWNkErZi9rY0dXV09QelI5RGFUdld1WFpnWVRkRVBpV3YxOXh4ZGFjclFxcTNyblI4CmNOWHQvYnVRbWFZMWpEbGZqNmxSSmtoa05kNnltWWtMdHRPdG9MbHEwZmhvcjRiRlYzQUxaaHBDMmdXS2liMTUKblc5Q2RKeldaZVZadUNtdWhNZjhEdWxacEQxTkJqSVpoSmE4Y0tUK2ovSDBOci94Z0E9PQotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tCg=="
client_key_data = "LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQpNSUlFb3dJQkFBS0NBUUVBMWlSeUNmMGFHRU5JN0drWFIyWEkrVGxwSlhpOU1jOVlsbTkxUk4vWnVUc2xvNy9NCjQ2TEFmSmtZNnZQaW1uS01iMjc3UWlsdzNNVzkzZlhOVnVNL0RXb2phbU1qMXlBenFkL0lEQUE1cjZ2S2VmSnUKd3BuTHo3cy9qUkNDMEdNVXNmeE9vYm5sdHZVOHcwaFBoTi9UdEtsL2xlcFBOWmFyUExvZDN6NGpVS2JJS2g1SgovdU5kYzI0SlJ6L0xVbEdQNi9ncHdwUWFxSTBKR2hnNSsxeGJ6WUlKQkV5Z1daZk0zTUtsWlAyS3VjRFYwMC9NCm1UVVRtcHRPVG5oWHlIUmdKdHNLb0Z6blI5RE1WK1FLaWtMSWhESGFhaTluYitCbWtCNVNhU2c5Tnd1VGVXWWoKM1pNdGVqd1NLbWRPTUpxS3JTa1FGWGl0aGVac1RpeEUxaFFvTXdJREFRQUJBb0lCQUNRYVJ1T3FPVUVIN3Y1MApoVWt6UHR2TnN3MXZPcTV3SDZaVktqY3ZhanlSWFRvck52YlYxSS90RzhkWTBNWnJNNFFCK1BoaGxqYVNXLzFVCjJJYWlqMW5Lb0NmcWlQdFc0WDd0VElQQmNmaE5CVGprQjRwbGRYZ1RRSmFleHY4dEJTc3d0MjBLczFEU0xhbGEKd3BWTFN4ejFTcDVTdjRId1lmUStDSlUvbTZLWC9NT09pRDlubm9keGRveUpoYkZiYkhBMUVJeEVCYWU1TnRPagpFOWp3a1VHRldzemwyaWFrRnlXMndSZlRIMnZsTXdkcUpVSG1NK05Id0YzVUh2eWwxd3BrMVBKdVJpQXEyU0JVCnBsZ3V5NmJoVXBBb2tSMHdHN0lCSDc0Rkg0TEo3Q3lFWkJZWG9lVzBxTnZ2d2U1MFlvNEo2U2lDMEV1WWNBV1YKSDdhUjZkRUNnWUVBOEVTNE5HaDZjN0hWQW1keVM1TW16d3BNN041aTNXTUo3c2pSaG9CQjRDUloxQVBZcHFDZwpuVllTN0R5aFc0ZDk2VWVkalh6M0Rkazk3ckhTZnNabkIrdGN2WjB3ekJWVHQwa21UN05sc2c5eFMrYWpHK0k2CklkYkNlRm55L2lFamt5T3p6Z2hRcE04aDdibVg4YTBCd0NFT3Y2Q3RoaU9qNEJmbVVkNEZGWnNDZ1lFQTVDblAKdmVwaEZWWXZIb0hUVlJndWZReTZ1SVFxSnJ2RnVjQVpJM3RmTXdXMGc2SWRZODNudklwVGlVYXBLOFJPdy9BLwplT3JQbitvRExzZkJTT0EwbWQzQW9KUXBlYVlzczAwZVlKNy9xUlNOak9GL1ZrbFhNWTl0R0lWbUdVQjFaOTUvCjRacUNMa2E0QjQ3QS85VEFtS0Zja3hUOC92ZDZVMXFCeWdNcWJVa0NnWUE5VnAzY0swd1BtemV4SEcydVk0dkYKMFhCZ0RFb2JFTHlwYkRVcGJEYmxIUUtkd0xtZm1HUklwbi9BTlo1UCtxQW5YUFFZK2Uwc2FPaUp0blh4alg4aQpJM0VTcXoyWTdGenA3cy9NQ3hXTVJxcjY0SStGZjlTdGJPRkt6bFBka3VJOUh5RTVHU0JWWXRmYms4VDVtdHhXCmkxbnppL2FneHhxQUREbnRib3ZIdndLQmdCVEgzaHp0Q1BTWmllY2NhZlFaSkxyTSt3Q3RRTzJRTXAwTmF2eTUKVXQxaHlxUW1rc2l4UzBiM3prMzFlcGo2NHpXalh4U1RSbC9KUDRyMk5KdC9tQ3JmY0pqdmhhdUh3QkNBbUtDeQpPcFRhdzEydWVCdVN5SGRDR2V5ZTBjTEJCVEIxcW00UTFZU0RlbVZ0MGhRNisyT3JaclFhdUVROHBBNk5jcjdFCmRRdkpBb0dCQU4zRmpTcGMreHVOSGRtQ0NHQ1VBYlZpRjJ1WGxRTXNmM2swbnlJU3A2Z044VjFibzJqSkdmTXAKakp5a0hCd21rZTU5OUlBL2xMc2NuUUVKOVBkdFRpendWUExkYWJBTVR4NUZvYlJVWEZIV1FwbkZzUmw5cHM3WgpweWNnNURTVHhzZFBHQ00zRDJDLzJ6Z3NkWmZ4T0MvZHNXZDYvUjRnL3ZkZEkyVmZ1ZHV2Ci0tLS0tRU5EIFJTQSBQUklWQVRFIEtFWS0tLS0tCg=="
certificate_authority_data = "LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUMvakNDQWVhZ0F3SUJBZ0lCQURBTkJna3Foa2lHOXcwQkFRc0ZBREFWTVJNd0VRWURWUVFERXdwcmRXSmwKY201bGRHVnpNQjRYRFRJek1EZ3hOekV6TXpBMU1sb1hEVE16TURneE5ERXpNekExTWxvd0ZURVRNQkVHQTFVRQpBeE1LYTNWaVpYSnVaWFJsY3pDQ0FTSXdEUVlKS29aSWh2Y05BUUVCQlFBRGdnRVBBRENDQVFvQ2dnRUJBTUl1CmF5ck0wSzFDTm0yUTJ5NEYrZ2JwSC9mcVJ5NWdtZmFrMXJCWUZnNTV6VTNyVTFzRWVBd0U5RXhFZUlobUxTSWoKODVTdklibVp1cktrWFIzNkVUL0dlVGFmV2grUk1FdzR1d3pIOWVpcllKMitJbzVaMmlweDlwWUlSU1NyV0RpQgo2THlJUnpYMldRcW5tUlRRK3htUHQ3ZWphSUR0T3FGUUNzS2dGVnc4LzRLZEhYMlNqc0IvcnFVemNTLzNUVVRPCmlWUDR1N0V5K09wcklmdDBkN2RsNkN5cWFGS0lPWktZRzBoZG43Q3lmRTVWTGJpM2lqN3FBcFY4bUhYRTduQWIKbTRUekRBVDJ5Y004blZEdkU2cnlGQzJtSmhZVGdHSzNVYXg3dnZ6cDZ0VE9BZHQ0VXRrNlZ6ZU5pY2pFSjgrRQpWYkQ1QVR6a25TRE5tbSs0MVhNQ0F3RUFBYU5aTUZjd0RnWURWUjBQQVFIL0JBUURBZ0trTUE4R0ExVWRFd0VCCi93UUZNQU1CQWY4d0hRWURWUjBPQkJZRUZLNit5RWRKSi9VSWErMG55TEhtNWNISFNNL0lNQlVHQTFVZEVRUU8KTUF5Q0NtdDFZbVZ5Ym1WMFpYTXdEUVlKS29aSWh2Y05BUUVMQlFBRGdnRUJBSzIybU13RHBGRkZMZ3JvWkpUaQpXajBQcTIyc1JoWjR4YkJrMDErbDFDTk5xb2l5aUJ2TnduVWo5SGJNeG4wNmdRcnovWThwcEtEdElqU3h2eU5DCk5TZjdZTSt6c21CaHN4d3l4SVdra3JQUTQ0M0FDN0xHOE5wdmhBYThpZFRXaUx5RDRhRlpQeGg4MGQ2UkJYWWwKbEJ0ZUhvNjhBVzVFcnFrSkdYVCsrV2FGdzhNWlNaUXVYbUZhV01STFdPYXBMQWxOZmtnY29uWHJpMFJmUTRlWApDd2pMSEFqUUFxZE0yTkMvZGU4cWhMd1RaUFNjN25lR1RZVDFnTlF5S2xyNE9uR1dJcC83aWtUMzdibmtEUklmCm95YVB2eFpDMm9JVUJicVhIVjNRcStJVVV1MUluZ1lsL29ZUzlQWGxxdDRHTkFTeTA3M0dXS1lGWWc1UHRrdGQKYWZrPQotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tCg=="

if not os.path.exists('./data'):
    os.makedirs('./data')

# Decode the Base64 encoded certificate data into certificate files
with open("./data/client.crt", "w") as f:
    f.write(base64.b64decode(client_certificate_data).decode())
with open("./data/client.key", "w") as f:
    f.write(base64.b64decode(client_key_data).decode())
with open("./data/ca.crt", "w") as f:
    f.write(base64.b64decode(certificate_authority_data).decode())

# Configure the Kubernetes client
configuration = client.Configuration()
configuration.host = server
configuration.ssl_ca_cert = "./data/ca.crt"
configuration.cert_file = "./data/client.crt"
configuration.key_file = "./data/client.key"

ssl_ca_cert = "./data/ca.crt"
cert_file = "./data/client.crt"
key_file = "./data/client.key"
# Create a new client instance
api_client = client.ApiClient(configuration=configuration)

@app.route('/trigger', methods=['POST'])
def trigger():
    data = request.json
    action = data.get('action')
    parameter = data.get('parameter')  # 获取整数参数
    if action == 'increase':
        exponential_increase(parameter)
        return jsonify(message="Exponential increase triggered!"), 200
    elif action == 'decrease':
        exponential_decrease(parameter)
        return jsonify(message="Exponential decrease triggered!"), 200
    else:
        return jsonify(error="Invalid action"), 400

def run_flask_app():
    app.run(host='0.0.0.0', port=8085)
def send_request():
    headers = {"Authorization": "Bearer " + 'YUF6TFpqbm1QRzErVUhQekxnOWtpaU5LRldnSFJ5R29USU1GL1d5UHN3Yz0K'}
    try:
        response = requests.get(
            server + "/api",
            verify=ssl_ca_cert,
            cert=(cert_file, key_file)
        )
        
    except requests.RequestException as e:
        print(e)
    return response.status_code
    

def send_request_with_rtt(i):
    start_time = time.time()
    response = send_request()
    end_time = time.time()
    round_trip_time = (end_time - start_time) * 1000
    return (response, round_trip_time)

def exponential_increase(parameter):
    timeout_percentage = 0.1
    avg_rtt_list = []
    x = 1
    max_x = parameter
    with ThreadPoolExecutor() as executor:
        while x > 0 and x <= max_x:
            response_times = []
            timeouts = 0
            results = list(executor.map(send_request_with_rtt, range(x)))
            for response, round_trip_time in results:
                response_times.append(round_trip_time)
                if response != 200:
                    timeouts += 1
                if round_trip_time > 3000:
                    break
            x *= 2
            valid_percentage = 1 - timeouts/x
            if valid_percentage < 1 - timeout_percentage and x >= 10:
                break
            avg_rtt = sum(response_times) / len(response_times)
            avg_rtt_list.append(avg_rtt)
    with open("./data/avg_rtt_history.txt", "a") as file:
        file.write("inc:"+"\n")
        file.write(str(avg_rtt_list) + "\n")

def exponential_decrease(parameter):
    timeout_percentage = 0.1
    avg_rtt_list = []
    x = parameter
    with ThreadPoolExecutor() as executor:
        while True and x >=1:
            response_times = []
            timeouts = 0
            results = list(executor.map(send_request_with_rtt, range(x)))
            print("Sending " + str(x) + " requests")
            for response, round_trip_time in results:
                response_times.append(round_trip_time)
                if response != 200:
                    timeouts+=1
                if round_trip_time>3000:
                    break
            x = int(x / 2)
            if x!=0:
                valid_percentage = 1 - timeouts/x
                if valid_percentage < 1 - timeout_percentage and x >= 10:
                    break
            avg_rtt = sum(response_times) / len(response_times)
            avg_rtt_list.append(avg_rtt)
    print(avg_rtt_list)
    with open("./data/avg_rtt_history.txt", "a") as file:
        file.write("dec:" + "\n")
        file.write(str(avg_rtt_list) + "\n")

# Define gauge metrics
CPU_UTILIZATION = Gauge('cpu_utilization_rate', 'CPU Utilization Rate')
MEMORY_UTILIZATION = Gauge('memory_utilization_rate','Memory Utilization Rate')
NETWORK_BANDWIDTH_UTILIZATION = Gauge('network_bandwidth_utilization_rate', 'Network Bandwidth Utilization Rate')

@app.route('/metrics')
def metrics():
    # Return all defined metrics
    return Response(generate_latest(), mimetype='text/plain')

def get_cpu_utilization():
    prom_url = "http://prometheus-operated.monitoring:9090"
    # prom_url = "http://localhost:9090/"
    # query CPU utilization
    query = '100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)'
    response = requests.get(f"{prom_url}/api/v1/query", params={'query': query})

    data = response.json()
    if data['status'] == 'success' and len(data['data']['result']) > 0:
        utilization = float(data['data']['result'][0]['value'][1])
        return utilization
    else:
        return None
# Function to get Memory utilization
def get_memory_utilization():
    prom_url = "http://prometheus-operated.monitoring:9090"
    # prom_url = "http://localhost:9090/"
    query = '(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100'
    response = requests.get(f"{prom_url}/api/v1/query", params={'query': query})
    data = response.json()
    if data['status'] == 'success' and len(data['data']['result']) > 0:
        return float(data['data']['result'][0]['value'][1])
    return None

# Function to get Network bandwidth utilization rate
def get_network_bandwidth_utilization():
    prom_url = "http://prometheus-operated.monitoring:9090"
    # prom_url = "http://localhost:9090/"
    query = 'irate(node_network_receive_bytes_total[5m]) + irate(node_network_transmit_bytes_total[5m])'
    response = requests.get(f"{prom_url}/api/v1/query", params={'query': query})
    data = response.json()
    if data['status'] == 'success' and len(data['data']['result']) > 0:
        return float(data['data']['result'][0]['value'][1])
    return None
# Function to update metrics
def update_metrics():
    while True:
        cpu_utilization = get_cpu_utilization()
        memory_utilization = get_memory_utilization()
        network_bandwidth_utilization = get_network_bandwidth_utilization()

        if cpu_utilization:
            CPU_UTILIZATION.set(cpu_utilization)
        if memory_utilization:
            MEMORY_UTILIZATION.set(memory_utilization)
        if network_bandwidth_utilization:
            NETWORK_BANDWIDTH_UTILIZATION.set(network_bandwidth_utilization)

        time.sleep(1)
if __name__ == '__main__':
    # Start up the server to expose the metrics
    start_http_server(8000)

    # Start Flask app in a separate thread
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.start()

    # Update metrics in the main thread
    update_metrics()


