from typing import Dict, Set, Optional, List
from collections import deque


class DependencyGraph:
    def __init__(self):
        self.graph: Dict[str, Set[str]] = {}
        self.processed_packages: Set[str] = set()  # Для отслеживания уже обработанных пакетов
    
    def add_dependency(self, package: str, dependency: str):
        """Добавляет зависимость в граф."""
        if package not in self.graph:
            self.graph[package] = set()
        if dependency:  # Добавляем только если dependency не пустая
            self.graph[package].add(dependency)
    
    def bfs_with_recursion(self, start_package: str, max_depth: int, repository_url: str, 
                          current_depth: int = 0, visited: Optional[Set[str]] = None) -> Set[str]:
        """
        BFS с рекурсией для построения графа зависимостей.
        """
        if visited is None:
            visited = set()
        
        # Проверка максимальной глубины
        if current_depth >= max_depth:
            print(f"{'  ' * current_depth}  Max depth reached for {start_package}")
            return visited
        
        # Проверка циклических зависимостей
        if start_package in visited:
            print(f"{'  ' * current_depth}  Cyclic dependency detected: {start_package}")
            return visited
        
        visited.add(start_package)
        print(f"{'  ' * current_depth} Processing {start_package} (depth: {current_depth})")
        
        try:
            # Получаем зависимости текущего пакета
            from npm_parser import fetch_npm_metadata, extract_dependencies
            
            # Для корневого пакета используем переданную версию, для зависимостей - latest
            version_to_use = "latest"  # Всегда используем latest для зависимостей
            
            metadata = fetch_npm_metadata(start_package, version_to_use, repository_url)
            dependencies = extract_dependencies(metadata)
            
            print(f"{'  ' * current_depth}   Dependencies found: {len(dependencies)}")
            
            for dep_name, dep_version in dependencies.items():
                self.add_dependency(start_package, dep_name)
                print(f"{'  ' * current_depth}    {dep_name}")
                
                # Рекурсивный вызов для зависимостей
                if dep_name not in visited:
                    self.bfs_with_recursion(
                        dep_name, max_depth, repository_url, 
                        current_depth + 1, visited
                    )
                else:
                    print(f"{'  ' * current_depth}    Already visited: {dep_name}")
                    
        except Exception as e:
            print(f"{'  ' * current_depth} Error processing {start_package}: {e}")
        
        return visited
    
    def bfs_iterative(self, start_package: str, max_depth: int, repository_url: str) -> Set[str]:
        """
        Альтернативная реализация BFS без рекурсии (для сравнения).
        """
        visited = set()
        queue = deque([(start_package, 0)])  # (package, depth)
        
        while queue:
            current_package, depth = queue.popleft()
            
            if current_package in visited:
                print(f"  Cyclic dependency detected: {current_package}")
                continue
                
            if depth >= max_depth:
                print(f"  Max depth reached for {current_package}")
                continue
            
            visited.add(current_package)
            print(f" Processing {current_package} (depth: {depth})")
            
            try:
                from npm_parser import fetch_npm_metadata, extract_dependencies
                metadata = fetch_npm_metadata(current_package, "latest", repository_url)
                dependencies = extract_dependencies(metadata)
                
                print(f"   Dependencies found: {len(dependencies)}")
                
                for dep_name, dep_version in dependencies.items():
                    self.add_dependency(current_package, dep_name)
                    print(f"    {dep_name}")
                    
                    if dep_name not in visited:
                        queue.append((dep_name, depth + 1))
                    else:
                        print(f"    Already visited: {dep_name}")
                        
            except Exception as e:
                print(f" Error processing {current_package}: {e}")
        
        return visited
    
    def get_all_dependencies(self) -> Dict[str, Set[str]]:
        """Возвращает весь граф зависимостей."""
        return self.graph
    
    def has_cycles(self) -> bool:
        """Проверка на наличие циклов в графе."""
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
        """Красивый вывод графа."""
        if not self.graph:
            print("  (graph is empty)")
            return
            
        print("\n Final dependency graph:")
        for package, dependencies in sorted(self.graph.items()):
            if dependencies:
                print(f"  {package} -> {', '.join(sorted(dependencies))}")
            else:
                print(f"  {package} -> (no dependencies)")