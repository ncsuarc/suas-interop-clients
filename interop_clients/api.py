"""Definition of the SUAS Interop API objects using `TypedDict`s.

This is hand-written alternative to the Python module generated by Protobuf's
`protoc` to avoid the dependency on protoc for users and to provide more
ergonomic API.
"""

import sys
from enum import IntEnum
from typing import List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


Id = int


class Credentials(TypedDict):
    username: str
    password: str


class Telemetry(TypedDict):
    latitude: float
    longitude: float
    altitude: float
    heading: float


class Position(TypedDict):
    latitude: float
    longitude: float
    altitude: Optional[float]


class FlyZone(TypedDict):
    altitude_min: float
    altitude_max: float
    boundary_points: List[Position]


class StationaryObstacle(TypedDict):
    latitude: float
    longitude: float
    radius: float
    height: float

class OdlcType(IntEnum):
    STANDARD = 1
    EMERGENT = 4


class OdlcOrientation(IntEnum):
    N = 1
    NE = 2
    E = 3
    SE = 4
    S = 5
    SW = 6
    W = 7
    NW = 8


class OdlcShape(IntEnum):
    CIRCLE = 1
    SEMICIRCLE = 2
    QUARTER_CIRCLE = 3
    TRIANGLE = 4
    SQUARE = 5
    RECTANGLE = 6
    TRAPEZOID = 7
    PENTAGON = 8
    HEXAGON = 9
    HEPTAGON = 10
    OCTAGON = 11
    STAR = 12
    CROSS = 13


class OdlcColor(IntEnum):
    WHITE = 1
    BLACK = 2
    GRAY = 3
    RED = 4
    BLUE = 5
    GREEN = 6
    YELLOW = 7
    PURPLE = 8
    BROWN = 9
    ORANGE = 10


class NewOdlc(TypedDict):
    """Odlc without an id"""

    mission: Id

    type: OdlcType

    # Must be specified together
    latitude: Optional[float]
    longitude: Optional[float]

    orientation: Optional[OdlcOrientation]

    shape: Optional[OdlcShape]

    alphanumeric: Optional[str]

    shape_color: Optional[OdlcColor]
    alphanumeric_color: Optional[OdlcColor]

    description: Optional[str]

    autonomous: bool


class Odlc(NewOdlc):
    id: Id


class TeamId(TypedDict):
    id: Id
    username: str
    name: str
    university: str


class TeamStatus(TypedDict):
    team: TeamId
    in_air: bool
    telemetry: Telemetry
    telemetry_id: int
    telemetry_age_sec: float
    telemetry_timestamp: str


class Mission(TypedDict):
    id: Id
    lost_comms_pos: Position
    fly_zones: List[FlyZone]
    waypoints: List[Position]
    search_grid_points: List[Position]
    off_axis_odlc_pos: Position
    emergent_last_known_pos: Position
    air_drop_boundary_points: List[Position]
    air_drop_pos: Position
    ugv_drive_pos: Position
    stationary_obstacles: List[StationaryObstacle]
