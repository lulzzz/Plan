
from generic import etl_utils

class WorkflowControl():
    r"""
    Execute workflow sequencially according to configuration list
    Has scanner for detecting source file changes and do automatic adjustments
    """

    # Scan source file
    def __init__(self, source_file):
        self.source_file = source_file
        self.table_chain_list = list()

    def field_selection(input, field_list):
        SQL alchemy select from database table

        insert into table2
        select a,b,c from table 1
        field_list = [a,b,c]

        return 'table2'


    def execute(self):
        r"""
        Execute workflow sequencially
        """
        pass
