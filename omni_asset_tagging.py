from api_utils.snowflake_api import Snowflake
import os

if __name__ == "__main__":
    # create snowflake connection
    sf = Snowflake(
        user=os.getenv("SNOWFLAKE_USER"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        role=os.getenv("SNOWFLAKE_ROLE"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        password=os.getenv("SNOWFLAKE_PASSWORD")
    )

    conn = sf.get_connection()
    # get tables created by omni by querying data_platform.omni.ingestion_resources
    get_tables_query = """
        select distinct arn
        from data_platform.omni.ingestion_resources 
        where arn like 'LANDING%' 
        and status = 'Active';
    """
    resources_results = sf.execute_query(query=get_tables_query, conn=conn)
    # get all of the complete ingestions 
    status_results = sf.execute_query(
        query="""
            select distinct arn, table_name from data_platform.omni.ingestion_status 
            where lower(status)='complete';
        """
        , conn=conn
    )
    # turn complete ingestions into dict with key as table name and value as arn
    complete_ingestions_mapping = {
        r[1] : r[0] for r in status_results
    }

    for result in resources_results:
        table_name = result[0]
        # if table name doesn't exist in complete ingestions, return None
        # these are ingestions that are no longer in use/failed in some way
        resource_arn = complete_ingestions_mapping.get(table_name, None)
        if resource_arn:
            tag_association = resource_arn.split(":")[2]
            if tag_association == 'logs':
                tag_association = 'kinesis'
            elif tag_association == 'sns':
                tag_association = 'sqs'
        try:
            # tag them with the ingestion_source tag using the following query
            sf.execute_query(
                    query=f"""
                            alter table {table_name}
                            set tag DATA_PLATFORM.GOVERNANCE.INGESTION_SOURCE = '{tag_association}';
                        """,
                    conn=conn
                )
            
            # create stream using the following query
            sf.execute_query(
                query=f"""
                        create stream if not exists 
                        {table_name.upper()}_LATENCY_STREAM
                        on table {table_name}
                        append_only = FALSE
                        show_initial_rows = FALSE;
                    """,
                    conn=conn
                )
        
            # grant privileges on the new stream for following roles
            for role in ["DATA_PLATFORM_TRANSFORM", "TRANSFORM", "LOAD"]:
                sf.execute_query(
                    query=f"""
                            grant SELECT on STREAM {table_name.upper()}_LATENCY_STREAM to role {role};
                        """,
                        conn=conn
                    )
            print(f"Completed table {table_name} for source {tag_association}")
        except Exception as err:
            print("ERROR: ", err)
    # close sf connection
    conn.close()