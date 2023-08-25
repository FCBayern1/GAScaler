import json
import sys
import requests

prom_url = "http://prometheus-operated.monitoring:9090"

def get_metric_from_prometheus(query):
    response = requests.get(f"{prom_url}/api/v1/query", params={"query": query})
    data = response.json()
    if data['status'] == "success":
        # Assuming you're interested in the first result
        return float(data['data']['result'][0]['value'][1])
    else:
        raise Exception(f"Failed to fetch metric: {data['error']}")

def main():

    spec = json.loads(sys.stdin.read())
    extract(spec)

def extract(spec):

    numOfTargets = 3  # only 3 metrics
    pipe_out = dict()

    # Define the Prometheus queries for each metric
    queries = {
        "cpu_usage": "sum(rate(container_cpu_usage_seconds_total[5m]))",
        "memory_working_set_bytes": "sum(container_memory_working_set_bytes)",
        "network_transmit_bytes": "sum(rate(container_network_transmit_bytes_total[5m]))"
    }

    for metric_name, query in queries.items():
        value = get_metric_from_prometheus(query)
        pipe_out[metric_name] = value

    # Store the collected metrics
    toBeStored = [
        pipe_out['cpu_usage'],
        pipe_out['memory_working_set_bytes'],
        pipe_out['network_transmit_bytes']
    ]
    toBeStored = ','.join(list(map(str, toBeStored)))
    with open("/metrics_log.csv", "a+") as fp:
        fp.write(toBeStored + "\n")

    # Generate some JSON to pass to the evaluator
    sys.stdout.write(json.dumps(pipe_out))

if __name__ == "__main__":
    main()
