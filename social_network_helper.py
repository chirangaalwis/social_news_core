import json
from datetime import datetime

from alchemyapi import AlchemyAPI
from SPARQLWrapper import SPARQLWrapper, JSON

from models import Tag


def get_named_entities(text):
    tags = []

    # Create the AlchemyAPI Object
    alchemy_api = AlchemyAPI()

    response = alchemy_api.entities('text', text)

    if response['status'] == 'OK':
        for entity in response['entities']:
            tags.append(Tag(entity['text'], [entity['type']]))
    else:
        print('Error in entity extraction call: ', response['statusInfo'])

    return tags


def get_ontology_types(subject):
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")

    sparql.setQuery("""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT ?labels
        WHERE {
            ?person rdfs:label "%s"@en ; rdf:type ?labels
            FILTER (strstarts(str(?labels), "http://dbpedia.org/ontology/"))
        }
    """ % subject)
    print(sparql.queryString)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    for result in results["results"]["bindings"]:
        print(result["labels"]["value"])


def get_status_text(status):
    tags = []
    if status.text:
        tags = get_named_entities(status.text)

    status_record = {'Id': status.id, 'Created_At': status.created, 'Score': status.score, 'Tags': tags}

    return status_record


def load_statuses(file_path):
    statuses = {}

    with open(file_path, 'r') as file:
        for line in file:
            status = json.loads(line)

            created_at = datetime.strptime(status['Created_At'], "%Y-%m-%d %H:%M:%S")
            status['Created_At'] = created_at

            if status['Created_At'].year in statuses:

                if not status['Created_At'].month in statuses[status['Created_At'].year]:
                    statuses[status['Created_At'].year][status['Created_At'].month] = []

                (statuses[status['Created_At'].year][status['Created_At'].month]).append(status)

            else:

                statuses[status['Created_At'].year] = {}

                statuses[status['Created_At'].year][status['Created_At'].month] = []

                (statuses[status['Created_At'].year][status['Created_At'].month]).append(status)

    return statuses


def get_status_text_created_at(string):
    if not string:
        return None

    datetime_instance = datetime.strptime(string, "%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    get_ontology_types('Manchester United F.C.')
