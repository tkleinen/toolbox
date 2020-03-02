FROM ubuntu:12.04
RUN apt-get update && apt-get install -y \
	build-essential \
	gettext \
	gdal-bin \
	libgdal-dev \
	python-dev \
	mysql-client
RUN mkdir /code
WORKDIR /code
RUN curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py"
RUN python get-pip.py && rm get-pip.py
COPY . .
RUN pip install pip --upgrade && pip install --no-binary django,django-olwidget -r requirements.txt


