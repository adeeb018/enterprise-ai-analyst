from src.ingestion.schema_models import TableInfo
from src.config.database import engine
import pandas as pd


class ValueExtractor:

    def __init__(self):
        self.engine = engine

    def extract(
        self,
        table: TableInfo,
    ) -> pd.DataFrame:

        query = f'''
        SELECT *
        FROM "{table.schema_name}"."{table.table}"
        '''

        return pd.read_sql(
            query,
            self.engine,
        )