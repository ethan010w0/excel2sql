import os
import xlrd

from sql_exporter.type_exporter import GeneralExporter


class MySQLExporter(GeneralExporter):
    # Pre and post syntax
    PRE_S = '/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;'
    POST_S = '/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;'

    # Default function syntax
    DEFAULT_FUN_S = 'Fun: '

    # Column definition syntax
    NAME_S = '`{name_def}`'
    NN_S = 'NOT NULL'
    UQ_S = 'UNIQUE'
    AI_S = 'AUTO_INCREMENT'
    DEFAULT_S = 'DEFAULT {default_val}'
    COMMENT_S = 'COMMENT \'{comment_str}\''

    # Primary key definition syntax
    PK_COL_S = '`{pk_col_name}`'
    PK_S = 'PRIMARY KEY ({pk_col_defs})'

    # Foreign key definition syntax
    REF_DEF_S = 'REFERENCES `{s_name}`.`{ref_tbl_name}` (`{ref_col_name}`)'
    FK_S = 'FOREIGN KEY (`{fk_col_name}`) {ref_def}'

    # Table option syntax
    TBL_COMMENT_S = 'COMMENT \'{tbl_comment_str}\''

    # Create definition syntax
    C_S = 'CREATE TABLE `{s_name}`.`{tbl_name}` ({linesep}  {c_defs}{linesep})'

    # Schema name
    _s_name = str()

    # Parse the default value is a value or a function
    def _parse_default_val(self, default_val):
        if str(default_val).startswith(self.DEFAULT_FUN_S):
            default_val = default_val[len(self.DEFAULT_FUN_S):]
        else:
            default_val = '\'{default_val}\''.format(default_val=default_val)
        return default_val

    def _make_col_def(self, col_def_val_idx):
        type_def = col_def_val_idx[self.TYPE_IDX]
        # Return if no data type
        if not type_def:
            return

        # Get column definition values.
        nn_bool = col_def_val_idx[self.NN_IDX]
        uq_bool = col_def_val_idx[self.UQ_IDX]
        ai_bool = col_def_val_idx[self.AI_IDX]
        default_val = col_def_val_idx[self.DEFAULT_IDX]
        comment_str = col_def_val_idx[self.COMMENT_IDX]

        # Make the column definition SQL
        col_def = [type_def, ' ']
        if nn_bool:
            col_def.extend([self.NN_S, ' '])
        if uq_bool:
            col_def.extend([self.UQ_S, ' '])
        if ai_bool:
            col_def.extend([self.AI_S, ' '])
        if default_val:
            default_val = self._parse_default_val(default_val)
            default_def = self.DEFAULT_S.format(default_val=default_val)
            col_def.extend([default_def, ' '])
        if comment_str:
            comment_def = self.COMMENT_S.format(comment_str=comment_str)
            col_def.extend([comment_def, ' '])

        del col_def[-1]
        return col_def

    def _make_c_def(self, col_def_val_idx):
        name_def = col_def_val_idx[self.NAME_IDX]
        # Return if no column name
        if not name_def:
            return

        # Make the create definition SQL
        col_name = self.NAME_S.format(name_def=name_def)
        col_def = self._make_col_def(col_def_val_idx)
        if not col_def:
            return
        c_def = [col_name, ' ']
        c_def.extend(col_def)

        return c_def

    # Make the primary key column definition
    def _make_pk_col_def(self, col_def_val_idx):
        pk_bool = col_def_val_idx[self.PK_IDX]
        if pk_bool:
            pk_col_name = col_def_val_idx[self.NAME_IDX]
            pk_col_def = self.PK_COL_S.format(pk_col_name=pk_col_name)
            return pk_col_def

    # Make the foreign key definition SQL
    def _make_fk_def(self, col_def_val_idx):
        fk_ref = col_def_val_idx[self.FK_IDX]
        if fk_ref:
            fk_col_name = col_def_val_idx[self.NAME_IDX]
            (ref_tbl_name, ref_col_name) = fk_ref.split('.')
            ref_def = self.REF_DEF_S.format(s_name=self.s_name,
                                            ref_tbl_name=ref_tbl_name,
                                            ref_col_name=ref_col_name)
            fk_def = self.FK_S.format(fk_col_name=fk_col_name, ref_def=ref_def)
            return fk_def

    def _make_c_defs(self, sh, col_def_idx):
        c_defs = list()
        pk_col_defs = list()
        fk_defs = list()
        for rx in range(2, sh.nrows):
            row = sh.row(rx)

            # Get column definition value indexes according to column defininton indexes
            col_def_val_idx = dict(
                zip(col_def_idx, map(lambda x: row[x].value, col_def_idx.values())))

            # Make create definition SQLs
            c_def = self._make_c_def(col_def_val_idx)
            if not c_def:
                continue
            c_defs.extend(c_def)
            c_defs.append(str().join([',', os.linesep, '  ']))

            # Make primary key cloumn definition SQLs
            pk_col_def = self._make_pk_col_def(col_def_val_idx)
            if pk_col_def:
                pk_col_defs.extend([pk_col_def, ', '])

            # Make foreign key definition SQLs
            fk_def = self._make_fk_def(col_def_val_idx)
            if fk_def:
                fk_defs.extend([fk_def, ' '])

        # Make creat definitions SQLs
        if pk_col_defs:
            del pk_col_defs[-1]
            pk_def = self.PK_S.format(pk_col_defs=str().join(pk_col_defs))
            c_defs.extend([pk_def, ', '])
        if fk_defs:
            c_defs.extend(fk_defs)
        if c_defs:
            del c_defs[-1]

        return c_defs

    # Make table comment option SQL
    def _make_tbl_comment_opt(self, sh):
        tbl_comment_str = sh.cell_value(*self.TBL_COMMENT_XY)
        if tbl_comment_str:
            tbl_comment_opt = self.TBL_COMMENT_S.format(
                tbl_comment_str=tbl_comment_str)
            return tbl_comment_opt

    def export(self, excel):
        c_sqls = list()
        c_sqls.extend([self.PRE_S, os.linesep])

        book = xlrd.open_workbook(excel)
        for sh in book.sheets():
            # Get the column definiton indexes
            col_def_idx = self._get_col_def_idx(sh)

            c_defs = self._make_c_defs(sh, col_def_idx)
            # Return if no create definition SQLs
            if not c_defs:
                continue

            tbl_name = sh.cell_value(*self.TBL_NAME_XY)
            if tbl_name:
                # Make create SQLs
                c_sql = self.C_S.format(
                    s_name=self.s_name, tbl_name=tbl_name, linesep=os.linesep, c_defs=str().join(c_defs))
                c_sqls.extend([c_sql, os.linesep])

                tbl_comment_opt = self._make_tbl_comment_opt(sh)
                if tbl_comment_opt:
                    c_sqls.extend([tbl_comment_opt, os.linesep])

                del c_sqls[-1]
                c_sqls.extend([';', os.linesep * 2])

        c_sqls.extend(self.POST_S)

        self._output_file(str().join(c_sqls))
