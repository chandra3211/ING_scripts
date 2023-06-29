"""Helper object to help build Artifactory Mapping JSON"""
import os
import json
from requests import exceptions
from ._tfsapi import _tfsapi


class _artifactory_map(object):

    def __init__(self, repokey = None, itempath = None, application = None, version = None):
        self.repokey = repokey
        self.itempath = itempath
        self.application = application
        self.version = version
        self.jsonfile = None

    def save(self):
        if not (self.jsonfile is None):
            self.json_dumpf(self.jsonfile)
        else:
            raise ValueError('Error: cannot save - jsonfile attribute is None')

    def json_dumpf(self, jsonfile):
        if os.path.exists(jsonfile):
            os.remove(jsonfile)
        data = self.json_dumps()
        with open(jsonfile, 'w') as f:
            f.write(data)
        self.jsonfile = jsonfile

    def _json(self):
        j = {}
        j['repokey'] = self.repokey
        j['itempath'] = self.itempath
        j['application'] = self.application
        j['version'] = self.version
        return j

    def json_dumps(self):
        j = self._json()
        return json.dumps(j)

    def to_taskvars(self):
        j = self._json()
        v = {}
        for item in j:
            key = "PLMAP_" + item.upper()            
            v[key] = j[item]
        return v

    @staticmethod
    def json_loads(jsonstr):
        m = _artifactory_map()
        j = json.loads(jsonstr)
        m.repokey = j['repokey']
        m.itempath = j['itempath']
        m.application = j['application']
        m.version = j['version']
        return m

    @staticmethod
    def json_loadf(jsonfile):
        """load from file, if not exists return new blank instance"""
        if not os.path.exists(jsonfile):
            m = _artifactory_map()
            m.jsonfile = jsonfile
            return m

        with open(jsonfile, 'r') as f:
            data = f.read()
        m = _artifactory_map.json_loads(data)
        m.jsonfile = jsonfile
        return m


class ApplicationNotFoundError(Exception):
    def __init__(self, app_name, original_exception):
        message = json.loads(original_exception.response.content)['message']
        super().__init__("Application '{}' or mapping file is not found!\n{}".format(app_name, message))


class VersionNotFoundError(Exception):
    def __init__(self, version, original_exception):
        message = json.loads(original_exception.response.content)['message']
        super().__init__("Version '{}' is not found!\n{}".format(version, message))


def from_app_version(app_name, ver, tfsuser=None, tfspwd=None):
    try:
        mapping_json = _tfsapi.git_get_file(
                "artifactory-map-{}.git".format(app_name),
                "/mapping.json",
                ver,
                "GitRC",
                tfsuser,
                tfspwd)
    except exceptions.HTTPError as e:
        if e.response.status_code == 404:
            raise ApplicationNotFoundError(app_name, e)
        elif e.response.status_code == 400:
            raise VersionNotFoundError(ver, e)
        else:
            raise e
    except:
        raise
    mapping = _artifactory_map.json_loads(mapping_json)
    return mapping
