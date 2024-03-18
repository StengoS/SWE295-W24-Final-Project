import json

# Pyvis documentation: https://pyvis.readthedocs.io/en/latest/documentation.html
from pyvis.network import Network


def create_network(repo_data):
    net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white", directed=True, 
                  select_menu=True)

    for artifact in repo_data.keys():
        if repo_data[artifact]["has_associated_CVE"]:
            net.add_node(artifact, label=artifact, color="#a20707")
        else:
            net.add_node(artifact, label=artifact)
    for artifact in repo_data.keys():
        for dependency in repo_data[artifact]["used_by"]:
            net.add_edge(artifact, dependency)

    net.show_buttons()
    net.show("mvn_repository_usage_graph.html", notebook=False)


def main():
    data = {}
    with open("../data-scraping/mvn_repo_data.json") as repo_data:
        data = json.load(repo_data)

    create_network(data)
    

if __name__ == "__main__":
    main()