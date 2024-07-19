from elasticsearch import Elasticsearch

class EsUtil:
    def __init__(self, username, password, url):
        self.username = username
        self.password = password
        self.url = url
        self.client = self.get_client_factory()

    def get_client_factory(self):
        # Ensure you specify the scheme (https), host, and port in the Elasticsearch URL
        # Example URL: https://your_elasticsearch_host:9200
        return Elasticsearch(
            [self.url],  # Make sure the URL includes the scheme, host, and port
            http_auth=(self.username, self.password),
        )

# Example usage
if __name__ == "__main__":
    # Provide your Elasticsearch credentials and URL
    username = "elastic"
    password = "TNLo1KLqA8PIk23CFVDoW7UJ"
    url = "https://3df13a502759404ea768a4fc5b1c723d.ap-south-1.aws.elastic-cloud.com:9243"  # Include the port in the URL

    es_util = EsUtil(username, password, url)
    
    # Now you can use `es_util.client` to interact with Elasticsearch
    # For example, to check the cluster health:
    cluster_health = es_util.client.cluster.health()
    print(cluster_health)
