
"""
Download Latest Json for all package on PyPi
"""
from typing import List, Dict, Tuple, Optional
import requests
import pandas as pd
import vaex as vx
import tqdm
import time
import json
from concurrent.futures import ThreadPoolExecutor
from batch_framework.etl import ObjProcessor
from .pip_util import enrich_requires_dist

RETRIES_COUNT = 3


def process_latest(data: Dict) -> Dict:
    results = dict()
    results['info'] = data['info']
    results['num_releases'] = len(data['releases'])
    if data['info']['requires_dist'] is not None:
        results['num_info_dependencies'] = len(data['info']['requires_dist'])
        results['requires'] = enrich_requires_dist(data['info']['requires_dist'])
    else:
        results['num_info_dependencies'] = 0
        results['requires'] = None
    return results


class LatestDownloader(ObjProcessor):
    """
    Crawl PyPi Instance that haven't been downloaded yet
    """
    @property
    def input_ids(self):
        return ['name_trigger_new']

    @property
    def output_ids(self):
        return ['latest_new']

    def transform(self, inputs: List[pd.DataFrame],
                  **kwargs) -> List[pd.DataFrame]:
        assert len(inputs[0]) > 0, 'input table should have size > 0'
        new_df = self._get_new_package_records(inputs[0].name.tolist())
        assert 'name' in new_df.columns
        assert 'latest' in new_df.columns
        assert 'etag' in new_df.columns
        assert len(new_df.columns) == 3
        new_df['latest'] = new_df['latest'].map(json.dumps)
        return [new_df]

    def _get_new_package_records(self, names: List[str]) -> pd.DataFrame:
        """Download new latest json data for a list of package names
        Args:
            names: Names of packages

        Returns:
            DataFrame with columns
                - name: Name of package
                - latest: Latest Json
                - etag: etag
        """
        results = []
        for i, name in enumerate(
                tqdm.tqdm(names, desc='get_new_package_records')):
            url = f"https://pypi.org/pypi/{name}/json"
            res = self.call_api(url)
            if res.status_code == 404:
                continue
            assert res.status_code == 200, f'response status code is {res.status_code}'
            latest = res.json()
            latest = process_latest(latest)
            etag = res.headers["ETag"]
            results.append((name, latest, etag))
        return pd.DataFrame.from_records(
            results, columns=['name', 'latest', 'etag'])

    def call_api(self, url):
        for i in range(RETRIES_COUNT):
            try:
                res = requests.get(url)
                return res
            except requests.exceptions.ConnectionError:
                print(f'ConnectionError happend on {i}th package download')
                time.sleep(5)


class LatestUpdator(ObjProcessor):
    """
    Update PyPi Instances that have already been downloaded
    and upsert them into the cached PyPi data.
    """

    def __init__(self, *args, **kwargs):
        kwargs['make_cache'] = True
        self._do_update = kwargs['do_update']
        self._workers = kwargs['workers']
        del kwargs['do_update']
        del kwargs['workers']
        super().__init__(*args, **kwargs)

    @property
    def input_ids(self):
        return ['latest_new']

    @property
    def output_ids(self):
        return ['latest']

    def transform(self, inputs: List[vx.DataFrame],
                  **kwargs) -> List[vx.DataFrame]:
        if not self.exists_cache:
            return [inputs[0]]
        else:
            if self._do_update:
                # 1. load cached name and etag
                latest_cache = self.load_cache(self.output_ids[0])[
                    'name', 'etag'].to_pandas_df()
                # 2. update latest_cache based on name and etag pandas
                # dataframe
                latest_cache['partition'] = latest_cache.index.map(
                    lambda x: str(x % self._workers))
                with ThreadPoolExecutor(max_workers=self._workers) as executor:
                    updated_latest_chunks = executor.map(
                        self._get_updated_package_records,
                        [x[1] for x in latest_cache.groupby('partition')])
                updated_latest = pd.concat(updated_latest_chunks)
                print('Total Updated Count:', len(updated_latest))
                # 3. Append updated_latest (pd), latest_new (vx), latest_cache
                # (vx)
                latest = vx.concat([
                    vx.from_pandas(updated_latest),
                    inputs[0],
                    # select those not in updated_latest
                    self.load_cache(self.output_ids[0])
                ]).to_pandas_df()
                # 4. Do dedupe operation on combined vaex dataframe
                latest.drop_duplicates(
                    subset=['name'], keep='first', inplace=True)
                return [vx.from_pandas(latest)]
            else:
                latest = vx.concat([
                    inputs[0],
                    self.load_cache(self.output_ids[0])
                ])
                return [latest]

    def _get_updated_package_records(
            self, latest_df: pd.DataFrame) -> pd.DataFrame:
        """Get the update latest records
        Args:
            latest_df (DataFrame with columns):
                - name: Name of package
                - latest: Latest Json
                - etag: etag
                - partition: for labeling which chunk is used
        Returns:
            new_df (Schema same as latest_df but only holds name of updated records)
        """
        total = len(latest_df)
        partition = latest_df.partition.unique().tolist()[0]
        name_etag_pipe = zip(latest_df.name.tolist(), latest_df.etag.tolist())
        update_pipe = map(
            lambda x: self._update_with_etag(
                x[0], x[1]), name_etag_pipe)
        update_pipe = tqdm.tqdm(
            update_pipe,
            total=total,
            desc=f'update_with_etag ({partition})')
        update_pipe = filter(
            lambda x: isinstance(
                x,
                tuple) and len(x) == 3,
            update_pipe)
        update_pipe = map(
            lambda x: (
                x[0],
                process_latest(
                    x[1]),
                x[2]),
            update_pipe)
        new_df = pd.DataFrame.from_records(
            update_pipe, columns=['name', 'latest', 'etag'])
        new_df['latest'] = new_df['latest'].map(json.dumps)
        print(f'# of update in chunk ({partition}): {len(new_df)}')
        return new_df

    def _update_with_etag(
            self, name: str, etag: str) -> Optional[Tuple[Dict, str]]:
        """Update latest json data given package name and etag.
        (reduce repeat crawling of old data)

        Args:
            name (str): Name of package
            etag (str): Etag of the API call

        Returns:
            Optional[Tuple[Dict, str]]:
                - Dict: The resulting latest json
                - str: The etag of the API call
                (Not None if there is data difference)
        """
        url = f"https://pypi.org/pypi/{name}/json"
        for i in range(RETRIES_COUNT):
            try:
                res = requests.get(url, headers={"If-None-Match": etag})
                break
            except requests.exceptions.ConnectionError:
                time.sleep(5)
                print(f'ConnectionError Happened, Sleep and Retry #{i+1}')
        if res.status_code == 404:
            return '404'
        assert res.status_code in [
            200, 304], f'response status code is {res.status_code}'
        if res.status_code == 200:
            latest = res.json()
            etag = res.headers["ETag"]
            return name, latest, etag
        else:
            return '304'
