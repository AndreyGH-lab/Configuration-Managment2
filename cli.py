import argparse
from npm_parser import fetch_npm_metadata, extract_dependencies, parse_test_repository
from dependency_graph import DependencyGraph
from npm_comparison import NPMComparator
from visualizer import GraphVisualizer


def main() -> None:
    parser = argparse.ArgumentParser(
        description="NPM dependency visualizer (Variant 20)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument("--package", required=True, help="Name of the package to analyze")
    parser.add_argument("--repository", required=True, help="Repository URL or path to test repository file")
    parser.add_argument("--test-mode", action="store_true", default=False, help="Enable test repository mode")
    parser.add_argument("--version", default="latest", help="Package version to analyze")
    parser.add_argument("--output", default="graph.png", help="Name of the generated graph image file")
    parser.add_argument("--max-depth", type=int, default=3, help="Maximum dependency analysis depth")
    parser.add_argument("--algorithm", choices=["bfs-recursive", "bfs-iterative"], default="bfs-recursive", help="Algorithm for graph traversal")
    parser.add_argument("--show-load-order", action="store_true", default=False, help="Show dependency load order (Stage 4)")
    parser.add_argument("--compare-with-npm", action="store_true", default=False, help="Compare with real NPM (Stage 4)")
    parser.add_argument("--visualize", action="store_true", default=False, help="Generate visualization (Stage 5)")
    
    args = parser.parse_args()

    print("=== Configuration Parameters ===")
    print(f"package = {args.package}")
    print(f"repository = {args.repository}")
    print(f"test_mode = {args.test_mode}")
    print(f"version = {args.version}")
    print(f"output = {args.output}")
    print(f"max_depth = {args.max_depth}")
    print(f"algorithm = {args.algorithm}")
    print(f"show_load_order = {args.show_load_order}")
    print(f"compare_with_npm = {args.compare_with_npm}")
    print(f"visualize = {args.visualize}")
    print("================================\n")

    print("--- Stage 2 & 3: Dependency Graph Construction ---")
    
    graph = DependencyGraph()
    visualizer = GraphVisualizer()
    
    if args.test_mode:
        print(f"Test mode: using file {args.repository}")
        try:
            test_repo = parse_test_repository(args.repository)
            print(f"Loaded test repository with {len(test_repo)} packages")
            
            if args.package not in test_repo:
                print(f"Error: Package '{args.package}' not found in test repository")
                print(f"Available packages: {', '.join(sorted(test_repo.keys()))}")
                return 1
            
            visited = graph.bfs_test_mode(
                start_package=args.package,
                max_depth=args.max_depth,
                test_repo=test_repo
            )
            
            print(f"\nGraph construction completed!")
            print(f"Total packages processed: {len(visited)}")
            print(f"Total dependencies found: {sum(len(deps) for deps in graph.get_all_dependencies().values())}")
            
            if graph.has_cycles():
                print("Cycle detection: Cycles found in dependency graph!")
            else:
                print("Cycle detection: No cycles found.")
                
            graph.print_graph()
            
            # Этап 4: Порядок загрузки
            if args.show_load_order:
                graph.print_load_order()
            
            # Этап 5: Визуализация
            if args.visualize:
                print("\n" + "="*50)
                print("STAGE 5: VISUALIZATION")
                print("="*50)
                
                success = visualizer.visualize_graph(
                    graph.get_all_dependencies(),
                    args.output,
                    args.package
                )
                
                if success:
                    visualizer.compare_with_npm_visualization(args.package)
                
        except Exception as e:
            print(f"Error in test mode: {e}")
            return 1
    else:
        print(f"Real repository mode: {args.repository}")
        print(f"Algorithm: {args.algorithm}")
        
        try:
            if args.algorithm == "bfs-recursive":
                visited = graph.bfs_with_recursion(
                    start_package=args.package,
                    max_depth=args.max_depth,
                    repository_url=args.repository
                )
            else:
                visited = graph.bfs_with_recursion(
                    start_package=args.package,
                    max_depth=args.max_depth,
                    repository_url=args.repository
                )
            
            print(f"\nGraph construction completed!")
            print(f"Total packages processed: {len(visited)}")
            print(f"Total dependencies found: {sum(len(deps) for deps in graph.get_all_dependencies().values())}")
            
            if graph.has_cycles():
                print("Cycle detection: Cycles found in dependency graph!")
            else:
                print("Cycle detection: No cycles found.")
                
            graph.print_graph()
            
            # Этап 4: Дополнительные операции
            if args.show_load_order or args.compare_with_npm:
                print("\n" + "="*50)
                print("STAGE 4: ADDITIONAL OPERATIONS")
                print("="*50)
                
                if args.show_load_order:
                    graph.print_load_order()
                
                if args.compare_with_npm:
                    comparator = NPMComparator()
                    
                    print("\nGetting actual NPM install order...")
                    npm_order = comparator.get_actual_npm_install_order(args.package, args.version)
                    
                    if npm_order:
                        our_order = graph.get_load_order()
                        comparison = comparator.compare_orders(our_order, npm_order)
                        comparator.explain_differences(comparison, our_order, npm_order)
                    else:
                        print("Failed to get NPM install order")
            
            # Этап 5: Визуализация
            if args.visualize:
                print("\n" + "="*50)
                print("STAGE 5: VISUALIZATION")
                print("="*50)
                
                success = visualizer.visualize_graph(
                    graph.get_all_dependencies(),
                    args.output,
                    args.package
                )
                
                if success:
                    visualizer.compare_with_npm_visualization(args.package)
                
        except Exception as e:
            print(f"Error during graph construction: {e}")
            return 1
        
    return 0


if __name__ == "__main__":
    exit(main())