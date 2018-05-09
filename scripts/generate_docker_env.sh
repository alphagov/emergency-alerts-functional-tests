#!/usr/bin/env bash

set -eo pipefail

[ -n "$ENVIRONMENT" ] || (echo "ENVIRONMENT is not defined" && exit 1)

echo -n "" > docker.env

env_vars=(
    ENVIRONMENT
    BUILD_ID
    TEST_NUMBER
    FUNCTIONAL_TEST_EMAIL
    FUNCTIONAL_TEST_PASSWORD
    NOTIFY_ADMIN_URL
    NOTIFY_API_URL
    NOTIFY_SERVICE_API_KEY
    SERVICE_ID
    API_KEY
    ZENDESK_API_KEY
    NOTIFY_RESEARCH_MODE_EMAIL
    NOTIFY_RESEARCH_MODE_EMAIL_PASSWORD
    NOTIFY_RESEARCH_SERVICE_ID
    NOTIFY_RESEARCH_SERVICE_API_KEY
    NOTIFY_RESEARCH_SERVICE_API_TEST_KEY
    JENKINS_BUILD_EMAIL_TEMPLATE_ID
    JENKINS_BUILD_SMS_TEMPLATE_ID
    JENKINS_BUILD_LETTER_TEMPLATE_ID
    NOTIFY_RESEARCH_SERVICE_NAME
    NOTIFY_RESEARCH_EMAIL_REPLY_TO
    NOTIFY_RESEARCH_SERVICE_EMAIL_AUTH_ACCOUNT
    NOTIFY_RESEARCH_ORGANISATION_ID
    DOCUMENT_DOWNLOAD_API_HOST
    DOCUMENT_DOWNLOAD_API_KEY
)

for env_var in "${env_vars[@]}"; do
    if [ -n "${!env_var}" ]; then
      echo "${env_var}=${!env_var}" >> docker.env
    fi
done
