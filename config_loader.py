from dataclasses import dataclass
import yaml
import os

@dataclass
class AppConfig:
    package: str
    version: str
    output_file: str = "graph.png"
    ascii_tree: bool = False
    max_depth: int = 5
    filter: str = ""
    test_mode: bool = False

def load_config(path: str) -> AppConfig:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    required = ["package", "version"]
    missing = [k for k in required if k not in data]
    if missing:
        raise ValueError(f"Missing required keys in config: {', '.join(missing)}")

    return AppConfig(
        package=str(data["package"]),
        version=str(data["version"]),
        output_file=str(data.get("output_file", "graph.png")),
        ascii_tree=bool(data.get("ascii_tree", False)),
        max_depth=int(data.get("max_depth", 5)),
        filter=str(data.get("filter", "")),
        test_mode=bool(data.get("test_mode", False)),
    )
