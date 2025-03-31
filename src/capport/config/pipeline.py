"""
PipelineRegistry:

PipelineRegistry will hold a mapping of pipelines to their specs.
The main pipeline produces results to be written into the output dir.

The pipeline only consists of Nodes. Each node's configuration is parsed
by capport/core/node.py currently, so it doesn't have to happen here.

Nodes are of 3 types: source, sink and transform. All nodes are executed as
async tasks (currently signle threaded bc I haven't setup MT).
Each node is of the form:

---
- label: <unique_node_label>
  node_type: SOURCE/SINK/TRANSFORM
  use: <template_task>
  args:
    <user_arg_label>: <user_arg_value>
  take_from: # <-- this is mandatory for non-sources, ignored by sources
    <user_arg_label>: <user_arg_value>
  output_as: # <-- this is mandatory for sinks, optional for non-sinks
    - type: CSV/PKL/etc
      filename: <filename>
---

Currently I haven't done the `output_as` nodes yet because I haven't actually
written any transform template_tasks.

What is a template_task? They are the tasks that will actually ingest the
`args`, `take_from` and `output_as` stuff and process the result.
We will be putting them into ./sources/*, ./sinks/* and ./transforms/*

VERY IMPORTANTLY EVERY TEMPLATE TASK MUST BE ASYNC.

Eventually PipelineParser should validate that the pipeline is a DAG
(but just trust ourselves for now).
"""
