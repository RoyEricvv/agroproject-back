# README #

This README would normally document whatever steps are necessary to get your application up and running.

### What is this repository for? ###

The Backend help users manangement a livestock farm

## Requirements

1. Docker

1. Ngrok

## Build

1. Build docker images

        docker compose build

1. Access to the zappa container

        docker compose run --rm --service-ports project

1. Setup virtual environment

        python -m venv .venv
        source .venv/bin/activate

1. Install python dependencies

    Install dependencies using pip:

        pip install -r requirements.txt

### Contribution guidelines ###

* Writing tests
* Code review
* Other guidelines

### Who do I talk to? ###

* Repo owner or admin
* Other community or team contact