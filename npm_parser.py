import json
import urllib.request
from typing import Dict, Set

def fetch_npm_metadata(package: str, version: str, repository_url: str) -> dict:
    url = f"{repository_url}/{package}/{version}"
    print(f"Downloading: {url}")

    try:
        with urllib.request.urlopen(url) as response:
            data = response.read()
            return json.loads(data)
    except Exception as e:
        raise RuntimeError(f"Failed to fetch metadata: {e}")


def extract_dependencies(metadata: dict) -> dict:
    """
    Извлекает прямые зависимости из npm JSON.
    """
    deps = metadata.get("dependencies", {})
    return deps

def parse_test_repository(file_path: str) -> Dict[str, Set[str]]:
    """
    Парсит тестовый репозиторий из файла.
    Формат: каждая строка 'ПАКЕТ: ЗАВИСИМОСТЬ1, ЗАВИСИМОСТЬ2, ...'
    """
    graph = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                if ':' in line:
                    package, deps_str = line.split(':', 1)
                    package = package.strip()
                    dependencies = {dep.strip() for dep in deps_str.split(',') if dep.strip()}
                    
                    graph[package] = dependencies
                    
        return graph
    except Exception as e:
        raise RuntimeError(f"Failed to parse test repository: {e}")


def get_dependencies_from_test_repo(package: str, test_repo: Dict[str, Set[str]]) -> Dict[str, str]:
    """
    Получает зависимости пакета из тестового репозитория.
    """
    if package in test_repo:
        # Для тестового репозитория возвращаем фиктивные версии
        return {dep: "test-version" for dep in test_repo[package]}
    return {}

def extract_dependencies(metadata: dict) -> dict:
    """
    Извлекает прямые зависимости из npm JSON.
    """
    print(f"    Available keys in metadata: {list(metadata.keys())}")
    
    deps = metadata.get("dependencies", {})
    print(f"    Dependencies found: {deps}")
    
    # Также проверим другие возможные места с зависимостями
    if "versions" in metadata:
        latest_version = metadata.get("dist-tags", {}).get("latest")
        if latest_version and latest_version in metadata["versions"]:
            version_data = metadata["versions"][latest_version]
            if "dependencies" in version_data:
                deps = version_data["dependencies"]
                print(f"    Found dependencies in versions/latest: {deps}")
    
    return deps