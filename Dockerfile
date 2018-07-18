FROM python:3.6.6-stretch
RUN mkdir -p /app
COPY requirements /app/requirements
RUN pip3 install -r /app/requirements/requirements.txt && ls /app
COPY duplex_cloud_scan /app/duplex_cloud_scan
COPY service_account.json /app
COPY client_secret.json /app
ENV GOOGLE_APPLICATION_CREDENTIALS /app/service_account.json
WORKDIR /app
CMD [ "python3", "/app/duplex_cloud_scan/main.py" ]