
import ConfigParser

# custom parser, so we can load prefs.conf file into a dictionary


class PrefsParser(ConfigParser.SafeConfigParser):

    def as_dict(self):
        d = dict(self._sections)
        for k in d:
            d[k] = dict(self._defaults, **d[k])
            d[k].pop('__name__', None)
        return d

__author__ = 'stack overflow'
