from ninja import Schema


class UserMiniOut(Schema):
    id: int
    username: str
    avatar_url: str | None
    tier: str


class UserWithStatsOut(UserMiniOut):
    punishment_count: int
    fikapinne_count: int
    is_bongskoterska: bool


class MeOut(UserMiniOut):
    force_password_reset: bool
    permissions: list[str]
