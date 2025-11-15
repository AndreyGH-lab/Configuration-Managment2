import urllib.request
import zipfile
import xml.etree.ElementTree as ET


def download_nupkg(package: str, version: str, output_path: str) -> str:
    """
    Скачивает NuGet-пакет .nupkg вручную.
    """
    url = f"https://api.nuget.org/v3-flatcontainer/{package.lower()}/{version}/{package.lower()}.{version}.nupkg"
    print(f"Downloading: {url}")

    try:
        urllib.request.urlretrieve(url, output_path)
        return output_path
    except Exception as e:
        raise RuntimeError(f"Failed to download .nupkg: {e}")


def extract_nuspec(nupkg_path: str) -> str:
    """
    Извлекает .nuspec из .nupkg (ZIP).
    """
    if not zipfile.is_zipfile(nupkg_path):
        raise ValueError("Downloaded file is not a valid ZIP (.nupkg)")

    with zipfile.ZipFile(nupkg_path, "r") as z:
        nuspec_name = None
        for name in z.namelist():
            if name.endswith(".nuspec"):
                nuspec_name = name
                break

        if nuspec_name is None:
            raise RuntimeError("No .nuspec file found in nupkg")

        with z.open(nuspec_name) as f:
            return f.read().decode("utf-8")


def parse_dependencies(nuspec_xml: str) -> list[tuple[str, str]]:
    """
    Парсит зависимости из .nuspec XML.
    Учитывает:
    - namespace
    - <group>
    - прямые <dependency>
    """
    root = ET.fromstring(nuspec_xml)


    ns = ""
    if root.tag.startswith("{"):
        ns = root.tag.split("}")[0] + "}"

    # пробуем достать metadata
    metadata = root.find(f"./{ns}metadata")
    if metadata is None:
        return []

    deps_section = metadata.find(f"{ns}dependencies")
    if deps_section is None:
        return []

    result = []


    for dep in deps_section.findall(f"{ns}dependency"):
        pkg = dep.attrib.get("id")
        ver = dep.attrib.get("version", "")
        if pkg:
            result.append((pkg, ver))


    for group in deps_section.findall(f"{ns}group"):
        for dep in group.findall(f"{ns}dependency"):
            pkg = dep.attrib.get("id")
            ver = dep.attrib.get("version", "")
            if pkg:
                result.append((pkg, ver))

    return result
