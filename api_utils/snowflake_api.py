import snowflake.connector as connector
import os

class Snowflake:

    def __init__(self, user, account, role, warehouse, password=None):
        self.user = user
        self.account = account
        self.role = role
        self.warehouse = warehouse
        self.password = password

    def get_connection(self):
        if not self.password:
            return connector.connect(
                user=self.user,
                account=self.account,
                role=self.role,
                warehouse=self.warehouse,
                authenticator="externalbrowser"
            )
        else:
            print("auth using pwrd")
            return connector.connect(
                user=self.user,
                account=self.account,
                role=self.role,
                warehouse=self.warehouse,
                password=self.password
            )
    
    def execute_query(self, query, conn):
        results = conn.cursor().execute(query)
        return results

    def fetch_as_pd_df(self, query, cursor):
        cursor.execute(query)
        return cursor.fetch_pandas_all()


if __name__ == "__main__":
    query = """
        with table1 as (
            SELECT * FROM DATA_PLATFORM.OMNI.INGESTION_STATUS
            WHERE 
            (
            true 
            OR LOWER(CORRELATION_ID) LIKE LOWER('%%')
            )
            QUALIFY ROW_NUMBER() OVER (PARTITION BY CORRELATION_ID ORDER BY CREATED_TIME DESC) = 1
            order by created_time desc
        )

        select * from table1 where lower(status) in ('creating', 'validationpassed');
    """

    sf = Snowflake(
        user=os.getenv("SNOWFLAKE_USER"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        role=os.getenv("SNOWFLAKE_ROLE"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE")
    )

    conn = sf.get_connection()

    results = sf.execute_query(query=query, conn=conn)
    i = 0
    for result in results:
        i += 1
        print(result)
        if i == 10:
            break