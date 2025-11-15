from typing import Dict, Set, Optional, List


class DependencyGraph:
    def __init__(self):
        self.graph: Dict[str, Set[str]] = {}
    
    def add_dependency(self, package: str, dependency: str):
        if package not in self.graph:
            self.graph[package] = set()
        if dependency:
            self.graph[package].add(dependency)
    
    def bfs_with_recursion(self, start_package: str, max_depth: int, repository_url: str, current_depth: int = 0, visited: Optional[Set[str]] = None) -> Set[str]:
        if visited is None:
            visited = set()
        
        if current_depth >= max_depth:
            print(f"{'  ' * current_depth}Max depth reached for {start_package}")
            return visited
        
        if start_package in visited:
            print(f"{'  ' * current_depth}Cyclic dependency detected: {start_package}")
            return visited
        
        visited.add(start_package)
        print(f"{'  ' * current_depth}Processing {start_package} (depth: {current_depth})")
        
        try:
            from npm_parser import fetch_npm_metadata, extract_dependencies
            
            metadata = fetch_npm_metadata(start_package, "latest", repository_url)
            dependencies = extract_dependencies(metadata)
            
            print(f"{'  ' * current_depth}Dependencies found: {len(dependencies)}")
            
            for dep_name, dep_version in dependencies.items():
                self.add_dependency(start_package, dep_name)
                print(f"{'  ' * current_depth}+ {dep_name}")
                
                if dep_name not in visited:
                    self.bfs_with_recursion(
                        dep_name, max_depth, repository_url, 
                        current_depth + 1, visited
                    )
                else:
                    print(f"{'  ' * current_depth}Already visited: {dep_name}")
                    
        except Exception as e:
            print(f"{'  ' * current_depth}Error processing {start_package}: {e}")
        
        return visited
    
    def bfs_test_mode(self, start_package: str, max_depth: int, test_repo: Dict[str, Set[str]], current_depth: int = 0, visited: Optional[Set[str]] = None) -> Set[str]:
        if visited is None:
            visited = set()
        
        if current_depth >= max_depth:
            print(f"{'  ' * current_depth}Max depth reached for {start_package}")
            return visited
        
        if start_package in visited:
            print(f"{'  ' * current_depth}Cyclic dependency detected: {start_package}")
            return visited
        
        visited.add(start_package)
        print(f"{'  ' * current_depth}Processing {start_package} (depth: {current_depth})")
        
        dependencies = test_repo.get(start_package, set())
        
        print(f"{'  ' * current_depth}Dependencies found: {len(dependencies)}")
        
        for dep_name in dependencies:
            self.add_dependency(start_package, dep_name)
            print(f"{'  ' * current_depth}+ {dep_name}")
            
            if dep_name not in visited:
                self.bfs_test_mode(
                    dep_name, max_depth, test_repo,
                    current_depth + 1, visited
                )
            else:
                print(f"{'  ' * current_depth}Already visited: {dep_name}")
        
        return visited
    
    def get_load_order(self) -> List[str]:
        """
        Возвращает порядок загрузки зависимостей (топологическая сортировка).
        """
        visited = set()
        temp_visited = set()
        result = []
        
        def visit(node: str):
            if node in temp_visited:
                raise RuntimeError(f"Cyclic dependency detected at node: {node}")
            if node in visited:
                return
                
            temp_visited.add(node)
            
            # Рекурсивно посещаем все зависимости
            if node in self.graph:
                for neighbor in sorted(self.graph[node]):
                    visit(neighbor)
            
            temp_visited.remove(node)
            visited.add(node)
            result.append(node)
        
        # Посещаем все узлы графа
        for node in sorted(self.graph.keys()):
            if node not in visited:
                visit(node)
        
        return result
    
    def print_load_order(self):
        """
        Выводит порядок загрузки зависимостей.
        """
        try:
            load_order = self.get_load_order()
            print("\nDependency load order:")
            for i, package in enumerate(load_order, 1):
                print(f"  {i:2d}. {package}")
        except RuntimeError as e:
            print(f"\nError in load order calculation: {e}")
    
    def get_all_dependencies(self) -> Dict[str, Set[str]]:
        return self.graph
    
    def has_cycles(self) -> bool:
        def dfs(node: str, path: Set[str]) -> bool:
            if node in path:
                return True
            if node not in self.graph:
                return False
            
            path.add(node)
            for neighbor in self.graph[node]:
                if dfs(neighbor, path.copy()):
                    return True
            return False
        
        for node in self.graph:
            if dfs(node, set()):
                return True
        return False
    
    def print_graph(self):
        if not self.graph:
            print("  (graph is empty)")
            return
            
        print("\nFinal dependency graph:")
        for package, dependencies in sorted(self.graph.items()):
            if dependencies:
                print(f"  {package} -> {', '.join(sorted(dependencies))}")
            else:
                print(f"  {package} -> (no dependencies)")