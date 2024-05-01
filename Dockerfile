FROM python:3.12.3-alpine3.19

RUN apk update

RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

WORKDIR /app

COPY . /app
RUN python -m venv venv
RUN source ./venv/bin/activate
RUN python -m pip install -r /app/requirements.txt

CMD ["python", "app.py"]
#ENTRYPOINT ["tail", "-f", "/dev/null"]