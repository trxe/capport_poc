"""
ModelRegistry:

ModelRegistry will hold a mapping of model names to their specifications,
in order to make the correct SQL commands to CRUD their tables.
see configs/model.yml for an example.

Roughly, the structure is:
---
model:
    <table_name>:
        <mandatory_table_key>: <type>
        <optional_table_key>?:
            type: <type>
            constraints: [<list of constraints>]
---
constraints include (for now):
- primary
- foreign
- unique
- optional (idiom for this is the "?" similar to typescript)
- indexed

there's more complex stuff we can handle later i think for now this is good enough

This will be used by the `sink` template_tasks e.g.

---
    - label: store_cs_player
      node_type: SINK
      use: postgres
      take_from:
        data: cs_player
        model_name: player <--
---
"""
