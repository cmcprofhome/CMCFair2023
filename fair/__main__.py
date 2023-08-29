import argparse
from typing import Optional

from fair.config import load_config, Config


def define_arg_parser():
    parser = argparse.ArgumentParser(description='Launch fair bot.')
    parser.add_argument('config_path', metavar='Config path', type=str, help='path to the config file')
    parser.add_argument('-e', '--use-env-vars', action='store_true', help='override config with env vars')
    parser.add_argument(
        '-m',
        dest='config_env_mapping_path',
        metavar='<mapping path>',
        type=str,
        help='path to the config env mapping file'
    )
    return parser


def main(config_path: str, use_env_vars: bool, config_env_mapping_path: Optional[str] = None):
    cfg = load_config(config_path, use_env_vars, config_env_mapping_path)
    print(cfg)


if __name__ == '__main__':
    arg_parser = define_arg_parser()
    args = arg_parser.parse_args()
    main(args.config_path, args.use_env_vars, args.config_env_mapping_path)
