import math
import os
import base64
import kubernetes
import requests
import time
import numpy as np
import torch
from torch import nn
import warnings
from urllib3.exceptions import InsecureRequestWarning
from concurrent.futures import ThreadPoolExecutor
from kubernetes import client, config

warnings.filterwarnings('ignore', category=InsecureRequestWarning)
os.environ['KMP_DUPLICATE_LIB_OK']='True'

max_x = 0
replica_arr = []

server = "https://127.0.0.1:64479"
client_certificate_data = "LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURJVENDQWdtZ0F3SUJBZ0lJWnRTdU0rU3hidll3RFFZSktvWklodmNOQVFFTEJRQXdGVEVUTUJFR0ExVUUKQXhNS2EzVmlaWEp1WlhSbGN6QWVGdzB5TXpBNE1qa3hOVFUyTlRCYUZ3MHlOREE0TWpneE5UVTJOVEphTURReApGekFWQmdOVkJBb1REbk41YzNSbGJUcHRZWE4wWlhKek1Sa3dGd1lEVlFRREV4QnJkV0psY201bGRHVnpMV0ZrCmJXbHVNSUlCSWpBTkJna3Foa2lHOXcwQkFRRUZBQU9DQVE4QU1JSUJDZ0tDQVFFQTRGVTEwN2gvUmsvUkdCc1gKS1hNL3duemo4SXR3bStwZnJPVEZsYkl4NVVHRkpndDNlWXdNd2t3MEVod3BtZHd6MDB4RGxmOW12TkpXMkM1YwpWYUFPTXpiYVFPeTRVSHhndDBoK3liMEpGSW9TSTloemVTR08xOVk2T1pXS1dHNnpqc2Rha2FvNWNtQWZyVnJRClc5bGFrWmZMMnF3a2Jyb1lSSlhrOE9nd1VnSDBTMmdTZTNianZuSDM1Q0pGSGF4Qm8yUER6VHZ1aDhEY0JMeFgKVXZCL2p5MUovdThLWHZwVis1SzJMSDArSG11NGNNSDZzU0E2eEJ2MnRVclVUUGlWaXE1K1JZaGRMM2RRcWxzOApxVUJFQnVLdGxhbWRIWWpja1kvVzVONTVENDlYUUcyQXN1ejVLMTRGZ2xNWGR1WDViRzBmQUxlLzdzbnV3ZzYxCjM2d0xiUUlEQVFBQm8xWXdWREFPQmdOVkhROEJBZjhFQkFNQ0JhQXdFd1lEVlIwbEJBd3dDZ1lJS3dZQkJRVUgKQXdJd0RBWURWUjBUQVFIL0JBSXdBREFmQmdOVkhTTUVHREFXZ0JSWUxFRkJybW4wSm13dzJyTkc0c1kxeExIaAozREFOQmdrcWhraUc5dzBCQVFzRkFBT0NBUUVBT2U1OFBrSmxUelFHSFN0SWRLRXBNM0FzdjVNdE94UERPVVJxCjhoaTM0L0dvZ1FxWWRMcGc3aWVGNmFxT1BGUUtxZkZKWUxOUlhXbWdaWlc1MTlRK2tJcTN1SStvTHpMcGhtbEgKL3Jqb3hkRCtMZ0Vvd1NkTVpPZGpQbmFoV3pxV3o0WjhnOUJEeTBJZGQ3bDlFcGlkQ25ObXp1ejM2K0F0SHNoNwpCVnBnT2ZqZk53T2dtK1F3cERxRHJrdmNhblRyNnJxWW1CQ3NZbGZMYTk2OGllc2Nxdk5DaDhFUFpTSnpibElTCk9LdGFxSzBxZ0NTeWJZcDJ6dGxyY2pnNG9xb3FUVzNUcGVJVEVLWVBFNEoydW9sZHdVK01OYVl4S1FOL1pFWXkKU3hVYjBFdzFMN2RUSGE2b1M2alZWVUhBRDlKQnJEWENHbmptN1hQcFFaakd2NUpzSVE9PQotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tCg=="
client_key_data = "LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQpNSUlFb3dJQkFBS0NBUUVBNEZVMTA3aC9Say9SR0JzWEtYTS93bnpqOEl0d20rcGZyT1RGbGJJeDVVR0ZKZ3QzCmVZd013a3cwRWh3cG1kd3owMHhEbGY5bXZOSlcyQzVjVmFBT016YmFRT3k0VUh4Z3QwaCt5YjBKRklvU0k5aHoKZVNHTzE5WTZPWldLV0c2empzZGFrYW81Y21BZnJWclFXOWxha1pmTDJxd2ticm9ZUkpYazhPZ3dVZ0gwUzJnUwplM2Jqdm5IMzVDSkZIYXhCbzJQRHpUdnVoOERjQkx4WFV2Qi9qeTFKL3U4S1h2cFYrNUsyTEgwK0htdTRjTUg2CnNTQTZ4QnYydFVyVVRQaVZpcTUrUlloZEwzZFFxbHM4cVVCRUJ1S3RsYW1kSFlqY2tZL1c1TjU1RDQ5WFFHMkEKc3V6NUsxNEZnbE1YZHVYNWJHMGZBTGUvN3NudXdnNjEzNndMYlFJREFRQUJBb0lCQUhYa01lSnUvZXZzZkQwSAoxNWMvNnMwQnB5UTlrMU5NeXpUb0VQSUhjSE5EaUg2aTNnbXhVTzgyN3RKcG5HOHdLc2dyTndWMzcvemhLU1I0CjBLdHE3cXQ1Y3g5Vmg5TThXZk5ZRk5GZUY0eUV0dDNCbllXVjNpU05mNUhOaGFQTm9XMHlWT1ZpS01oenZaSHoKdkxYWU51RjJmWG9RcHlETmlYMVpyTFB4d1pzR1VkeEU3WnVzS1hRdzFyWnpBTEIyWVFoejU0RCs0K1YyYjZSMgpJaGpOVnZkeTRPYjk4VkNtdTZMUFZzS1lnYjVKci9OYml2elh0Y055dlM1WmVOMkJjTkpNNzVsSk9WZGt5V3lYCnpZYUQycjNBc3NCTU1IRlFrcFVpUHBqQnNBelY1ck8wSktYNktzY3ZYNWdQekdyN1JvS3JVYk1Call2NGh6TFUKemhaQUNqMENnWUVBK0MrUmpQZ2RIdGVZVWs0MmpyTklMRjVYMk9lRCthV0UvUHRzQi9Ra0NleG9mOEIvblkrUgp3QTZjZ0FQV2IwN3lGdWFUWnVQOWlVak1Gb0ZVbFpTWE4vWFVqaVhXaW9McjNVa1VYa0RKeW9yay9nQzBpYjJqCm11bmNSTmFzeWVldHJGbE9tVUVoL2ZMQ2ZqTmJCdXNsMHpLN01tMkVCUkw4MUhMQkZ3cnpPVE1DZ1lFQTUyVmgKdEpUeVA3RTcyRXlCMGl5ay9lYlB1YmJDNmVNLzdjcXBvTllqd3dlZzFYK1lGcldWLzhoTGdpbG1mTkdMdE5BdQpxZnFBV2g3VmxWZzFNWWpGQ2lmR0daejR4Q3JwaUJQOG5xRnJSMDZiOWVBenVSTWlnemxKRmx6a2dGaW1XU1p4CmtGbmp4YStmcGVncTdOTVVkek51SmJQZ0srTnJZVDJBU3JRdDZOOENnWUFKUDJ5Qy9qUEhsR3orbEIrQVRibmcKdlZzMG45dlJENVBYQVY5VEpJdTdPdTNoNU1CY2xKN3ZzeHV0d1hiYUN1MEdZVzBZcG1JcUhXWk5hR0JJZXBMdgo2TjhVdE9BN3BRazQ0Nkk0cU4xY0NMVGpxZzhRR3RyZnlOc0dUYUYrbkgxaU1LbTNHREEyRURlakVETFNIU3o1Cm82aEtCcjZtbWNDR0FnaWozU3FXOVFLQmdDekZLTXBQcHk4N2syQ2VMT0FGVTBic3lYUWRNRWtnZHRZRFNCNmUKVC8wRUZOSTZCYXNmSnc1K0tsM2N0TCtocTI0b2VWN1o0TXVPKzdRUmhQazRoU2NaMnZKSnRMZi90WDltbnBIeQptVmNLbHBKVDlxM3dUZFVsMkVaRFl0S1NWRjBiV3cyYTFyOEE0OXF0dU9CcFZxUlpodzQwWjBNV2xVZ1RKaWRPCkJUUHhBb0dCQUp6c1Z3SlZvdGhpdHRnYnIxTWcxbmV1VDFodDAycXNoMXNqKzZOSzByRHc3bTQyNUNjWEhDMUkKUjhzQWxKaGwzNHZqa1ZZdEdBN2pwYUw2eHp4cmN4UkFLcmJkejJtTmc1MTZOeW5VSVo2UzdVSTFmWnlGU3M2bApRRHJhRVVGY2E1amh3a01wNnpHQ1MrQ0RIdHpkbzZMVzZHaWpqN25qclN3Ynl6UVI0ZXc0Ci0tLS0tRU5EIFJTQSBQUklWQVRFIEtFWS0tLS0tCg=="
certificate_authority_data = "LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUMvakNDQWVhZ0F3SUJBZ0lCQURBTkJna3Foa2lHOXcwQkFRc0ZBREFWTVJNd0VRWURWUVFERXdwcmRXSmwKY201bGRHVnpNQjRYRFRJek1EZ3lPVEUxTlRZMU1Gb1hEVE16TURneU5qRTFOVFkxTUZvd0ZURVRNQkVHQTFVRQpBeE1LYTNWaVpYSnVaWFJsY3pDQ0FTSXdEUVlKS29aSWh2Y05BUUVCQlFBRGdnRVBBRENDQVFvQ2dnRUJBTUxjCkg1ZERSTkNJNis4QzJCN2hNOTRpeitHRmpzZVdER2M0ZytEMEJZdlo4VlRIV0R4UTBUU3MxL09QV3ZIeWFtMG8KelM1SWVuVzlLU3crNVBHWk9oSWJlRTJmQUtIMTJhZkhKL1RUUTJIbzVHSFltU25aOVFzMFUycVFJVmd4V3JKbQpXYm9DVnF4UWhiOVVCWGNFS09ENks2Y3JTUlUvS0kzR0JsVmxuVFpoZy8xNEtaZUtVdGdjTTY3NHlHQ1EvZ3ptClZXREtncWk5MUJIYno2TWZyYU1ISzlMWjY2bUtzQ0R1QS91eUI1Q09LcjZBcTBkSXpGZkhpKzdrSUo3Q2VOYUQKMnpxa1lWejJ1RTVDdWJmd3RwOFAzV21NU01Da1hWU25iSlMyeWVXRUZRZktUaUNQMC9wMVA2ZXlQSUdIenA0TAppRUtKYXdnU3RWcnkvekZQY3JrQ0F3RUFBYU5aTUZjd0RnWURWUjBQQVFIL0JBUURBZ0trTUE4R0ExVWRFd0VCCi93UUZNQU1CQWY4d0hRWURWUjBPQkJZRUZGZ3NRVUd1YWZRbWJERGFzMGJpeGpYRXNlSGNNQlVHQTFVZEVRUU8KTUF5Q0NtdDFZbVZ5Ym1WMFpYTXdEUVlKS29aSWh2Y05BUUVMQlFBRGdnRUJBSGZ1c05kT2xHUkFOOU1icXlDRwpWZkNtOHY0SHJpLzNnQTNITU9kck5FdXU4bXVXbXBsSC92dXl5VEZxaUtkMXBpME9USy8wWlg5aEptOGdiN3ZSCjg3L0pXYnJFSkdiVThVN0RCUm5MQnpJQVR0WUNsWW40c3I0Tkd1WEs5Wm5LZFNFL2lHM09DQmhyZ214SVdoNlkKbXFUTThlRW01RjJnODVlVXlOOHNIbTBUVVhiblhjaHg5V0RFbUpXMWVTTWFGRlJrdDdVYzkrY0lNZWZVck0yagpzSkRBVkpCdHdRRFY2SmhseUNsa2FRajhjWFFNdU1MTjloRHV6VUIwVXc3dEM5TDZZdWJtdTlUbHRZVGNVVEN4CkUyd2lZb1ZUL1NXVzVUWlVWK2hNRTdyQ1FrMllFR0pTeXZFYy9vSEVkeVRKR1JMMWpKMmhmb203NWZlanA4aUUKNjRRPQotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tCg=="

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
token = "YUF6TFpqbm1QRzErVUhQekxnOWtpaU5LRldnSFJ5R29USU1GL1d5UHN3Yz0K"
configuration.ssl_ca_cert = "./data/ca.crt"
configuration.cert_file = "./data/client.crt"
configuration.key_file = "./data/client.key"
url=server
ssl_ca_cert = "./data/ca.crt"
cert_file = "./data/client.crt"
key_file = "./data/client.key"
# Create a new client instance
api_client = client.ApiClient(configuration=configuration)
api = client.AutoscalingV1Api(client.ApiClient())
apps_v1 = client.AppsV1Api(api_client)

hpa_name = "exp-test-statefulset"


class GRU(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(GRU, self).__init__()
        self.gru = nn.GRU(input_size, hidden_size)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x, _ = self.gru(x)
        x = self.fc(x[-1])
        return x


# def get_predictions(dataset_name):
#     script_dir = os.path.dirname(os.path.abspath(__file__))
#     # Change the current working directory to the script directory
#     os.chdir(script_dir)
#     os.chdir('dataset_files')
#     model = GRU(1, 128, 1)
#     if dataset_name == "world_cup":
#         data = np.loadtxt('invocation_count.csv', delimiter=',', skiprows=1, usecols=[1])
#     elif dataset_name == "nasa":
#         data = np.loadtxt('formatted_nasa_dataset.csv', delimiter=',', skiprows=1, usecols=[1])
#     data = data.reshape(-1, 1)
#     normal_data = data
#     # Normalize data
#     mean = data.mean()
#     std = data.std()
#     data = (data - mean) / std
#
#     # Split data into training and testing sets
#     split_index = int(0.6 * len(data))
#
#     test_data = data[split_index:]
#     # test_targets = data[split_index:]
#     test_targets = normal_data[split_index:]
#
#     # Convert data to tensors
#     test_targets = torch.FloatTensor(test_targets)
#     if dataset_name == "world_cup":
#         # Load the saved model
#         model.load_state_dict(torch.load("wc_model_count.pth"))
#     elif dataset_name == "nasa":
#         model.load_state_dict(torch.load("NASA_MODEL.pth"))
#     model.eval()
#     # Convert the data to tensors.
#     test_data = torch.from_numpy(test_data).float().unsqueeze(0)
#     test_targets = torch.FloatTensor(test_targets)
#     # Make predictions on the test data
#     with torch.no_grad():
#         predicted_data = model(test_data)
#     # Un-normalize the predictions
#     predicted_data = predicted_data.numpy()
#     predicted_data = predicted_data * std + mean
#
#     # Store the un-normalized predictions in a data structure
#     predictions = predicted_data.flatten().tolist()
#     # Convert the values in the predictions list to integers
#     predictions = [int(value) for value in predictions]
#
#     return predictions, test_targets


def send_request():
    # Set the headers for the subsequent request
    # headers = {"Authorization": "Bearer " + token}
    # # Send a GET request to the Kubernetes API server and print the response code
    # response = requests.get(url + "/api/v1", headers=headers, verify=False)
    # return response.status_code
    try:
        headers = {"Authorization": "Bearer " + 'YUF6TFpqbm1QRzErVUhQekxnOWtpaU5LRldnSFJ5R29USU1GL1d5UHN3Yz0K'}
        response = requests.get(
            server + "/api",
            verify=ssl_ca_cert,
            cert=(cert_file, key_file), headers=headers
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


def exponential_test(type, max_x):
    timeout_percentage = 0.1
    x = 1
    valid_times = []
    avg_rtt_list = []
    if type == "increase" or type == "2":
        print("BEGINNING EXPONENTIAL INCREASE")
    elif type == "decrease":
        print("BEGINNING EXPONENTIAL DECREASE")
        x = max_x


    with ThreadPoolExecutor() as executor:
        while True and x > 0 and x <= max_x:
            print("Sending " + str(x) + " requests")
            pods = get_pod_count(int(x))
            scaler(pods)
            # hpa_scaler()
            response_times = []
            timeouts = 0
            results = list(executor.map(send_request_with_rtt, range(x)))

            for response, round_trip_time in results:
                response_times.append(round_trip_time)
                if response != 200:
                    timeouts += 1
                if round_trip_time >3000:
                    break
            if type == "increase" or type == "2":
                x *= 2
            elif type == "decrease":
                x = math.floor(x / 2)
            if x ==0:
                valid_percentage = 1 - timeouts / 1
            else:
                valid_percentage = 1 - timeouts/x
            if valid_percentage < 1 - timeout_percentage and x >= 10:
                max_x = x
                break
            avg_rtt = sum(response_times) / len(response_times)
            avg_rtt_list.append(avg_rtt)
            print(avg_rtt_list[-1])
            if type == "2":
                try:
                    statefulset = apps_v1.read_namespaced_stateful_set(name=hpa_name, namespace='default')
                except:
                    print("can't connect to cluster")
                    print("is config correct?")
                    replica_arr.append(2) # append minimum if cant connect
                # Get the current number of replicas
                replicas = statefulset.status.replicas
                print(replicas)
                replica_arr.append(replicas)
    print("LOOP ENDED - EXPONENTIAL TEST COMPLETE")
    print("TIMEOUTS OCCURED AT 1 BEFORE: " + str(x))
    print(avg_rtt_list)
    print("max_x: " + str(max_x))


def get_pod_count(request_count):
    model = SimpleNN(1, 10, 1)
    model.load_state_dict(torch.load("nn_model.pth"))
    model.eval()
    with torch.no_grad():
        normalized_input = (request_count - 1) / (1024 - 1)
        input_tensor = torch.tensor([[normalized_input]], dtype=torch.float32)
        prediction = model(input_tensor)
        return prediction.item()


def scaler(predicted_pod_count):
    predicted_pod_count=int(predicted_pod_count)
    predicted_pod_count = max(1, predicted_pod_count)
    try:
        statefulset = apps_v1.read_namespaced_stateful_set(name=hpa_name, namespace='default')
        replicas = statefulset.status.replicas
    except Exception as e:
        print(f"Error reading StatefulSet: {e}")
        return

    if predicted_pod_count != replicas:
        statefulset.spec.replicas = predicted_pod_count
        try:
            apps_v1.replace_namespaced_stateful_set(name=hpa_name, namespace='default', body=statefulset)
        except Exception as e:
            print(f"Error updating StatefulSet: {e}")

# def generate_replica_arr():
#     max_x = 1024
#     timeout_percentage = 0.1
#     valid_times = []
#     re = []
#
#     print("BEGINNING LINEAR INCREASE")
#     x = 1
#
#     with ThreadPoolExecutor() as executor:
#         while x <= max_x:
#             print(f"Sending {x} requests")
#
#             # Calculate required pods based on request count and scale accordingly
#             pods = get_pod_count(int(x))
#             scaler(pods)
#
#             response_times = []
#             timeouts = 0
#             results = list(executor.map(send_request_with_rtt, range(x)))
#
#             for response, round_trip_time in results:
#                 response_times.append(round_trip_time)
#                 if response != 200:
#                     timeouts += 1
#                 if round_trip_time > 3000:
#                     break
#
#             valid_percentage = 1 - timeouts / x
#
#             if valid_percentage < 1 - timeout_percentage and x >= 10:
#                 break
#
#             try:
#                 statefulset = apps_v1.read_namespaced_stateful_set(name=hpa_name, namespace='default')
#             except:
#                 print("can't connect to cluster")
#                 print("is config correct?")
#                 re.append(2)  # append minimum if cant connect
#             else:
#                 # Get the current number of replicas
#                 replicas = statefulset.status.replicas
#                 print(replicas)
#                 re.append(replicas)
#
#             # Increment x for next iteration
#             x += 1
#
#     print("LINEAR TEST COMPLETE")
#     print(replica_arr)
#     return replica_arr
class SimpleNN(torch.nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super(SimpleNN, self).__init__()
        self.layer1 = torch.nn.Linear(input_dim, hidden_dim)
        self.layer2 = torch.nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        x = torch.nn.functional.relu(self.layer1(x))
        return self.layer2(x)
#
#
# def linear_regression():
#     # 数据生成
#     re = np.zeros(1024, dtype=np.float32)
#     re[:374] = 1
#     re[374:826] = 2
#     re[826:] = 3
#
#     X = np.array([[i] for i in range(1, 1025)], dtype=np.float32)
#     y = np.array(re, dtype=np.float32)
#
#     X_normalized = (X - X.min()) / (X.max() - X.min())
#
#     X_tensor = torch.from_numpy(X_normalized)
#     y_tensor = torch.from_numpy(y)
#
#     model = SimpleNN(1, 10, 1)
#     criterion = torch.nn.MSELoss()
#     optimizer = torch.optim.Adam(model.parameters(), lr=0.005)
#
#     num_epochs = 2000
#     for epoch in range(num_epochs):
#         optimizer.zero_grad()
#         outputs = model(X_tensor)
#         loss = criterion(outputs, y_tensor.view(-1, 1))
#         loss.backward()
#         optimizer.step()
#
#         if epoch % 100 == 0:
#             print(f'Epoch [{epoch}/{num_epochs}], Loss: {loss.item():.4f}')
#
#     torch.save(model.state_dict(), "nn_model.pth")
#     print("Training complete. Model saved to 'nn_model.pth'.")



def average_use_case_test(predictions, actual):
    avg_rtt_list = []
    count = 0
    previous_request_count = 0
    for x in predictions:
        response_times = []
        actual_count_to_send = actual[x]
        predicted_count_to_send = predictions[x]
        pod_count = get_pod_count(predicted_count_to_send)
        scaler(pod_count)
        for i in range(int(x)):
            response, round_trip_time = send_request_with_rtt(i)
            if response is not None:
                response_times.append(round_trip_time)
        avg_rtt = sum(response_times) / len(response_times)
        avg_rtt_list.append(avg_rtt)
        print(str(count) + ":" + str(avg_rtt_list))
        count += 1
        previous_request_count = int(x)



def predict(input_val):
    model = SimpleNN(1, 10, 1)
    model.load_state_dict(torch.load("nn_model.pth"))
    model.eval()
    with torch.no_grad():
        normalized_input = (input_val - 1) / (1024 - 1)
        input_tensor = torch.tensor([[normalized_input]], dtype=torch.float32)
        prediction = model(input_tensor)
        return prediction.item()

if __name__ == "__main__":
    # dataset_name = "world_cup"
    dataset_name = "nasa"
    # predictions, actual = get_predictions(dataset_name)

    # begin exponential increase
    exponential_test("increase", 1024)

    # begin exponential decrease
    # exponential_test("decrease", 1024)  # THIS VALUE MUST BE MANUALLY SET BY WHATEVER AVG LIMIT IS IN TESTS

    # begin average use case
    # average_use_case_test(predictions, actual)
