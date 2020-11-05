#!/bin/sh
set -o nounset -o errexit

PROJECT=$(grep -E '^application:' app.yaml | sed 's/application: *//')
VERSION=$(git describe --tags --long --dirty| tr '[:upper:].' '[:lower:]-')

read -r -p "Project (default '$PROJECT'): " user_project
read -r -p "Version (default '$VERSION'): " user_version

if [[ ! "$user_project" ]]; then
    user_project="$PROJECT"
fi

if [[ ! "$user_version" ]]; then
    user_version="$VERSION"
fi

gcloud app deploy app.yaml --version=$user_version --project=$user_project $@
