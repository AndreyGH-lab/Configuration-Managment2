# cli.py

import argparse
from config_loader import load_config

def main() -> None:
    parser = argparse.ArgumentParser(description="NuGet dependency visualizer (Variant 20)")
    parser.add_argument("--config", required=True, help="Path to YAML config")

    args = parser.parse_args()
    cfg = load_config(args.config)

    # Этап 1: вывод всех параметров
    print(f"package = {cfg.package}")
    print(f"version = {cfg.version}")
    print(f"output_file = {cfg.output_file}")
    print(f"ascii_tree = {cfg.ascii_tree}")
    print(f"max_depth = {cfg.max_depth}")
    print(f"filter = {cfg.filter}")
    print(f"test_mode = {cfg.test_mode}")

if __name__ == "__main__":
    main()
