#!/bin/sh

# Package and publish the chart to s3 for developer use

set -e

CHART=$1
VERSION=v1.0.0

helm show chart ${CHART}

echo "Packaging ${CHART} chart directory in an archive."
helm package heroic-api/charts/${CHART} --version ${VERSION}

echo "Uploading chart archive to s3."
aws s3 cp ${CHART}-${VERSION}.tgz s3://heroic-api/charts/${CHART}/