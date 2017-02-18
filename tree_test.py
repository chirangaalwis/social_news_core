from retrying import retry
from treelib import Node, Tree
from urllib.error import HTTPError
from SPARQLWrapper import SPARQLWrapper, JSON, SPARQLExceptions

from models import Tag
from social_network_text_refinement import camel_case_split

# temp
from social_network_helper import get_ontology_types


# temp
def get_tags():
    tags = []

    terms = ['Manchester United F.C.', 'Mona Lisa', 'Mahinda Rajapaksa', 'José Mourinho', 'The Count of Monte Cristo']

    for term in terms:
        tags.append(Tag(topic=term, context={'sub_types': get_ontology_types(term)}))

    return tags


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
    except (HTTPError, SPARQLExceptions.EndPointInternalError,
            SPARQLExceptions.EndPointNotFound, SPARQLExceptions.QueryBadFormed):
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
        try:
            super_class = get_ontology_super_class(class_type)
            child_parent[class_type] = super_class
        except Exception:
            return ordered

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


def build_interest_topic_tree(tags):
    if not tags:
        return None

    clusters = Tree()

    for tag in get_tags():

        try:
            sub_types = tag.context['sub_types']
        except (KeyError, TypeError):
            continue

        if sub_types is not None:
            sorted_types = _sort_class_order(sub_types)
            sorted_types.insert(0, 'Thing')
            create_branch(clusters, sorted_types)

    return clusters


if __name__ == "__main__":
    interests = build_interest_topic_tree(get_tags())

    interests.show()

