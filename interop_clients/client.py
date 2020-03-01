"""
Basic Python client for the interop server.
"""

import requests


class InteropError(Exception):
    """
    Generic exception thrown by InteropClient.

    All exceptions thrown by InteropClient should be subclasses of this.
    """


class InteropClient:
    """
    Client providing authenticated access to the Judge's interoperability
    server.

    All methods may raise an InteropError.

    Constructing the client sends a login request, and all future requests use
    this authenticated cookie.
    """

    def __init__(self, url, username, password):
        """
        Create new client and login.

        Args:
            url: Base URL of interop server (e.g. "http://localhost:8080").
            username: Interop username.
            password: Interop password.
        """
        self.session = requests.Session()
        self.url = url

        self.post(
            "/api/login", json=dict(username=username, password=password)
        )

    def get(self, uri, **kwargs):
        """
        GET request to server.

        This is a wrapper around `self.session.get`.

        Args:
            uri: Server URI without base URL (e.g. "/api/teams").
            kwargs: Arguments to pass to `requests.Session.get`.

        Raises:
            InteropError: When the GET request returns an error.
        """
        r = self.session.get(self.url + uri, **kwargs)
        if not r.ok:
            raise InteropError(r)
        return r

    def post(self, uri, **kwargs):
        """
        POST request to server.

        This is a wrapper around `self.session.post`.

        Args:
            uri: Server URI without base URL (e.g. "/api/teams").
            kwargs: Arguments to pass to `requests.Session.post`.

        Raises:
            InteropError: When the POST request returns an error.
        """
        r = self.session.post(self.url + uri, **kwargs)
        if not r.ok:
            raise InteropError(r)
        return r

    def put(self, uri, **kwargs):
        """
        PUT request to server.

        This is a wrapper around `self.session.put`.

        Args:
            uri: Server URI without base URL (e.g. "/api/teams").
            kwargs: Arguments to pass to `requests.Session.put`.

        Raises:
            InteropError: When the PUT request returns an error.
        """
        r = self.session.put(self.url + uri, **kwargs)
        if not r.ok:
            raise InteropError(r)
        return r

    def delete(self, uri):
        """
        DELETE request to server.

        This is a wrapper around `self.session.delete`.

        Args:
            uri: Server URI without base URL (e.g. "/api/teams").

        Raises:
            InteropError: When the DELETE request returns an error.
        """
        r = self.session.put(self.url + uri)
        if not r.ok:
            raise InteropError(r)
        return r

    def get_teams(self):
        """
        GET the status of teams.

        Returns:
            List of team status dicts for active teams.
        """
        return self.get("/api/teams").json()

    def get_mission(self, mission_id):
        """
        GET mission information by ID.

        Args:
            mission_id: ID of mission to get.
        Returns:
            Mission information dict.
        """
        return self.get(f"/api/missions/{mission_id}").json()

    def post_telemetry(self, telem):
        """
        POST new telemetry.

        Args:
            telem: Telemetry object containing telemetry state.
        """
        self.post("/api/telemetry", json=telem)

    def get_odlcs(self, mission=None):
        """
        GET list of odlcs (targets).

        Args:
            mission: Optional ID of mission to restrict by.
        Returns:
            List of odlc dicts.
        """
        url = "/api/odlcs"
        if mission is not None:
            url += f"?mission={mission}"
        return self.get(url).json()

    def get_odlc(self, odlc_id):
        """
        GET odlc by ID.

        Args:
            odlc_id: ID of odlc to get.
        Returns:
            odlc dict with given ID.
        """
        return self.get(f"/api/odlcs/{odlc_id}").json()

    def post_odlc(self, odlc):
        """
        POST odlc.

        This gets the image ID, content, and all other required information
        from `odlc`.

        Args:
            odlc: Dict of odlc information to post.
        Returns:
            odlc dict with given ID.
        """
        self.post(f"/api/odlcs", json=odlc)

    def put_odlc(self, odlc_id, odlc):
        """
        PUT odlc.

        Args:
            odlc_id: ID of odlc to update.
            odlc: Next dict of odlc details. Missing keys are left unchanged.
        """
        self.put(f"/api/odlcs/{odlc_id}", json=odlc)

    def delete_odlc(self, odlc_id):
        """
        DELETE odlc.

        Args:
            odlc_id: ID of odlc to delete.
        """
        self.delete(f"/api/odlcs/{odlc_id}")

    def get_odlc_image(self, odlc_id):
        """
        GET raw odlc image bytes.

        Args:
            odlc_id: ID of odlc to get.
        Returns:
            Raw thumbnail data for given odlc.
        """
        return self.get(f"/api/odlcs/{odlc_id}/image").content

    def post_odlc_image(self, odlc_id, image_data):
        """
        PUT odlc.

        `image_data` must be either a PNG or a JPG.

        Args:
            odlc_id: ID of odlc for which to upload image_data.
            image_data: Raw image bytes to upload.
        """
        self.put_odlc_image(odlc_id, image_data)

    def put_odlc_image(self, odlc_id, image_data):
        """
        PUT odlc.

        `image_data` must be either a PNG or a JPG.

        Args:
            odlc_id: ID of odlc for which to upload image_data.
            image_data: Raw image bytes to upload.
        """
        self.put(f"/api/odlcs/{odlc_id}/image", data=image_data)

    def delete_odlc_image(self, odlc_id):
        """
        DELETE odlc.

        Args:
            odlc_id: ID of odlc which is being deleted.
        """
        self.delete(f"/api/odlcs/{odlc_id}/image")
