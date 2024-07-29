FROM python:3.11

WORKDIR /usr/src/app

COPY . .

RUN chmod +x /usr/src/app

RUN pip3 install -r requirements.txt

CMD ["bash", "start.sh"]
