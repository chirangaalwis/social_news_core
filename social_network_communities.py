from retrying import retry
from treelib import Node, Tree
from urllib.error import HTTPError
from SPARQLWrapper import SPARQLWrapper, JSON, SPARQLExceptions

from social_network_text_refinement import camel_case_split
from social_network_helper import get_named_entity_tags


def cluster_community_members(members):
    if not members:
        return None

    # concatenate member content prior to entity extraction
    content = []
    for member in members:
        content.append(member.content)
    content = [user_content for user_content in content if user_content is not None]
    content = ' '.join(content)

    # extract named entities
    tags = get_named_entity_tags(content)
    # build community interest tree
    interest_tree = build_interest_topic_tree(tags)

    entities = {}
    for tag in tags:
        entities[tag] = tag.topic

    for member in members:
        content = member.content

        identified_entities = []
        for key, value in entities.items():
            if content is not None:
                if value in content:
                    identified_entities.append(key)

        member.content = set(identified_entities)
        place_member(member, interest_tree)

    print(interest_tree.paths_to_leaves())

    return interest_tree


def get_matching_clusters(interest_tags, interest_tree):
    if (interest_tags, interest_tree) is None:
        return None

    interests = {}
    for tag in interest_tags:
        try:
            sub_types = tag.context['sub_types']
        except (KeyError, TypeError):
            continue

        if sub_types is not None:
            sorted_types = sort_class_order(sub_types)

            if sorted_types is not None:
                if len(sorted_types) > 0:
                    immediate_level = sorted_types[len(sorted_types) - 1]
                    node = interest_tree.get_node(immediate_level)
                    
                    if node is not None:
                        interests[tag.topic] = node.data

    return interests


def build_interest_topic_tree(tags):
    if not tags:
        return None

    clusters = Tree()

    for tag in tags:
        try:
            sub_types = tag.context['sub_types']
        except (KeyError, TypeError):
            continue

        if sub_types is not None:
            sorted_types = sort_class_order(sub_types)
            if sorted_types is not None:
                sorted_types.insert(0, 'Thing')
                create_branch(clusters, sorted_types)

    return clusters


def place_member(member, tree):
    if not (member, tree):
        return

    member_content = member.content

    sub_types = []
    for tag in member_content:
        sub_types.append(tag.context['sub_types'])

    for sub_type in sub_types:
        sub_type = sort_class_order(sub_type)

        if sub_type is None:
            continue

        if len(sub_type) > 0:
            tree.get_node(sub_type[len(sub_type) - 1]).data.append(member)


# support functions
def create_branch(tree_structure, types):
    if not (tree_structure, types):
        return

    previous = None
    for class_type in types:
        node = Node(identifier=class_type, data=[])

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


def sort_class_order(types):
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

    parent = return_key(child_parent, None)
    ordered.append(parent)
    while parent is not None:
        parent = return_key(child_parent, parent)
        if parent is not None:
            ordered.append(parent)

    return ordered


def return_key(dictionary, value):
    matching = {child: parent for child, parent in dictionary.items() if parent == value}
    matching_value = None

    for child, parent in matching.items():
        matching_value = child

    return matching_value
