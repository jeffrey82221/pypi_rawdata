"""
Main ETL Class
"""
from typing import Optional, List
import vaex as vx
import pandas as pd
from batch_framework.filesystem import LocalBackend
from batch_framework.storage import PandasStorage, VaexStorage
from batch_framework.etl import ETLGroup, ObjProcessor
from batch_framework.parallize import MapReduce
from .trigger import PyPiNameTrigger
from .crawl import (
    LatestDownloader,
    LatestUpdator
)
from .tabularize import LatestTabularize


class NewPackageExtractor(ObjProcessor):
    def __init__(self, *args, **kwargs):
        kwargs['make_cache'] = True
        super().__init__(*args, **kwargs)

    @property
    def input_ids(self):
        return ['name_trigger']

    @property
    def output_ids(self):
        return ['name_trigger_new']

    def transform(self, inputs: List[vx.DataFrame],
                  **kwargs) -> List[vx.DataFrame]:
        pkg_name_df = inputs[0]
        print('Size of pkg_name:', len(pkg_name_df))
        if self.exists_cache:
            pkg_name_cache_df = self.load_cache(self.input_ids[0])
            print('Size of cached pkg_name:', len(pkg_name_cache_df))
            new_pkg_names = self._get_new_package_names(
                pkg_name_df, pkg_name_cache_df)
            print('number of new packages:', len(new_pkg_names))
            # assert len(new_pkg_names) > 0, 'Should have new package'
            if len(new_pkg_names) == 0:
                new_pkg_names = pkg_name_cache_df.head(64)['name'].tolist()
            return [vx.from_pandas(pd.DataFrame(
                new_pkg_names, columns=['name']))]
        else:
            return inputs

    def _get_new_package_names(
            self, pkg_name_df: vx.DataFrame, cache_pkg_name_df: vx.DataFrame) -> List[str]:
        pkg_names = pkg_name_df[['name']].to_arrays(array_type='list')[0]
        cache_pkg_names = cache_pkg_name_df[['name']].to_arrays(array_type='list')[
            0]
        new_names = list(set(pkg_names) - set(cache_pkg_names))
        return new_names


class SimplePyPiCanonicalize(ETLGroup):
    def __init__(self, raw_df: LocalBackend,
                 tmp_fs: LocalBackend,
                 output_fs: LocalBackend,
                 partition_fs: LocalBackend,
                 download_worker_count: int = 1,
                 update_worker_count: int = 16,
                 test_count: Optional[int] = None,
                 do_update: bool = True):
        self._tmp_fs = tmp_fs
        units = [
            PyPiNameTrigger(PandasStorage(tmp_fs), test_count=test_count),
            NewPackageExtractor(VaexStorage(tmp_fs)),
            MapReduce(
                LatestDownloader(PandasStorage(tmp_fs)),
                download_worker_count,
                partition_fs
            )
        ]
        self.updator = LatestUpdator(
            VaexStorage(tmp_fs),
            VaexStorage(raw_df),
            do_update=do_update,
            workers=update_worker_count
        )
        units.extend([
            self.updator
        ])
        units.append(
            LatestTabularize(
                input_storage=PandasStorage(raw_df),
                output_storage=PandasStorage(output_fs)
            )
        )
        super().__init__(*units)

    @property
    def input_ids(self):
        return []

    @property
    def output_ids(self):
        return ['latest_package', 'latest_requirement', 'latest_url']
