import asyncio

from capport.pipeline.pipeline import Pipeline
from capport.tools.cli import ConfigPack, get_cli_arg_parser


def main():
    parser = get_cli_arg_parser()
    args = parser.parse_args()
    config_pack = ConfigPack(args.config_dir)
    # temporarily look thru pipelines like this:
    plname = args.pipeline
    plconf = ConfigPack.get_config("pipeline", plname)
    pipeline = Pipeline(args.pipeline, plconf)
    # asyncio.run(pipeline.start(interactive=args.interactive), debug=True)


if __name__ == "__main__":
    main()
