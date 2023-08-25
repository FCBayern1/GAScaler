import json, sys
import os
import GeneticAlgorithm as GA
import requests

# prom_url = "http://prometheus-operated.monitoring:9090"

if 'Threshold' in os.environ:
    expected = float(os.environ['Threshold'])
else:
    expected = 0.8

thresholds_up = {
    'cpu_usage': 0.7,
    'memory_working_set_bytes': 0.7,
    'network_transmit_bytes': 1000000
}
thresholds_down={
    'cpu_usage': 0.1,
    'memory_working_set_bytes': 0.1,
    'network_transmit_bytes': 10000
}
def main():
    spec = json.loads(sys.stdin.read())
    evaluate(spec)

def detect_bottleneck(metrics, thresholds_up,thresholds_down):
    count=0
    for metric, value in metrics.items():
        if value > thresholds_down[metric] and value < thresholds_up[metric]:
            count+=1
    return count==len(metrics)

def evaluate(spec):
    max_replicas = 8
    num_of_Targets = 3  # Only 3 metrics
    try:
        metrics_value_data = spec['metrics'][0]["value"]
        if isinstance(metrics_value_data, str):
            metrics_values = json.loads(metrics_value_data)
        else:
            metrics_values = metrics_value_data
    except json.JSONDecodeError as e:
        sys.stderr.write(f"Error decoding: {spec['metrics'][0]['value']}\n")
        sys.stderr.flush()
        raise e
    # Define the thresholds for each metric for scaling up and scaling down


    # Extract the current metrics from the spec
    current_metrics = {metric: metrics_values[metric] for metric in ['cpu_usage', 'memory_working_set_bytes', 'network_transmit_bytes']}

    Flag = detect_bottleneck(current_metrics, thresholds_up,thresholds_down)
    current_replicas = metrics_values.get("current_replicas", 1)  # Assuming 1 if not provided
    ga = GA.GeneticAlgorithm(population_size=20, mutation_rate=0.05, crossover_rate=0.5, max_generations=50,
                             max_replicas=8, current_replica_count=current_replicas)
    # Determine the scaling decision using Genetic Algorithm
    target_replicas = ga.evolve(current_metrics['cpu_usage'],current_metrics['memory_working_set_bytes'],current_metrics['network_transmit_bytes'])
    # Return the scaling decision
    if target_replicas <= max_replicas:
        evaluation = {"targetReplicas": target_replicas}
    else:
        evaluation = {"targetReplicas": max_replicas}
    if Flag:
        evaluation = 1
    sys.stdout.write(json.dumps(evaluation))

if __name__ == "__main__":
    main()