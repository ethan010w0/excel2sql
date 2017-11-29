from type_exporter.mysql_exporter import MySQLExporter


class SQLExporterFactory:
    def __init__(self, db_type, s_name):
        self.db_type = db_type
        self.s_name = s_name

    # Create the specified type SQL exporter
    def create_exporter(self):
        if self.db_type == 'mysql':
            return MySQLExporter(self.db_type, self.s_name)
        else:
            raise Exception('Unsupported database type')
