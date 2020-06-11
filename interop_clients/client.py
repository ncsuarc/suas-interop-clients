"""Basic Python client for the SUAS Interop server."""

from typing import Any, List, Optional

import requests

from interop_clients import api


class InteropError(Exception):
    """Generic exception thrown by InteropClient.

    All exceptions thrown by InteropClient should be subclasses of this.
    """


class InteropClient:
    """Client providing authenticated access to the interop server.

    All methods may raise an InteropError.

    Constructing the client sends a single login request. All future requests
    use this authenticated cookie.
    """

    def __init__(self, url: str, username: str, password: str) -> None:
        """Create new client and login.

        Args:
            url: Base URL of interop server (e.g. "http://localhost:8080").
            username: Interop username.
            password: Interop password.

        Raises:
            InteropError: When the provided username or password are incorrect.
                When the interop server cannot be reached.
        """
        self.session = requests.Session()
        self.url = url

        self._post(
            "/api/login",
            json=api.Credentials(username=username, password=password),
        )

    def _get(self, uri: str, **kwargs: Any) -> requests.Response:
        """GET request to server.

        This is a wrapper around `self.session.get`.

        Args:
            uri: Server URI without base URL (e.g. "/api/teams").
            kwargs: Arguments to pass to `requests.Session.get`.

        Raises:
            InteropError: When the GET request returns an error.
        """
        r = self.session.get(self.url + uri, **kwargs)
        if not r.ok:
            raise InteropError(r.text)
        return r

    def _post(self, uri: str, **kwargs: Any) -> requests.Response:
        """POST request to server.

        This is a wrapper around `self.session.post`.

        Args:
            uri: Server URI without base URL (e.g. "/api/teams").
            kwargs: Arguments to pass to `requests.Session.post`.

        Raises:
            InteropError: When the POST request returns an error.
        """
        r = self.session.post(self.url + uri, **kwargs)
        if not r.ok:
            raise InteropError(r.text)
        return r

    def _put(self, uri: str, **kwargs: Any) -> requests.Response:
        """PUT request to server.

        This is a wrapper around `self.session.put`.

        Args:
            uri: Server URI without base URL (e.g. "/api/teams").
            kwargs: Arguments to pass to `requests.Session.put`.

        Raises:
            InteropError: When the PUT request returns an error.
        """
        r = self.session.put(self.url + uri, **kwargs)
        if not r.ok:
            raise InteropError(r.text)
        return r

    def _delete(self, uri: str) -> requests.Response:
        """DELETE request to server.

        This is a wrapper around `self.session.delete`.

        Args:
            uri: Server URI without base URL (e.g. "/api/teams").

        Raises:
            InteropError: When the DELETE request returns an error.
        """
        r = self.session.delete(self.url + uri)
        if not r.ok:
            raise InteropError(r.text)
        return r

    def get_teams(self) -> List[api.TeamStatus]:
        """GET the status of teams.

        Returns:
            List of team status dicts for active teams.
        """
        return self._get("/api/teams").json()

    def get_mission(self, mission_id: api.Id) -> api.Mission:
        """GET mission information by ID.

        Args:
            mission_id: ID of mission to get.
        Returns:
            Mission information dict.
        """
        return self._get(f"/api/missions/{mission_id}").json()

    def post_telemetry(self, telem: api.Telemetry) -> None:
        """POST new telemetry.

        Args:
            telem: Telemetry object containing telemetry state.
        """
        self._post("/api/telemetry", json=telem)

    def get_odlcs(self, mission: Optional[api.Id] = None) -> List[api.Odlc]:
        """GET list of odlcs (targets).

        Args:
            mission: Optional ID of mission to restrict by.
        Returns:
            List of odlc dicts.
        """
        url = "/api/odlcs"
        if mission is not None:
            url += f"?mission={mission}"
        return self._get(url).json()

    def get_odlc(self, odlc_id: api.Id) -> api.Odlc:
        """GET odlc by ID.

        Args:
            odlc_id: ID of odlc to get.
        Returns:
            odlc dict with given ID.
        """
        return self._get(f"/api/odlcs/{odlc_id}").json()

    def post_odlc(self, odlc: api.NewOdlc) -> api.Id:
        """POST odlc.

        This is for posting new ODLCs.

        TODO: Fact check this info

        Args:
            odlc: Dict of odlc information to post. Must not contain "id"
            because that will be filled in by the server.
        Returns:
            ID assigned to the given ODLC.
        """
        return self._post("/api/odlcs", json=odlc).json()["id"]

    def put_odlc(self, odlc_id: api.Id, odlc: api.Odlc) -> None:
        """PUT odlc.

        Args:
            odlc_id: ID of odlc to update.
            odlc: Next dict of odlc details. Missing keys are left unchanged.
            The ODLC ID must agree.
        """
        self._put(f"/api/odlcs/{odlc_id}", json=odlc)

    def delete_odlc(self, odlc_id: api.Id) -> None:
        """DELETE odlc.

        Args:
            odlc_id: ID of odlc to delete.
        """
        self._delete(f"/api/odlcs/{odlc_id}")

    def get_odlc_image(self, odlc_id: api.Id) -> bytes:
        """GET raw odlc image bytes.

        Args:
            odlc_id: ID of odlc to get.
        Returns:
            Raw thumbnail data for given odlc.
        """
        return self._get(f"/api/odlcs/{odlc_id}/image").content

    def put_odlc_image(self, odlc_id: api.Id, image_data: bytes) -> None:
        """PUT odlc.

        `image_data` must be either a PNG or a JPG.

        Args:
            odlc_id: ID of odlc for which to upload image_data.
            image_data: Raw image bytes to upload.
        """
        self._put(f"/api/odlcs/{odlc_id}/image", data=image_data)

    def delete_odlc_image(self, odlc_id: api.Id) -> None:
        """DELETE odlc.

        Args:
            odlc_id: ID of odlc which is being deleted.
        """
        self._delete(f"/api/odlcs/{odlc_id}/image")
