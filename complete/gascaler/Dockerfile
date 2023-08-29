# Pull in Python build of CPA
FROM custompodautoscaler/python:latest

# Install required packages
RUN pip install joblib numpy pandas requests


# Add config, evaluator and metric gathering Py scripts
ADD config.yaml evaluate.py metric.py __init__.py GeneticAlgorithm.py /


