FROM python:3.11-bookworm
COPY . .
RUN pip3 install -r requirements.txt