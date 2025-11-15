import argparse
from npm_parser import fetch_npm_metadata, extract_dependencies


def main() -> None:
    parser = argparse.ArgumentParser(
        description="NPM dependency visualizer (Variant 20)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Обязательные параметры
    parser.add_argument(
        "--package",
        required=True,
        help="Name of the package to analyze"
    )
    parser.add_argument(
        "--repository",
        required=True,
        help="Repository URL or path to test repository file"
    )
    
    # Опциональные параметры с значениями по умолчанию
    parser.add_argument(
        "--test-mode",
        action="store_true",
        default=False,
        help="Enable test repository mode"
    )
    parser.add_argument(
        "--version",
        default="latest",
        help="Package version to analyze"
    )
    parser.add_argument(
        "--output",
        default="graph.png",
        help="Name of the generated graph image file"
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=5,
        help="Maximum dependency analysis depth"
    )
    
    args = parser.parse_args()

    # Вывод всех параметров (требование этапа 1)
    print("=== Configuration Parameters ===")
    print(f"package = {args.package}")
    print(f"repository = {args.repository}")
    print(f"test_mode = {args.test_mode}")
    print(f"version = {args.version}")
    print(f"output = {args.output}")
    print(f"max_depth = {args.max_depth}")
    print("================================\n")

    # Этап 2: Извлечение зависимостей
    print("--- Stage 2: NPM Direct Dependency Extraction ---")
    
    try:
        metadata = fetch_npm_metadata(args.package, args.version)
        deps = extract_dependencies(metadata)

        print("\nDirect dependencies:")
        if not deps:
            print("No dependencies found.")
        else:
            for name, ver in deps.items():
                print(f"- {name}: {ver}")
                
    except Exception as e:
        print(f"Error during dependency extraction: {e}")
        return 1
        
    return 0


if __name__ == "__main__":
    exit(main())