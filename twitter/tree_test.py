import os
import sys
from retrying import retry
from treelib import Node, Tree
from urllib.error import HTTPError
from SPARQLWrapper import SPARQLWrapper, JSON, SPARQLExceptions

sys.path.insert(0, os.path.realpath('..'))
from models import Tag
from social_network_text_refinement import camel_case_split


# temp
def get_tags():
    tag1 = Tag(topic='BO', context={'sub_types': ['Agent', 'Person', 'Office Holder']})
    tag2 = Tag(topic='SO', context={'sub_types': ['Agent', 'Person', 'Noble']})
    tag3 = Tag(topic='SOS', context={'sub_types': ['Agent', 'Person', 'Organisation Member', 'Sports Team Member']})

    return [tag1, tag2, tag3]


def create_branch(tree_structure, types):
    if not (tree_structure, types):
        return

    previous = None
    for class_type in types:
        node = Node(identifier=class_type)

        if previous is None:
            if tree_structure.get_node(node.identifier) is None:
                tree_structure.add_node(node)
        else:
            if tree_structure.get_node(node.identifier) is None:
                tree_structure.add_node(node, previous.identifier)

        previous = node


@retry(wait_exponential_multiplier=1000, wait_exponential_max=20000, stop_max_delay=120000)
def get_ontology_super_class(subclass):
    if not subclass:
        return None

    sparql = SPARQLWrapper("http://dbpedia.org/sparql")

    sparql.setQuery("""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?superclass
        WHERE {
        dbo:%s rdfs:subClassOf ?superclass
        FILTER (strstarts(str(?superclass), "http://dbpedia.org/ontology/"))
        }
    """ % subclass.replace(" ", ""))

    sparql.setReturnFormat(JSON)
    try:
        results = sparql.query().convert()
    except (SPARQLExceptions.EndPointInternalError,
            SPARQLExceptions.EndPointNotFound, SPARQLExceptions.QueryBadFormed, HTTPError):
        raise Exception("Retry!")

    try:
        if 'results' in locals():
            values = camel_case_split((results["results"]["bindings"][0]["superclass"]["value"])
                                      .replace("http://dbpedia.org/ontology/", ""))
            return ' '.join(values)
        else:
            return None
    except (IndexError, TypeError):
        return None


def _sort_class_order(types):
    if not types:
        return None

    ordered = []

    child_parent = {}
    for class_type in types:
        super_class = get_ontology_super_class(class_type)
        child_parent[class_type] = super_class

    parent = _return_key(child_parent, None)
    ordered.append(parent)
    while parent is not None:
        parent = _return_key(child_parent, parent)
        if parent is not None:
            ordered.append(parent)

    return ordered


def _return_key(dictionary, value):
    matching = {child: parent for child, parent in dictionary.items() if parent == value}
    matching_value = None

    for child, parent in matching.items():
        matching_value = child

    return matching_value


if __name__ == "__main__":
    clusters = Tree()

    # for tag in get_tags():
    #     sub_types = tag.context['sub_types']
    #     # create_branch(clusters, sub_types)
    #
    #     for sub_type in sub_types:
    #         superclass = get_ontology_super_class(sub_type)
    #         if superclass is not None:
    #             print(superclass + ' | ' + sub_type)

    # clusters.show()

    classes = ['Sports Team Member', 'Person', 'Agent', 'Organisation Member']
    classes = ['Artwork', 'Work']
    print(_sort_class_order(classes))
