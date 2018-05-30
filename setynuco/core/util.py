

def strip_uri(uri):
    if uri[0] == "<":
        return uri[1:len(uri)-1]
    return uri
