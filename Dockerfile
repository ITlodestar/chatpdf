FROM python:3.9

RUN mkdir /app
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN python3 -m pip install --no-cache-dir --upgrade pip
# RUN rm -rf /var/lib/apt/lists/* && apt-get clean && apt-get update
RUN python3 -m pip install --no-cache-dir --upgrade -r /app/requirements.txt &&\
    pip install flask

COPY . .

EXPOSE 5000

CMD [ "flask", "run","--host","0.0.0.0","--port","5000"]

RUN mkdir /.cache
RUN chmod 777 /.cache
RUN mkdir .chroma
RUN chmod 777 .chroma
