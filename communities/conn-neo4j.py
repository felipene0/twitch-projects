from neo4j import GraphDatabase
from config import URI, AUTH

def connection(URI, AUTH, DATABASE='neo4j'):
    driver = GraphDatabase.driver(URI, auth=AUTH)
    session = driver.session(database=DATABASE)

    return session

def createNode(channels, session):
    #Execute the node creation
    for channel in channels:
        if 'broadcaster_id' in channel:
            session.execute_query(
                """
                    merge (c:Channel {name: '', followed_at: ''})
                """
            )
    
    return None

try:
    driver = GraphDatabase.driver(URI, auth=AUTH)
    DATABASE = 'neo4j'
    
    with driver.session(database=DATABASE) as session:
        # Get the name of all 42 year-olds
        driver.execute_query(
            """
            merge (p:Person {name: 'teste'})
            merge (p2:Person {name: 'teste2'})
            merge (p3:Person {name: 'teste3'})

            merge (p)-[:test]->(p2)
            merge (p2)-[:test]->(p3)   
            """
        )

        records, summary, keys = driver.execute_query(
            "MATCH (n) RETURN n",
            database_=DATABASE,
        )

        # Loop through results and do something with them
        for person in records:
            print(person.data())

        # Summary information
        print("The query `{query}` returned {records_count} records in {time} ms.".format(
            query=summary.query, records_count=len(records),
            time=summary.result_available_after,
        ))

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if 'driver' in locals():
        session.close()