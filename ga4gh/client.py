"""
Client classes for the GA4GH reference implementation.
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
 
import json
import future
from future.standard_library import hooks
with hooks():
    import http.client

import ga4gh
import ga4gh.protocol as protocol

class HTTPClient(object):
    """
    Simple HTTP client for the GA4GH protocol.
    """
    def __init__(self, host, port, debugLevel):
        self.httpConnection = http.client.HTTPConnection(host, port)
        self.httpConnection.set_debuglevel(debugLevel)
        self.debugLevel = debugLevel

    def searchVariants(self, request):
        """
        Sends the specified GASearchVariantsRequest to the server and returns
        an iterator over the returned set of GAVariant objects. Result paging
        is handled transparently, so that several HTTP requests may be made
        while this method executes.
        """
        notDone = True
        while notDone:
            s = request.toJSON()
            self.httpConnection.request("POST", "variants/search", s)
            r = self.httpConnection.getresponse()
            if self.debugLevel > 0:
                print() # ugly - http doesn't end lines for some reason
            s = r.read().decode() # TODO encoding??
            if self.debugLevel > 1:
                # TODO use a logging output and integrate with HTTP client more
                # nicely.
                print("json response:")
                pp = json.dumps(json.loads(s), sort_keys=True, indent=4)
                print(pp)
            resp = ga4gh.protocol.GASearchVariantsResponse.fromJSON(s)
            # TODO check if this resp is a GAException and raise an error
            for v in resp.variants:
                yield v
            request.pageToken = resp.nextPageToken
            notDone = resp.nextPageToken is not None

