from flask import request, url_for

def route_for(name, **kwargs):
    return request.host_url.rstrip('/') + url_for(name, **kwargs)
