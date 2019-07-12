FROM alpine

RUN apk add --no-cache gcc g++ make linux-headers libxml2 libxslt-dev libffi-dev openssl-dev

FROM python:3.7

RUN pip install --upgrade pip

RUN mkdir /dstea

WORKDIR /dstea

COPY requirements.txt /dstea/

RUN python -m venv dstea_env

# RUN source ./dstea_env/bin/activate

RUN pip install --no-cache-dir -r requirements.txt

COPY . /dstea/

#CMD [ "python", "manage.py", "runserver" ]
