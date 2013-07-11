# This file is part of the musicbrainzngs library
# Copyright (C) Alastair Porter, Adrian Sampson, and others
# This file is distributed under a BSD-2-Clause type license.
# See the COPYING file for more information.
# Global authentication and endpoint details.
import logging
from .musicbrainz import _version
from .musicbrainz import _mb_request, _do_mb_query, _do_mb_search, _rate_limit
from .musicbrainz import _check_filter_and_make_params, _check_includes_impl
from .musicbrainz import VALID_BROWSE_INCLUDES

class MusicBrainzWS(object):
    user = password = ""
    _hostname = "musicbrainz.org"
    _client = ""
    _useragent = ""

    _log = logging.getLogger("musicbrainzngs")

    # Rate limiting.

    limit_interval = 1.0
    limit_requests = 1
    do_rate_limit = True

    def auth(self, u, p):
        """Set the username and password to be used in subsequent queries to
        the MusicBrainz XML API that require authentication.
        """
        self.user = u
        self.password = p

    def set_useragent(self, app, version, contact=None):
        """Set the User-Agent to be used for requests to the MusicBrainz webservice.
        This must be set before requests are made."""

        if not app or not version:
            raise ValueError("App and version can not be empty")
        if contact is not None:
            self._useragent = "%s/%s python-musicbrainz-ngs/%s ( %s )" % (app, version, _version, contact)
        else:
            self._useragent = "%s/%s python-musicbrainz-ngs/%s" % (app, version, _version)
        self._client = "%s-%s" % (app, version)
        self._log.debug("set user-agent to %s" % self._useragent)

    def set_hostname(self, new_hostname):
        """Set the base hostname for MusicBrainz webservice requests.
        Defaults to 'musicbrainz.org'."""
        self._hostname = new_hostname

    def set_rate_limit(self, limit_or_interval=1.0, new_requests=1):
        """Sets the rate limiting behavior of the module. Must be invoked
        before the first Web service call.
        If the `limit_or_interval` parameter is set to False then
        rate limiting will be disabled. If it is a number then only
        a set number of requests (`new_requests`) will be made per
        given interval (`limit_or_interval`).
        """

        if isinstance(limit_or_interval, bool):
            do_rate_limit = limit_or_interval
        else:
            if limit_or_interval <= 0.0:
                raise ValueError("limit_or_interval can't be less than 0")
            if new_requests <= 0:
                raise ValueError("new_requests can't be less than 0")
            self.do_rate_limit = True
            self.limit_interval = limit_or_interval
            self.limit_requests = new_requests

    @_rate_limit
    def _mb_request(self, path, method='GET', auth_required=False, client_required=False,
                    args=None, data=None, body=None):
        return _mb_request(path, method=method, auth_required=auth_required,
            client_required=client_required, args=args, data=data, body=body,
            client=self._client, hostname=self._hostname, useragent=self._useragent)


    def _do_mb_query(self, entity, id, includes=[], params={}):
        return _do_mb_query(entity=entity, id=id, includes=includes,
            params=params, client=self._client)

    def _do_mb_search(self, entity, query='', fields={},
              limit=None, offset=None, strict=False):
        return _do_mb_search(entity=entity, query=query, fields=fields,
              limit=limit, offset=offset, strict=strict,
              client=self._client, hostname=self._hostname, useragent=self._useragent)

    def _do_mb_delete(self, path):
        """Send a DELETE request for the specified object.
        """
        return self._mb_request(path, 'DELETE', True, True)

    def _do_mb_put(self, path):
        """Send a PUT request for the specified object.
        """
        return self._mb_request(path, 'PUT', True, True)

    def _do_mb_post(path, body):
        """Perform a single POST call for an endpoint with a specified
        request body.
        """
        return _mb_request(path, 'POST', True, True, body=body)


    def get_artist_by_id(self, id, includes=[], release_status=[], release_type=[]):
        """Get the artist with the MusicBrainz `id` as a dict with an 'artist' key.

        *Available includes*: {includes}"""
        params = _check_filter_and_make_params("artist", includes,
                                               release_status, release_type)
        return self._do_mb_query("artist", id, includes, params)


    def get_label_by_id(self, id, includes=[], release_status=[], release_type=[]):
        """Get the label with the MusicBrainz `id` as a dict with a 'label' key.

        *Available includes*: {includes}"""
        params = _check_filter_and_make_params("label", includes,
                                               release_status, release_type)
        return self._do_mb_query("label", id, includes, params)


    def get_recording_by_id(self, id, includes=[], release_status=[], release_type=[]):
        """Get the recording with the MusicBrainz `id` as a dict
        with a 'recording' key.

        *Available includes*: {includes}"""
        params = _check_filter_and_make_params("recording", includes,
                                               release_status, release_type)
        return _do_mb_query("recording", id, includes, params)

    def get_release_by_id(self, id, includes=[], release_status=[], release_type=[]):
        """Get the release with the MusicBrainz `id` as a dict with a 'release' key.

        *Available includes*: {includes}"""
        params = _check_filter_and_make_params("release", includes,
                                               release_status, release_type)
        return self._do_mb_query("release", id, includes, params)

    def get_release_group_by_id(self, id, includes=[],
                                release_status=[], release_type=[]):
        """Get the release group with the MusicBrainz `id` as a dict
        with a 'release-group' key.

        *Available includes*: {includes}"""
        params = _check_filter_and_make_params("release-group", includes,
                                               release_status, release_type)
        return self._do_mb_query("release-group", id, includes, params)

    def get_work_by_id(self, id, includes=[]):
        """Get the work with the MusicBrainz `id` as a dict with a 'work' key.

        *Available includes*: {includes}"""
        return self._do_mb_query("work", id, includes)

    def get_url_by_id(self, id, includes=[]):
        """Get the url with the MusicBrainz `id` as a dict with a 'url' key.

        *Available includes*: {includes}"""
        return self._do_mb_query("url", id, includes)


    # Searching

    def search_annotations(self, query='', limit=None, offset=None, strict=False, **fields):
        """Search for annotations and return a dict with an 'annotation-list' key.

        *Available search fields*: {fields}"""
        return _do_mb_search('annotation', query, fields, limit, offset, strict)

    def search_artists(self, query='', limit=None, offset=None, strict=False, **fields):
        """Search for artists and return a dict with an 'artist-list' key.

        *Available search fields*: {fields}"""
        return self._do_mb_search('artist', query, fields, limit, offset, strict)

    def search_labels(self, query='', limit=None, offset=None, strict=False, **fields):
        """Search for labels and return a dict with a 'label-list' key.

        *Available search fields*: {fields}"""
        return self._do_mb_search('label', query, fields, limit, offset, strict)

    def search_recordings(self, query='', limit=None, offset=None,
                          strict=False, **fields):
        """Search for recordings and return a dict with a 'recording-list' key.

        *Available search fields*: {fields}"""
        return self._do_mb_search('recording', query, fields, limit, offset, strict)

    def search_releases(self, query='', limit=None, offset=None, strict=False, **fields):
        """Search for recordings and return a dict with a 'recording-list' key.

        *Available search fields*: {fields}"""
        return self._do_mb_search('release', query, fields, limit, offset, strict)

    def search_release_groups(self, query='', limit=None, offset=None,
                  strict=False, **fields):
        """Search for release groups and return a dict
        with a 'release-group-list' key.

        *Available search fields*: {fields}"""
        return self._do_mb_search('release-group', query, fields, limit, offset, strict)

    def search_works(self, query='', limit=None, offset=None, strict=False, **fields):
        """Search for works and return a dict with a 'work-list' key.

        *Available search fields*: {fields}"""
        return self._do_mb_search('work', query, fields, limit, offset, strict)


    def _browse_impl(self, entity, includes, valid_includes, limit, offset, params, release_status=[], release_type=[]):
        _check_includes_impl(includes, valid_includes)
        p = {}
        for k,v in params.items():
            if v:
                p[k] = v
        if len(p) > 1:
            raise Exception("Can't have more than one of " + ", ".join(params.keys()))
        if limit: p["limit"] = limit
        if offset: p["offset"] = offset
        filterp = _check_filter_and_make_params(entity, includes, release_status, release_type)
        p.update(filterp)
        return self._do_mb_query(entity, "", includes, p)

    # Browse methods
    # Browse include are a subset of regular get includes, so we check them here
    # and the test in _do_mb_query will pass anyway.
    def browse_artists(recording=None, release=None, release_group=None,
                       includes=[], limit=None, offset=None):
        """Get all artists linked to a recording, a release or a release group.
        You need to give one MusicBrainz ID.

        *Available includes*: {includes}"""
        # optional parameter work?
        valid_includes = VALID_BROWSE_INCLUDES['artists']
        params = {"recording": recording,
                  "release": release,
                  "release-group": release_group}
        return self._browse_impl("artist", includes, valid_includes,
                            limit, offset, params)

    def browse_labels(release=None, includes=[], limit=None, offset=None):
        """Get all labels linked to a relase. You need to give a MusicBrainz ID.

        *Available includes*: {includes}"""
        valid_includes = VALID_BROWSE_INCLUDES['labels']
        params = {"release": release}
        return self._browse_impl("label", includes, valid_includes,
                            limit, offset, params)

    def browse_recordings(artist=None, release=None, includes=[],
                          limit=None, offset=None):
        """Get all recordings linked to an artist or a release.
        You need to give one MusicBrainz ID.

        *Available includes*: {includes}"""
        valid_includes = VALID_BROWSE_INCLUDES['recordings']
        params = {"artist": artist,
                  "release": release}
        return self._browse_impl("recording", includes, valid_includes,
                            limit, offset, params)

    def browse_releases(artist=None, label=None, recording=None,
                        release_group=None, release_status=[], release_type=[],
                        includes=[], limit=None, offset=None):
        """Get all releases linked to an artist, a label, a recording
        or a release group. You need to give one MusicBrainz ID.

        You can filter by :data:`musicbrainz.VALID_RELEASE_TYPES` or
        :data:`musicbrainz.VALID_RELEASE_STATUSES`.

        *Available includes*: {includes}"""
        # track_artist param doesn't work yet
        valid_includes = VALID_BROWSE_INCLUDES['releases']
        params = {"artist": artist,
                  "label": label,
                  "recording": recording,
                  "release-group": release_group}
        return self._browse_impl("release", includes, valid_includes, limit, offset,
                            params, release_status, release_type)

    def browse_release_groups(artist=None, release=None, release_type=[],
                              includes=[], limit=None, offset=None):
        """Get all release groups linked to an artist or a release.
        You need to give one MusicBrainz ID.

        You can filter by :data:`musicbrainz.VALID_RELEASE_TYPES`.

        *Available includes*: {includes}"""
        valid_includes = VALID_BROWSE_INCLUDES['release-groups']
        params = {"artist": artist,
                  "release": release}
        return self._browse_impl("release-group", includes, valid_includes,
                            limit, offset, params, [], release_type)

    def browse_urls(resource=None, includes=[], limit=None, offset=None):
        """Get urls by actual URL string.
        You need to give a URL string as 'resource'

        *Available includes*: {includes}"""
        # optional parameter work?
        valid_includes = VALID_BROWSE_INCLUDES['urls']
        params = {"resource": resource}
        return self._browse_impl("url", includes, valid_includes,
                            limit, offset, params)
