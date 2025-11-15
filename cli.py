
from nuget_parser import download_nupkg, extract_nuspec, parse_dependencies
import os

import argparse
from config_loader import load_config

def main() -> None:
    parser = argparse.ArgumentParser(description="NuGet dependency visualizer (Variant 20)")
    parser.add_argument("--config", required=True, help="Path to YAML config")

    args = parser.parse_args()
    cfg = load_config(args.config)


    print(f"package = {cfg.package}")
    print(f"version = {cfg.version}")
    print(f"output_file = {cfg.output_file}")
    print(f"ascii_tree = {cfg.ascii_tree}")
    print(f"max_depth = {cfg.max_depth}")
    print(f"filter = {cfg.filter}")
    print(f"test_mode = {cfg.test_mode}")

    print("\n--- Stage 2: NuGet download + dependency parsing ---")

    nupkg_filename = f"{cfg.package}.{cfg.version}.nupkg"

    # 1. Скачиваем .nupkg
    download_nupkg(cfg.package, cfg.version, nupkg_filename)

    # 2. Извлекаем .nuspec
    nuspec_xml = extract_nuspec(nupkg_filename)

    # 3. Парсим зависимости
    deps = parse_dependencies(nuspec_xml)

    print("\nDependencies:")
    if not deps:
        print("No dependencies found.")
    else:
        for pkg, ver in deps:
            print(f"- {pkg} ({ver})")


if __name__ == "__main__":
    main()
