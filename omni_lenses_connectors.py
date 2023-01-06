from api_utils.lenses_api import LensesAPI
from api_utils.snowflake_api import Snowflake
import os
from datetime import datetime

if __name__ == "__main__":

    # get the names of all the connectors
    env = os.getenv("ENVIRONMENT")
    host = f"https://lenses.cko-{env}.ckotech.co"
    lenses = LensesAPI(host)
    connectors = [x.lower() for x in lenses.get_connectors(cluster_alias="connectClusters")]

    # get the correlation id, arn and creation date of all the ingestions with 'creating' or 'validationpassed'
    query = """
        with table1 as (
            SELECT * FROM DATA_PLATFORM.OMNI.INGESTION_STATUS
            QUALIFY ROW_NUMBER() OVER (PARTITION BY CORRELATION_ID ORDER BY CREATED_TIME DESC)=1
        )

        select correlation_id, arn, created_time from table1 where lower(status) in ('creating', 'validationpassed');
    """

    sf = Snowflake(
        user=os.getenv("SNOWFLAKE_USER"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        role=os.getenv("SNOWFLAKE_ROLE"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE")
    )
    conn = sf.get_connection()

    results = sf.execute_query(query=query, conn=conn)
    # loop through all of the above
        # format the arn to get the name of the snowflake sink
        # check if sink is in the list of connectors
        # if it is, update this row to say 'Created'
        # if not, update this row to say 'Failure'

    for result in results:
        print(result)
        correlation_id, arn, creation_date = result
        sink_name = ""
        if 'sns' in arn:
            sink_name = f'{arn.split(":")[-1]}-snowflake-sink'
        elif 'kinesis' in arn:
            sink_name = f'{arn.split("stream/")[-1]}-snowflake-sink'
        elif 'log-group' in arn:
            sink_name = f"{arn.split('log-group:/')[-1].replace(':*', '').replace('/', '-')}-snowflake-sink"

        status = 'Created' if sink_name.lower() in connectors else "Failure"

        # was not created successfully
        update_query = f"""
            update data_platform.omni.ingestion_status
            set status='{status}'
            where correlation_id='{correlation_id}' 
            and created_time='{str(creation_date)}';
        """

        result = sf.execute_query(update_query, conn=conn)
        print(result.fetchone())
    conn.close()


