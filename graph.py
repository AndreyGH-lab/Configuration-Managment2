from typing import Dict, Set, List, Optional
from collections import deque
import json


class DependencyGraph:
    def __init__(self):
        self.graph: Dict[str, Set[str]] = {}
        self.visited: Set[str] = set()
    
    def add_dependency(self, package: str, dependency: str):
        if package not in self.graph:
            self.graph[package] = set()
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
            return visited
        
        # Проверка циклических зависимостей
        if start_package in visited:
            print(f"Cyclic dependency detected: {start_package}")
            return visited
        
        visited.add(start_package)
        print(f"{'  ' * current_depth} {start_package} (depth: {current_depth})")
        
        try:
            # Получаем зависимости текущего пакета
            from npm_parser import fetch_npm_metadata, extract_dependencies
            metadata = fetch_npm_metadata(start_package, "latest", repository_url)
            dependencies = extract_dependencies(metadata)
            
            for dep_name, dep_version in dependencies.items():
                self.add_dependency(start_package, dep_name)
                
                # Рекурсивный вызов для зависимостей
                if dep_name not in visited:
                    self.bfs_with_recursion(
                        dep_name, max_depth, repository_url, 
                        current_depth + 1, visited
                    )
                    
        except Exception as e:
            print(f"{'  ' * current_depth} Error processing {start_package}: {e}")
        
        return visited
    
    def get_all_dependencies(self) -> Dict[str, Set[str]]:
        return self.graph
    
    def has_cycles(self) -> bool:
        """Проверка на наличие циклов в графе."""
        def dfs(node, path):
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