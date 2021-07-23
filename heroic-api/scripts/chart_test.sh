#!/bin/sh

# Installs the test pods and tests the helm charts.

set -e

CHART=$1

echo "Installing helm chart: ${CHART}"

helm upgrade \
    ${CHART}-test ${CHART} \
    --install \
    --namespace default \
    --atomic \
    -f heroic-api/charts/tests/${CHART}-values.yml

echo "Testing helm chart: ${CHART}"

helm test \
    ${CHART}-test \
    --namespace default

helm uninstall \
    ${CHART}-test \
    --namespace default