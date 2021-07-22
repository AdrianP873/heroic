#!/bin/sh

echo "Linting helm chart..."
helm lint charts/application

echo "Templating helm chart..."
helm template \
    test-chart \
    charts/application \
  --namespace default \
  --atomic \
  -f charts/tests/application-values.yml \
  --output-dir charts/tests/test-outputs