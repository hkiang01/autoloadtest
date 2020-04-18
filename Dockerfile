FROM python:3.8-buster

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD app.py .
ADD generate_locustfile.py .
RUN python generate_locustfile.py

EXPOSE 80
HEALTHCHECK --interval=10s --timeout=3s \
    CMD curl -f http://localhost:80/ping || exit 1


CMD ["python", "app.py"]
