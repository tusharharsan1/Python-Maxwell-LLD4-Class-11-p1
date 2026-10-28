from typing import Dict, Optional, Sequence, Tuple

# Already finished. The three refusal messages, so that you do not have to type them.
NOT_AUTHENTICATED = "Not authenticated"
BAD_TOKEN = "Invalid or expired token"
NOT_ALLOWED = "You are not allowed to do this"


def read_bearer(header: Optional[str]) -> Optional[str]:
    """Door 1. Give back the token text from an Authorization header, or None when there is no usable token."""
    if header is None:
        return None  # Already finished. It is your example: no header, so no token.
    # TODO 1 (Task 1): the header must be exactly two words with one space between them:
    #   the first word is "Bearer" (in any capital letters), the second is the token and it is not empty.
    #   Anything else (another first word, one word, three words, an empty token) gives None.
    return header  # placeholder: it is wrong on purpose. Replace it.


def check_access(
    authorization: Optional[str],
    tokens: Dict[str, dict],
    users: Dict[str, dict],
    allowed_roles: Sequence[str],
) -> Tuple[int, str]:
    """Doors 2 and 3. Give back a pair (status, message)."""
    token = read_bearer(authorization)
    if token is None:
        return 401, NOT_AUTHENTICATED  # Already finished. It is your example of one refusal.
    # TODO 2 (Task 2): find the claims of the token, then the user, then check the role.
    #   - the token is not in `tokens`, or its claims have no "sub", or that id is not in `users`: return 401, BAD_TOKEN
    #   - the role of the user ON THE GUEST LIST (`users`) is not in `allowed_roles`: return 403, NOT_ALLOWED
    #   - otherwise: return 200 and the email of the user
    return 200, "nobody"  # placeholder: it is wrong on purpose. Replace it.
