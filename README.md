# MLOps/Flow showcase

Hi! This is a dummy project that tries to showcase the wonders of MLOps in a **minimal**, **open-source**, **Python-based**, **MLFlow-centered** kind of way.

The product itself is a *"@oscarigrexas sickness predictor app"*, that tries to predict whether I will personally be sick the following day based on some meteorological air quality indicators.

As far as nice MLOps practices go, this repo covers:
- Scheduled data integration pipelines (thanks to dlt and Prefect)
- Workflow orchestration and observability (thanks to Prefect)
- Exploratory experiment tracking (thanks to MLFlow)
- Model registration and comparison (thanks to MLFlow)
- Standardized model serving with promotion strategy (thanks to MLFlow)
- Robust automatable deployments (thanks to Docker Compose)

## Setup
You'll need Docker.
If you want to work on and run stuff locally you'll also need uv.

To launch the whole thing, first create a `.env` environment file based on the example provided:
```bash
cp example.env .env
vim .env     # edit whatever
```

And then run:
```bash
docker compose up -d --build
```

That should be it!

## Project structure
I've decided to organize the different components of the system in separate folders within the same GitHub repo for convenience's sake.
In reality, these invidual components are their own self-contained Python projects, and could live in their own separate repos owned by different teams, having independent life-cycles governed by separate CI pipelines.

```bash
.
├── app             # the very simple web app that serves as front-end
├── db              # the DB configuration
├── elt             # the data integration service
├── minio           # the configuration for the unstructured object storage
├── ml              # the ML training and inference service
├── mlflow          # config for the MLFlow service
├── notebooks       # exploratory Jupyter notebooks
├── example.env     # an example environment config
├── compose.yml     # the heart of the deployment, connecting everything together
└── README.md       # this doc
```

## Components
Let's take a look at these individual components and their roles in the bigger picture.

### The DB
In this case, the DB is only used as support, to store some metadata for other services (Prefect and MLFlow). In any case, it's a full-fledged Postgres instance, and could of course be used to setup a data warehouse with actual business data and analytics capabilities!

You may check it out at the standard port 5432, using the credentials defined in your `.env` file. Use `docker compose exec -it psql -U postgres` to run psql from within the DB container itself, or use your favorite SQL tool.

## The object storage
Being the backbone of data lakes, unstructured object storage services are very much useful in data and ML engineering contexts. In this case, the S3-like object storage Minio serves as both a landing zone for the raw meteorological data from the API, and to house the files that MLFlow uses to store ML models and other unstructured artifacts.

You can browse its buckets and files at [http://localhost:9001](http://localhost:9001), using the `MINIO_ROOT_` credentials in `.env`.

## The orchestrator
An orchestration-scheduling service such as Prefect (or Airflow, or Dagster, etc., but I like this one) is useful to both... well... orchestrate and schedule..., but also to add a very nice observability and resilience layer to data and ML workflows, which usually look like pipelines and DAGs, and benefit greatly from a bit of structure.

Check out its workflow runs and logs at [http://localhost:4200](http://localhost:4200)!

## The ELT pipeline
This component uses [dlt](https://dlthub.com/) to query the [Open-Meteo meteorological API](https://open-meteo.com/en/docs/air-quality-api) and incrementally load the newest data into our object storage. Check out the generated files in the *elt-data* bucket in Minio.

## The notebooks
Jupyter Notebooks are a very popular and scientist-loved way of interacting with Python code, ML models and visualizations in a friendly sandbox context. While they're often associated with not-so-great software-building practices, they're an invaluable tool to iterate efficiently through data science approaches.

## The ML code
This module contains the ML code itself (and all of its data science dependencies). Here we extract our favorite model from the dirtier exploration code, and package it in such a way that it can be easily trained, evaluated, distributed and reproduced. The generated artifacts (model and Docker image containing its dependencies) can then be used to serve the ML solution.

## The front-end app
This is just an example of the kind of downstream app that could be consuming our model. Built using Streamlit, it acts as a thin but colorful wrapper over the API of the model server.

Interact with it at [http://localhost:8501](http://localhost:8501).

## The ML experiment tracking server and model registry
Finally, the star of the project. MLFlow serves as an experiment tracking server (logging the parameters and results of both exploratory and production-level training), as a model registry (storing the different versions of the trained models, along with their lineage and metadata), and as an inference server (publishing models under a consistent API and allowing for promotion patterns).

Browse it at [http://localhost:5000](http://localhost:5000).