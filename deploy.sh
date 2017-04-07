#!/bin/sh
set -o nounset -o errexit

APPLICATION=$(grep -E '^application:' app.yaml | sed 's/application: *//')
VERSION=$(git describe --tags --long --dirty| tr '[:upper:].' '[:lower:]-')

read -r -p "Application (default '$APPLICATION'): " user_application
read -r -p "Version (default '$VERSION'): " user_version

if [[ ! "$user_application" ]]; then
    user_application="$APPLICATION"
fi

if [[ ! "$user_version" ]]; then
    user_version="$VERSION"
fi

appcfg.py update . --version=$user_version --application=$user_application $@
