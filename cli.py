import argparse
from npm_parser import fetch_npm_metadata, extract_dependencies, parse_test_repository, get_dependencies_from_test_repo
from dependency_graph import DependencyGraph


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
        default=3,
        help="Maximum dependency analysis depth"
    )
    parser.add_argument(
        "--algorithm",
        choices=["bfs-recursive", "bfs-iterative"],
        default="bfs-recursive",
        help="Algorithm for graph traversal"
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
    print(f"algorithm = {args.algorithm}")
    print("================================\n")

    # Этап 2 и 3: Построение графа зависимостей
    print("--- Stage 2 & 3: Dependency Graph Construction ---")
    
    graph = DependencyGraph()
    
    if args.test_mode:
        # Режим тестирования - работа с файлом
        print(f" Test mode: using file {args.repository}")
        try:
            test_repo = parse_test_repository(args.repository)
            print(f"Loaded test repository with {len(test_repo)} packages")
            
            # TODO: Реализовать BFS для тестовых данных
            print("Test mode BFS will be implemented in next iteration")
            
        except Exception as e:
            print(f"Error in test mode: {e}")
            return 1
    else:
        # Режим реального репозитория
        print(f" Real repository mode: {args.repository}")
        print(f" Algorithm: {args.algorithm}")
        
        try:
            if args.algorithm == "bfs-recursive":
                visited = graph.bfs_with_recursion(
                    start_package=args.package,
                    max_depth=args.max_depth,
                    repository_url=args.repository
                )
            else:
                visited = graph.bfs_iterative(
                    start_package=args.package,
                    max_depth=args.max_depth,
                    repository_url=args.repository
                )
            
            print(f"\n Graph construction completed!")
            print(f"Total packages processed: {len(visited)}")
            print(f"Total dependencies found: {sum(len(deps) for deps in graph.get_all_dependencies().values())}")
            
            # Проверка на циклы
            if graph.has_cycles():
                print(" Cycle detection: Cycles found in dependency graph!")
            else:
                print(" Cycle detection: No cycles found.")
                
            # Вывод итогового графа
            graph.print_graph()
                
        except Exception as e:
            print(f"Error during graph construction: {e}")
            return 1
        
    return 0


if __name__ == "__main__":
    exit(main())