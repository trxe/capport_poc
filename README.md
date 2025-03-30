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

We build pipelines in the configs with list of nodes in the form of a DAG.
Each node comes with a unique string label, and subsequent children nodes
`take_from` them their results as kwargs.

## Immediate todo:

write interfaces for
- node.py
- pipeline.py

setup pytest

write node and pipeline tests

write interfaces for 
- config parsers
- nhl_interface

implement
- transform/mapping