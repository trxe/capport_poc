import asyncio

from capport.core.cli import ConfigPack, get_cli_arg_parser
from capport.core.pipeline import Pipeline


def main():
    parser = get_cli_arg_parser()
    args = parser.parse_args()
    config_pack = ConfigPack(args.config_dir)
    # temporarily look thru pipelines like this:
    plname = args.pipeline
    plconf = [file.get(plname) for file in config_pack.collated_configs.get("pipeline") if file.get(plname)][
        0
    ]  # take the first
    pipeline = Pipeline(args.pipeline, plconf)
    asyncio.run(pipeline.start(interactive=args.interactive), debug=True)


if __name__ == "__main__":
    main()
