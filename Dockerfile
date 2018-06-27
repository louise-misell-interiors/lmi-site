FROM python:3
ENV PYTHONUNBUFFERED 1
RUN apt-get update \
    && apt-get install -y --no-install-recommends libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /src
WORKDIR /src
ADD requirements.txt /src
RUN pip install -r requirements.txt
COPY ./lmisite /src
CMD /src/start.sh
EXPOSE 8000
