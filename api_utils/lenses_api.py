import requests
import os
import json

class LensesAPI:

    def __init__(self, host):
        """Authenticates with the lenses api

        Args:
            host (str): name of lenses host, without a trailing slash e.g. if you access lenses at http://localhost:3000,
            this would be http://localhost:3000
        """
        self.host = host
        self.username = os.getenv("LENSES_USERNAME")
        self.password = os.getenv("LENSES_PASSWORD")
        data = {
            'user': self.username,
            'password': self.password
        }
        headers = {'Content-Type': 'application/json'}
        url=f"{self.host}/api/login"

        if self.username and self.password:
            response = requests.post(
                url=url,
                data=json.dumps(data),
                headers=headers
            )

            self.token = response.text
        else:
            print("Please set the following environment variables:\n- LENSES_USERNAME\n- LENSES_PASSWORD")
    

    def get_connectors(self, cluster_alias):
        """Lists all the connectors for the given cluster alias

        Args:
            cluster_alias (str): case sensitive alias of the cluster

        Returns:
            list: list of strings containing the names of all the connectors
        """
        headers = {"X-Kafka-Lenses-Token": f"{self.token}", "Content-Type": "application/json"}
        
        response = requests.get(
            url=f"{self.host}/api/proxy-connect/{cluster_alias}/connectors",
            headers=headers
        )
        return response.text


if __name__ == "__main__":
    env = os.getenv("ENVIRONMENT")
    host = f"https://lenses.cko-{env}.ckotech.co"
    lenses = LensesAPI(host)
    connectors = lenses.get_connectors(cluster_alias=os.getenv("CLUSTER_ALIAS"))
    print(connectors)