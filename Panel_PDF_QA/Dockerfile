FROM python:3.9

RUN mkdir /code
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
COPY ./LangChain_QA_Panel_App.py /LangChain_QA_Panel_App.py
RUN python3 -m pip install --no-cache-dir --upgrade pip
RUN rm -rf /var/lib/apt/lists/* && apt-get clean && apt-get update
RUN python3 -m pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . .

EXPOSE 8080

CMD ["panel", "serve", "/LangChain_QA_Panel_App.py", "--address", "0.0.0.0", "--port", "8080", "--allow-websocket-origin", "*", "localhost", "templates/index.html"]

RUN mkdir /.cache
RUN chmod 777 /.cache
RUN mkdir .chroma
RUN chmod 777 .chroma
