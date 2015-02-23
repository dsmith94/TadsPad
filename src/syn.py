
#
#   Synonym check subsystem
#

import urllib2


def check(word):

    # call big huge thes online and get synonyms
    api_key = ''
    url = 'http://words.bighugelabs.com/api/2/' + api_key + '/' + word
    result = urllib2.Request(url)
    print result


__author__ = 'dj'
