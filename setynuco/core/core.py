from easysparql import *


def get_numerical_properties_for_url(endpoint, class_uri):
    """
    :param endpoint:
    :param class_uri:
    :return:
    """
    class_uri_stripped = strip_uri(class_uri)
    query = """
        select ?p count(distinct ?s) as ?num where {
        ?s a <%s>.
        ?s ?p ?o
        FILTER(isNumeric(?o))
        }
        group by ?p
        order by desc(?num)
    """ % class_uri_stripped
    results = run_query(query=query, endpoint=endpoint, raiseexception=False)
    properties = [r['p']['value'] for r in results]
    return properties


def strip_uri(uri):
    if uri[0] == "<":
        return uri[1:len(uri)-1]
    return uri


