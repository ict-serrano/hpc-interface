FROM openjdk:11.0.8-jre-buster as builder
WORKDIR /build/
COPY . /build/
RUN /build/generate.sh

FROM python:3.8.7-alpine3.13
WORKDIR /app

COPY requirements.txt /app/
RUN pip3 install --no-cache-dir -r requirements.txt

COPY --from=builder /build/src/ /app/

EXPOSE 8080

WORKDIR /app
ENTRYPOINT ["python3"]
CMD ["-m", "hpc.api.run"]