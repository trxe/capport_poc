# Capport (POC)

First look at implementing Capport for configurable data pipelines.

Does not handle scheduling, only the execution of flows 
(to minimize programming needs).

because this is a POC the performance/stability requirements aren't strict,
but good to take note of them in our eventual move

## Overview

We build pipelines in the configs with list of nodes in the form of a DAG.
Each node comes with a unique string label, and subsequent children nodes
`take_from` them their results as kwargs.

## Immediate todo:

Write interfaces for
- node.py
- pipeline.py

setup pytest

write node and pipeline tests

write interfaces for 
- config parsers
- nhl_interface

Implement
- transform/mapping