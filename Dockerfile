FROM python:3
WORKDIR /usr/app
COPY . .
RUN pip3 install .
ENTRYPOINT ["reblockstore"]
