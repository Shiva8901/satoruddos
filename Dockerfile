FROM python:3.11

WORKDIR /usr/src/app

COPY . .

# Grant execute permission for the entire directory and its contents
RUN chmod -R +x /usr/src/app

RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["python3", "main.py"]
