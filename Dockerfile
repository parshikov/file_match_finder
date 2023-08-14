FROM python:3-alpine

COPY . /app

RUN cd /app && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

RUN mkdir /torrents && \
    mkdir /source && \
    mkdir /destination

WORKDIR /app

ENTRYPOINT ["python", "file_match_finder.py", "-s", "/source", "-d", "/destination"]