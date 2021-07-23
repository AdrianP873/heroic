#!/bin/sh

# Lints helm chart and renders chart templates locally and displaying the output.

set -e

CHART=$1

echo "Linting helm chart..."
helm lint charts/${CHART}

echo "Templating helm chart..."
helm template \
    test-${CHART}-chart \
    charts/${CHART} \
  --namespace default \
  --atomic \
  -f charts/tests/${CHART}-values.yml \
  --output-dir charts/tests/test-outputs