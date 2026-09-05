FROM ghcr.io/home-assistant/base:latest

LABEL \
    io.hass.version="1.0.0" \
    io.hass.type="app" \
    io.hass.arch="aarch64|amd64"

WORKDIR /app

RUN apk add --no-cache \
    python3 \
    py3-pip

COPY requirements.txt .

RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

COPY app ./app
COPY run.sh /run.sh

RUN chmod a+x /run.sh

EXPOSE 8000

CMD ["/run.sh"]
