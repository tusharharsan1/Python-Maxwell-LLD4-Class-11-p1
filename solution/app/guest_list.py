from typing import Dict, Optional, Sequence, Tuple

# The three refusal messages, so that nobody has to type them.
NOT_AUTHENTICATED = "Not authenticated"
BAD_TOKEN = "Invalid or expired token"
NOT_ALLOWED = "You are not allowed to do this"


def read_bearer(header: Optional[str]) -> Optional[str]:
    """Door 1. Give back the token text from an Authorization header, or None when there is no usable token."""
    if header is None:
        return None  # no header, so no token
    # "Bearer t-asha" becomes ["Bearer", "t-asha"]. Any other shape gives a different number of words.
    parts = header.split(" ")
    # Exactly two words, the first one is "Bearer" in any capital letters, and the token is not empty.
    if len(parts) != 2 or parts[0].lower() != "bearer" or parts[1] == "":
        return None
    return parts[1]


def check_access(
    authorization: Optional[str],
    tokens: Dict[str, dict],
    users: Dict[str, dict],
    allowed_roles: Sequence[str],
) -> Tuple[int, str]:
    """Doors 2 and 3. Give back a pair (status, message)."""
    token = read_bearer(authorization)
    if token is None:
        return 401, NOT_AUTHENTICATED  # nobody brought a pass
    # Door 2: who is it? A token nobody made gives {}, and {}.get("sub") gives None, and no user has the id None.
    claims = tokens.get(token, {})
    user = users.get(claims.get("sub"))
    if user is None:
        return 401, BAD_TOKEN  # an unknown token, claims without a sub, or an account that was deleted
    # Door 3: what may this user do? The role comes from the guest list (users), NOT from the claims of the token.
    if user["role"] not in allowed_roles:
        return 403, NOT_ALLOWED
    return 200, user["email"]
