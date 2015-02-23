
#
#   Synonym check subsystem
#

import urllib2


def check(word):

    # call big huge thes online and get synonyms
    api_key = '42b544dd99a98e6ccd9554a2363c7a49'
    url = 'http://words.bighugelabs.com/api/2/' + api_key + '/' + word + '/'
    result = urllib2.urlopen(url)

    # we have result, stock nouns and verbs
    words = result.read().split('\n')
    nouns = []
    verbs = []
    search_for = (('noun|syn|', nouns), ('verb|syn|', verbs))
    for (search_string, current_list) in search_for:
        for w in words:
            if search_string in w:
                current_list.append(w[len(search_string):])
    return nouns, verbs


__author__ = 'dj'
