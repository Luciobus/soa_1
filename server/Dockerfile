FROM python:3.8

WORKDIR /code

COPY . .

RUN pip install -r requirements.txt
RUN apt update
RUN apt install -y protobuf-compiler
RUN protoc -I=./proto/ --python_out=./proto/ data.proto

ENTRYPOINT [ "python3", "server.py" ]