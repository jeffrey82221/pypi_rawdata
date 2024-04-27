import sys
from main import etl_obj
from batch_framework.adaptor import GithubActionAdaptor
    
if __name__ == '__main__':
    adaptor = GithubActionAdaptor(etl_group=etl_obj)
    task_id = sys.argv[1]
    if task_id == 'whole':
        etl_obj.execute(max_active_run=16)
    else:
        adaptor.run_by_id(task_id)
    