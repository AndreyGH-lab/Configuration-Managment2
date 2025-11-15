import json
import urllib.request


def fetch_npm_metadata(package: str, version: str) -> dict:
    """
    Загружает JSON метаданные npm-пакета.
    """
    url = f"https://registry.npmjs.org/{package}/{version}"
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
