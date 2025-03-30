"""
TransformRegistry:

Configurations for the transform template_tasks.

Inside ./transforms/* there should only be one `mapping` method.
`mapping` infact actually takes in the mapping config from the 
transforms config file and creates mapping functions, named by their keys,
that the PipelineRegistry can lookup.

see transform.yml for features required.
"""