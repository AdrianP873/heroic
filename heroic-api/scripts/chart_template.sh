#!/bin/sh

# Lints helm chart and renders chart templates locally and displaying the output.

set -e

CHART=$1

echo "Linting helm chart..."
helm lint heroic-api/charts/${CHART}

echo "Templating helm chart..."
helm template \
    test-${CHART}-chart \
    heroic-api/charts/${CHART} \
  --namespace default \
  --atomic \
  -f heroic-api/charts/tests/${CHART}-values.yml \
  --output-dir heroic-api/charts/tests/test-outputs