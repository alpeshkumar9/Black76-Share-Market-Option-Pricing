# Black76 Europe Option Pricing

A REST API web application to calculate PV of European options with Black76 formula

Tech Stack: Python, FastAPI, Postgres, Docker

## Initial Steps

- Clone the repositry
- Rename env.txt file to .env

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
