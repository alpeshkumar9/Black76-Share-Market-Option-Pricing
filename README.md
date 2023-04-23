# Black76 Share Market Option Pricing

A REST API web application to calculate PV of European options with Black76 formula

Tech Stack: Docker, FastAPI, Postgres

## Setup and start Postgres database docker container

run following command on terminal to setup database

```commandline
docker-compose up -d db
```

## Setup and start Web Application docker container

run following command on terminal to setup database

```commandline
docker-compose up -d --build app
```

## Testing

run following command on terminal to setup database

```commandline
docker-compose up tests
```
