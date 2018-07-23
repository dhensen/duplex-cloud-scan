import apiclient
from httplib2 import Http


def build_request(creds):
    def inner(http, *args, **kwargs):
        new_http = creds.authorize(Http())
        return apiclient.http.HttpRequest(new_http, *args, **kwargs)
    return inner
