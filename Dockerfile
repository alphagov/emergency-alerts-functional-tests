FROM --platform=linux/amd64 ubuntu:20.04

ENV ENVIRONMENT='development'
ENV DIR_TESTS='/eas/emergency-alerts-functional-tests'
ENV VENV_TESTS='/venv/emergency-alerts-functional-tests'
ENV PYTHON_VERSION='3.9'
ENV PYTHON_FULL_VERSION=$PYTHON_VERSION'.16'
ENV TZ=Europe/London

# Tenant-specific Environment Variables
ENV TENANT_ID='<your-tentant-prefix>'
ENV TENANT_GOVUK_URL='<tenant-cloudfront-distribution>'

# Variables copied from "emergency-alerts-infra-mgt" account
ENV BROADCAST_SERVICE_API_KEY='<broadcast-api-key>'
ENV SECRET_KEY='<secret-key>'
ENV DANGEROUS_SALT='<dangerous-salt>'
ENV ADMIN_CLIENT_SECRET='<admin-api-client-secret>'

# Set up timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install tools & python related pre-reqs
RUN apt-get update -y
RUN apt-get install -y \
    apt-utils \
    build-essential \
    cmake \
    curl \
    libcurl4-openssl-dev \
    libffi-dev \
    libgconf-2-4 \
    libnss3 \
    libssl-dev \
    libxi6 \
    make \
    python-openssl \
    wget \
    xvfb \
    zlib1g-dev

# Install Python.
RUN cd /opt && \
    wget https://www.python.org/ftp/python/$PYTHON_FULL_VERSION/Python-$PYTHON_FULL_VERSION.tgz --no-check-certificate && \
    tar xzvf Python-$PYTHON_FULL_VERSION.tgz && \
    cd Python-$PYTHON_FULL_VERSION && \
    ./configure && \
    make && \
    make install && \
    ln -fs /opt/Python-$PYTHON_FULL_VERSION/Python /usr/bin/python$PYTHON_VERSION

# Install google chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' && \
    apt-get -y update && \
    apt-get install -y google-chrome-stable

# Install chromedriver
RUN apt-get install -yqq unzip jq && \
    curl -s https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json | jq -rc '.channels.Stable.downloads.chromedriver[] | select(.platform == "linux64").url' > /tmp/chromedriver_url && \
    wget -O /tmp/chromedriver.zip `cat /tmp/chromedriver_url` && \
    unzip -j /tmp/chromedriver.zip chromedriver-linux64/chromedriver -d /usr/local/bin/

# Install any missing dependencies
RUN apt-get install -f -y

COPY . $DIR_TESTS

# Bootstrap the functional test application
RUN cd $DIR_TESTS && \
    python$PYTHON_VERSION -m venv $VENV_TESTS && \
    . $VENV_TESTS/bin/activate && \
    chmod +x environment.sh && \
    . ./environment.sh && \
    python$PYTHON_VERSION -m pip install --upgrade pip wheel setuptools && \
    make bootstrap

# Run the functional tests
RUN cd $DIR_TESTS && . $VENV_TESTS/bin/activate && . ./environment.sh && \
    make test-broadcast-flow && \
    make test-cbc-integration && \
    make test-platform-admin-flow && \
    make test-authentication-flow && \
    make test-links-and-cookies && \
    make test-template-flow && \
    make test-user-operations
