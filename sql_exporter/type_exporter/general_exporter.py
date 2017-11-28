import sys


class GeneralExporter:
    FILE_NAME = '{s_name}.sql'

    # Create definition indexes
    NAME_IDX = 'Name'
    TYPE_IDX = 'Type'
    PK_IDX = 'PK'
    FK_IDX = 'FK'
    NN_IDX = 'NN'
    UQ_IDX = 'UQ'
    AI_IDX = 'AI'
    DEFAULT_IDX = 'Default'
    COMMENT_IDX = 'Comment'

    # Create SQL definition xy position in Excel
    TBL_NAME_XY = (0, 0)
    TBL_COMMENT_XY = (0, 1)
    TBL_IDX_X = 1

    def __init__(self, db_type, s_name):
        self.db_type = db_type
        self.s_name = s_name

    def _output_file(self, sql_script):
        f_name = self.FILE_NAME.format(s_name=self.s_name)
        f = open(f_name, 'w')
        f.write(sql_script)
