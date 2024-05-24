FROM ubuntu:20.04

ENV ENVIRONMENT='development'
ENV DIR_TESTS='/eas/emergency-alerts-functional-tests'
ENV VENV_TESTS='/venv/emergency-alerts-functional-tests'
ENV PYTHON_FULL_VERSION='3.9.16'

ENV TENANT_ID='<your-tentant-prefix>'
ENV TENANT_GOVUK_URL='<tenant-cloudfront-distribution>'

# Install OS updates
RUN apt-get update -y

# Install commonly used tools, python related pre-reqs, ca-certs and OS tools
RUN apt-get install -y xvfb libxi6 libgconf-2-4 libnss3

# Install Python.
RUN cd /opt && \
    wget https://www.python.org/ftp/python/$PYTHON_FULL_VERSION/Python-$PYTHON_FULL_VERSION.tgz --no-check-certificate && \
    tar xzvf Python-$PYTHON_FULL_VERSION.tgz && \
    cd Python-$PYTHON_FULL_VERSION && \
    ./configure && \
    make && \
    make install && \
    ln -fs /opt/Python-$PYTHON_FULL_VERSION/Python /usr/bin/python$PYTHON_VERSION && \
    pip install --upgrade pip

# Install google chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' && \
    apt-get install -y google-chrome-stable

# Install chromedriver
RUN apt-get install -yqq unzip jq && \
    curl -s https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json | jq -rc '.channels.Stable.downloads.chromedriver[] | select(.platform == "linux64").url' > /tmp/chromedriver_url && \
    wget -O /tmp/chromedriver.zip `cat /tmp/chromedriver_url` && \
    unzip -j /tmp/chromedriver.zip chromedriver-linux64/chromedriver -d /usr/local/bin/

RUN apt-get install -f -y

COPY . $DIR_TESTS

RUN cd $DIR_TESTS && \
    python -m venv $VENV_TESTS && \
    . $VENV_TESTS/bin/activate && \
    chmod +x environment.sh && \
    . ./environment.sh && \
    python -m pip install --upgrade pip wheel setuptools && \
    make bootstrap

RUN cd $DIR_TESTS && . $VENV_TESTS/bin/activate && make test
