import subprocess
import json
import tempfile
import os
from typing import List, Set, Dict


class NPMComparator:
    def __init__(self):
        self.actual_install_order: List[str] = []
    
    def get_actual_npm_install_order(self, package: str, version: str = "latest") -> List[str]:
        """
        Получает реальный порядок установки зависимостей через npm.
        """
        try:
            # Создаем временную директорию для npm install
            with tempfile.TemporaryDirectory() as temp_dir:
                # Создаем package.json
                package_json = {
                    "name": "test-package",
                    "version": "1.0.0",
                    "dependencies": {
                        package: version
                    }
                }
                
                with open(os.path.join(temp_dir, "package.json"), "w") as f:
                    json.dump(package_json, f)
                
                # Запускаем npm install с выводом в JSON
                result = subprocess.run(
                    ["npm", "install", "--json"],
                    cwd=temp_dir,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    npm_output = json.loads(result.stdout)
                    return self._extract_install_order(npm_output)
                else:
                    print(f"npm install failed: {result.stderr}")
                    return []
                    
        except Exception as e:
            print(f"Error getting npm install order: {e}")
            return []
    
    def _extract_install_order(self, npm_output: dict) -> List[str]:
        """
        Извлекает порядок установки из вывода npm.
        """
        order = []
        
        def extract_from_deps(deps: dict):
            for dep_name, dep_info in deps.items():
                if dep_name not in order:
                    order.append(dep_name)
                if "dependencies" in dep_info:
                    extract_from_deps(dep_info["dependencies"])
        
        if "dependencies" in npm_output:
            extract_from_deps(npm_output["dependencies"])
        
        return order
    
    def compare_orders(self, our_order: List[str], npm_order: List[str]) -> Dict[str, any]:
        """
        Сравнивает наш порядок с порядком npm.
        """
        our_set = set(our_order)
        npm_set = set(npm_order)
        
        return {
            "common_packages": our_set & npm_set,
            "only_in_our_order": our_set - npm_set,
            "only_in_npm_order": npm_set - our_set,
            "order_matches": our_order == npm_order,
            "our_order_length": len(our_order),
            "npm_order_length": len(npm_order)
        }
    
    def explain_differences(self, comparison: Dict[str, any], our_order: List[str], npm_order: List[str]):
        """
        Объясняет расхождения между нашим порядком и порядком npm.
        """
        print("\n" + "="*60)
        print("COMPARISON WITH REAL NPM")
        print("="*60)
        
        print(f"\nOur load order: {len(our_order)} packages")
        print(f"NPM install order: {len(npm_order)} packages")
        
        print(f"\nCommon packages: {len(comparison['common_packages'])}")
        print(f"Only in our order: {len(comparison['only_in_our_order'])}")
        print(f"Only in NPM order: {len(comparison['only_in_npm_order'])}")
        
        if comparison["order_matches"]:
            print("\n Orders match perfectly!")
        else:
            print("\n Orders differ")
            
            if comparison['only_in_our_order']:
                print(f"\nPackages only in our order: {sorted(comparison['only_in_our_order'])}")
            
            if comparison['only_in_npm_order']:
                print(f"\nPackages only in NPM order: {sorted(comparison['only_in_npm_order'])}")
            
            # Анализ причин расхождений
            print("\nPossible reasons for differences:")
            print("1. NPM учитывает peerDependencies и optionalDependencies")
            print("2. NPM использует более сложный алгоритм разрешения версий")
            print("3. NPM может объединять дублирующиеся зависимости")
            print("4. Наш алгоритм использует простую топологическую сортировку")
            print("5. NPM учитывает package-lock.json и семантическое версионирование")