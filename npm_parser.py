import json
import urllib.request
import urllib.error
from typing import Dict, Set


def fetch_npm_metadata(package: str, version: str, repository_url: str) -> dict:
    """
    Загружает JSON метаданные npm-пакета.
    """
    base_url = repository_url.rstrip('/')
    
    if version == "latest":
        url = f"{base_url}/{package}"
    else:
        url = f"{base_url}/{package}/{version}"
        
    print(f"Downloading: {url}")

    try:
        with urllib.request.urlopen(url) as response:
            data = response.read()
            return json.loads(data)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise RuntimeError(f"Package '{package}' or version '{version}' not found in repository.") from e
        else:
            raise RuntimeError(f"HTTP Error {e.code}: {e.reason}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error: {e.reason}") from e
    except Exception as e:
        raise RuntimeError(f"Failed to fetch metadata: {e}") from e


def extract_dependencies(metadata: dict) -> dict:
    """
    Извлекает прямые зависимости из npm JSON.
    """
    deps = {}
    

    if "dependencies" in metadata:
        deps = metadata["dependencies"]
        print(f"   Found dependencies in root: {len(deps)}")
    

    elif "versions" in metadata and "dist-tags" in metadata:
        latest_version = metadata["dist-tags"].get("latest")
        if latest_version and latest_version in metadata["versions"]:
            version_data = metadata["versions"][latest_version]
            if "dependencies" in version_data:
                deps = version_data["dependencies"]
                print(f"   Found dependencies in versions/{latest_version}: {len(deps)}")
    
    if deps:
        print(f"   Dependencies: {list(deps.keys())}")
    else:
        print(f"   No dependencies found")
        
    return deps


def parse_test_repository(file_path: str) -> Dict[str, Set[str]]:
    """
    Парсит тестовый репозиторий из файла.
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