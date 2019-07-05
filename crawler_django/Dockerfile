FROM python:3.5-alpine

RUN apk add --no-cache jpeg-dev zlib-dev

RUN apk add --no-cache postgresql-dev

RUN apk add --no-cache libmemcached-dev zlib-dev

RUN apk add --no-cache gcc g++ make linux-headers libxml2 libxslt-dev libffi-dev openssl-dev

WORKDIR ./

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD [ "python", "manage.py", "runserver" ]
