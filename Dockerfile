FROM python:3.7.5
WORKDIR /usr/app
COPY . .
RUN pip3 install .
ENTRYPOINT ["reblockstore"]
