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

    _c_def_idx = (NAME_IDX, TYPE_IDX, PK_IDX, FK_IDX, NN_IDX,
                  UQ_IDX, AI_IDX, DEFAULT_IDX, COMMENT_IDX)

    def __init__(self, db_type, s_name):
        self.db_type = db_type
        self.s_name = s_name

    # Get column definition indexes in excel sheet
    def _get_col_def_idx(self, sh):
        col_def_idx = dict()
        for ry in range(sh.ncols):
            c_def_tag = sh.cell_value(self.TBL_IDX_X, ry)
            col_def_idx[c_def_tag] = ry

        # Check for missing create definition
        for x in self._c_def_idx:
            if x not in col_def_idx:
                raise Exception, 'No create definition: {key}'.format(key=x)
        return col_def_idx

    def _output_file(self, sql_script):
        f_name = self.FILE_NAME.format(s_name=self.s_name)
        f = open(f_name, 'w')
        f.write(sql_script)
