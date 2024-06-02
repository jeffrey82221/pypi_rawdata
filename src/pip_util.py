"""
Convert requires_dist to 
mapping of required_package to suitable versions
"""
from typing import List, Optional, Tuple, Dict
from pip._vendor.distlib.util import parse_requirement
from pip._vendor.distlib.locators import PyPIJSONLocator
from pip._vendor.distlib import DistlibException

def get_dist(dist_str) -> Tuple[str, Dict[str, List[str]]]:
    """
    Convert distribution pattern to actual list of distribution

    Args:
        - dist_str: 
            e.g., numpy>=1.9.0
    Returns:
        result: 
            item[0]: name of the package
            item[1]: dict
                key=releases (list) a list of releases versions
                key=contraints (list of tuple) parsed representation of version contraint
                    e.g., 'constraints': [('==', '1.9.3')]
                key=marker
                key=url
                key=requirement (same as dist_str)
    """
    try:
        name_space = parse_requirement(dist_str)
        name = name_space.name
        dists = PyPIJSONLocator('https://pypi.org/pypi/').get_project(name)
        versions = [key for key in dists if key not in ['urls', 'digests']]
        releases = []
        for version in versions:
            try:
                if dists[version].matches_requirement(dist_str):
                    releases.append(version)
            except BaseException:
                pass
        data = {
            'releases': releases,
            'extras': name_space.extras,
            'constraints': name_space.constraints,
            'marker': name_space.marker,
            'url': name_space.url,
            'requirement': name_space.requirement
        }
        return (name, data)
    except (DistlibException, SyntaxError):
        return (dist_str, None)

def enrich_requires_dist(requires_dist: Optional[List[str]]) -> Dict[str, List[str]]:
    if requires_dist is not None:
        return dict([get_dist(dist_str) for dist_str in requires_dist])
    else:
        return None