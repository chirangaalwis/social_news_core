import os
import json
import re
from datetime import datetime
from time import sleep
import math
from retrying import retry
from collections import OrderedDict
import pyld
import rdflib
import requests
from json import JSONDecodeError
from urllib.error import HTTPError

from pytrends.request import ResponseError, RateLimitError
from alchemyapi import AlchemyAPI
from SPARQLWrapper import SPARQLWrapper, JSON, SPARQLExceptions

from models import SocialNetworkTrend, Tag, ZScore
from google_trends_client import get_pytrends
from social_network_text_refinement import camel_case_split, entity_fraction_from_text

GOOGLE_TRENDS = get_pytrends()


@retry(wait_exponential_multiplier=1000, wait_exponential_max=20000, stop_max_delay=120000)
def get_historical_trends(keywords):
    payload = {'q': keywords, 'date': 'now 12-H'}

    try:
        response = GOOGLE_TRENDS.trend(payload, return_type='json')
    except (ResponseError, JSONDecodeError, RateLimitError):
        raise Exception("Retry!")

    results = OrderedDict()

    for row in response['table']['rows']:
        results.update({row['c'][0]['f']: row['c'][1]['v']})

    return results


def get_zscore(keywords):
    historical_trends = []
    data = {}

    try:
        data = get_historical_trends(keywords)
    except Exception:
        print('arrived')

    if not data:
        return -1

    for date, value in data.items():
        historical_trends.append(value)

    historical_trends = list(reversed(historical_trends))

    historical_trends = [x for x in historical_trends if x is not None]

    current_trend = historical_trends[0]

    historical_trends = historical_trends[1:]

    z_score = ZScore(0.9, historical_trends)
    return z_score.get_score(current_trend)


def get_social_trend(index, queue, results):
    # temp
    factor = int(index / 4)
    print('sleeping ' + str(factor * 60))
    sleep(factor * 60)

    term = queue.get()

    print(term)

    z_score = get_zscore(term)
    results.append(SocialNetworkTrend(topic=term, score=z_score))
    queue.task_done()


def get_named_entities(text):
    # Create the AlchemyAPI Object
    alchemy_api = AlchemyAPI()

    response = alchemy_api.entities('text', text)

    entities = []
    if response['status'] == 'OK':
        for entity in response['entities']:
            entities.append(entity['text'])
    else:
        print('Error in entity extraction call: ', response['statusInfo'])
        return []

    entities = entity_fraction_from_text(entities, text)

    tags = []

    for entity in entities:

        data = get_ontology_data(entity['entity'])

        if not data:
            data = get_ontology_data(entity['entity'])

        for datum in data:

            # TODO: to be fixed DBpedia issue
            # context = {'type': datum[1], 'description': datum[2], 'sub_types': datum[4]}

            context = {'type': datum[1], 'description': datum[2]}

            tag = Tag(datum[0], context, context_fraction=entity['fraction'])
            if tag not in tags:
                tags.append(tag)

    return tags


@retry(wait_exponential_multiplier=1000, wait_exponential_max=20000, stop_max_delay=120000)
def get_ontology_types(subject):
    if subject is None:
        return None

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

    sparql.setReturnFormat(JSON)
    try:
        results = sparql.query().convert()
    except (HTTPError, SPARQLExceptions.EndPointInternalError,
            SPARQLExceptions.EndPointNotFound, SPARQLExceptions.QueryBadFormed):
        raise Exception("Retry!")

    types = []
    if results:
        for result in results["results"]["bindings"]:
            words = camel_case_split((result["labels"]["value"]).replace("http://dbpedia.org/ontology/", ""))
            split = " ".join(words)
            types.append(split.lower().title())

    return types


def get_google_knowledge_graph_result(keyword):
    # Improve mechanism to retrieve the key
    kg_key = open(os.path.join(os.path.expanduser('~'), 'knowledge-graph-key')).read()

    r = requests.get("https://kgsearch.googleapis.com/v1/entities:search",
                     params=dict(query=keyword, key=kg_key, limit=3))

    jsonld = json.loads(r.text)

    normalized = pyld.jsonld.normalize(jsonld, {'algorithm': 'URDNA2015', 'format': 'application/nquads'})

    g = rdflib.Graph()
    g.parse(data=normalized, format='n3')
    g.serialize(format='turtle')

    q = """SELECT ?name ?description ?detail ?score
    WHERE
    {
    ?entity a ns2:EntitySearchResult ; ns2:resultScore ?score ; ns1:result ?result .
    ?result ns1:name ?name .
    OPTIONAL
    {
    ?result ns1:description ?description .
    }
    OPTIONAL
    {
    ?result ns2:detailedDescription ?detailed .
    ?detailed ns1:articleBody ?detail .
    }
    }
    ORDER BY DESC(?score)
    """

    result = None
    try:
        result = g.query(q).serialize(format='csv')
    except Exception:
        pass

    return result


def get_ontology_data(keyword):
    result = get_google_knowledge_graph_result(keyword)

    if not result:
        return []

    # Split the result set data
    entities = []
    for line in re.split('\r', result.decode("utf-8")):
        if not line:
            continue

        line = line.strip()
        results = line.split(',', 1)
        if len(results) < 2:
            continue

        results.extend(results[1].split(',', 1))
        del results[1]

        if len(results) < 3:
            continue

        results.extend(results[2].rsplit(',', 1))
        del results[2]

        # TODO: check DBpedia bug

        # types = get_ontology_types(results[0])
        #
        # print(types)
        #
        # results.append(list(set(types) - {results[1].lower()}))

        entities.append(results)

    # Delete the headers
    del entities[0]

    index = 0
    result = None
    for entity in entities:
        if index > 0:
            diff = result - float(entity[3])

            if diff > 100:
                break

        result = float(entity[3])
        index += 1

    return entities[:index]


def get_status_text(status):
    tags = []
    if status.text:
        tags = get_named_entities(status.text)

    status_record = {'Id': status.id, 'Created_At': status.created, 'Score': status.get_score, 'Tags': tags}

    return status_record


def load_statuses(file_path):
    statuses = {}

    with open(file_path, 'r') as file:
        for line in file:
            status = json.loads(line)

            created_at = datetime.strptime(status['Created_At'], "%Y-%m-%d %H:%M:%S")
            status['Created_At'] = created_at
            status['Score'] = decay_base_score(status['Score'], created_at)

            if status['Created_At'].year in statuses:

                if not status['Created_At'].month in statuses[status['Created_At'].year]:
                    statuses[status['Created_At'].year][status['Created_At'].month] = []

                (statuses[status['Created_At'].year][status['Created_At'].month]).append(status)

            else:

                statuses[status['Created_At'].year] = {}

                statuses[status['Created_At'].year][status['Created_At'].month] = []

                (statuses[status['Created_At'].year][status['Created_At'].month]).append(status)

    return statuses


def store_statuses(statuses, file_path):
    with open(file_path, 'a+') as file:
        for status in statuses:
            if status.text:
                file.write(json.dumps(get_status_text(status), default=jdefault) + "\n")


def jdefault(o):
    return o.__dict__


def get_entity_diversity(statuses):
    total_list = []

    for status in statuses:
        tags = status['Tags']
        tags = [convert_dictionary_to_tag(tag) for tag in tags]
        total_list.extend(tags)

    total_size = len(total_list)

    without_duplicates = len(set(total_list))

    return without_duplicates / total_size


def decay_base_score(base_score, created_at):
    time_difference = (datetime.now() - created_at)
    time_difference_in_days = (time_difference.days * 86400 + time_difference.seconds) / 86400

    # start decaying the score after two days
    drop_off = 2
    if time_difference_in_days > drop_off:
        decayed_score = base_score * math.exp(
            -5 * (time_difference_in_days - drop_off) * (time_difference_in_days - drop_off))
    else:
        decayed_score = base_score

    return decayed_score


def convert_dictionary_to_tag(dictionary):
    if not dictionary:
        return None

    if ('topic' in dictionary) & ('context' in dictionary):
        return Tag(topic=dictionary['topic'], context=dictionary['context'])
    else:
        return None


if __name__ == "__main__":

    print(get_ontology_types('Manchester United F.C.'))
    print(get_ontology_types('Mona Lisa'))
    print(get_ontology_types('Mahinda Rajapaksa'))
    print(get_ontology_types('José Mourinho'))
    print(get_ontology_types('The Count of Monte Cristo'))

    # print(get_historical_trends('Manchester United'))
    # print(get_zscore('Manchester United'))
    # print(get_zscore('Liverpool'))
    # print(get_zscore(['Real Madrid C.F.', '‪CA Osasuna']))

    # statuses = load_statuses(os.path.realpath('.') + '/statuses.jsonl')
    # print(get_entity_diversity(statuses[2017][2]))

    # print(get_ontology_data('castillo io'))

    # print(get_ontology_data('fergie'))

    # string = 'It is only two months since Henrikh Mkhitaryan was the man in the same position Anthony Martial ' \
    #          'currently finds himself in. Held accountable for a poor workrate in the derby defeat to Manchester City ' \
    #          'in September, Mkhitaryan had to take the long road back into Jose Mourinho’s plans. Mkhitaryan is ' \
    #          'a great player. Martial must learn from Mkhitaryan. Hail Henrikh Mkhitaryan. Come one Henrikh!!! ' \
    #          'European Organization for Nuclear Research is a great place to be. Anthony Martial has been to the ' \
    #          'Nuclear ' \
    #          'Research center. '
    #
    # for tag in get_named_entities(string):
    #     print('topic: ' + tag.topic)
    #     print('context: ' + str(tag.context))
    #     print('fraction: ' + str(tag.context_fraction))
    #     print()

    # print(get_ontology_data('paulpogba'))
