# Capport (POC)

First look at implementing Capport for configurable data pipelines.

Does not handle scheduling, only the execution of flows 
(to minimize programming needs).

because this is a POC the performance/stability requirements aren't strict,
but good to take note of them in our eventual move, which should include 
more complete config validation

## Setup

```bash
# at project root
# first setup
python -m venv .venv/

# also at project root
source .venv/bin/activate
pip install .
# run the pipeline "trial" with the dev configs provided
source src/capport/core/main.py -c configs -p trial

# formatter
./scripts/format.sh
```

## Overview

This is POC for a data pipeline tool. 

Each pipeline is a DAG that TRANSFORMs information from SOURCE to SINK,
and we're calling each such stage as a "node".

Each node runs exactly one "task". Each task can be a 

    - simple task: implementation non-dependent on other configs
        - e.g. Writing output to csv.
    - templated task: implementation depends on other configs
        - e.g. Mapping between 2 JSONs

Each templated task will depend on other auxiiliary configs. These include:

    - model.yml (for sources/sinks)
    - service.yml (for sources/sinks)
    - transform.yml (for transforms)

The "src/capport/config/" folder currently has a rough idea of how the configs 
should be handled, and example configs are in "config/".

There is a ton of config data, so each sort needs to be put into a **registry**.
Pipelines should eventually be able to call other pipelines too, hence all 
pipelines have to be registered.

ALL THE COMPONENTS (at least most of them) ALREADY HAVE A FILE, what each
should do is contained there

### FAQ

1. What are you even doing?
    - secret

2. You may notice this looks like what Airflow does so why not just use Airflow?
    - It's more fun building your own Airflow
    - I would prefer for this to be yaml configurable so non-programmers can 
    maintain the pipelines
    - We're not sticking with python in the long run, this is just the POC

3. Where should the registries go
    - Not in config, they should be in their individual folders
        - model
        - pipeline
        - service
        - transform

4. What is the folder "sources/" for?
    - You might notice that there is a "sources" folder without a config, 
    - and that's because for the time being i don't think the sources will 
    need templated tasks.
    - **This folder is for the source tasks.**
    - **Similarly there should be one for sink tasks.**
    - eventually if we need templated tasks for either, 
    we'll need to create registries like "transforms" for both sources and sinks.

## Immediate todo:

- [ ] basic CI/CD (pylint, pytest is enough)
- [ ] create sink tasks folder
- [ ] simple source task: `load_json`
- [ ] simple transform task: `json_to_df`
- [ ] simple sink task: `df_to_csv`
- [ ] write node and pipeline tests (rn i think it works but is untested LMAO)
- [ ] `PipelineParser` / `PipelineRegistry`
- [ ] `ModelParser` / `ModelRegistry`
- [ ] `ServiceParser` / `ServiceRegistry`
- [ ] `TransformParser` / `TransformRegistry`
- [ ] transform templated task: `mapping`