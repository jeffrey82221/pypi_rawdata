"""
Convert requires_dist to 
mapping of required_package to suitable versions
"""
from typing import List, Optional, Tuple, Dict
from pip._vendor.distlib.util import parse_requirement
from pip._vendor.distlib.locators import PyPIJSONLocator
from pip._vendor.distlib import DistlibException

def get_dist(dist_str) -> Tuple[str, List[str]]:
    try:
        name = parse_requirement(dist_str).name
        dists = PyPIJSONLocator('https://pypi.org/pypi/').get_project(name)
        versions = [key for key in dists if key not in ['urls', 'digests']]
        results = []
        for version in versions:
            if dists[version].matches_requirement(dist_str):
                results.append(version)
        return (name, results)
    except DistlibException:
        return (dist_str, None)

def enrich_requires_dist(requires_dist: Optional[List[str]]) -> Dict[str, List[str]]:
    if requires_dist is not None:
        return dict([get_dist(dist_str) for dist_str in requires_dist])
    else:
        return None