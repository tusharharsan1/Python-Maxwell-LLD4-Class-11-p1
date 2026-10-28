"""Run this file to see what your guest-list code does:   python try_it.py
It asks the two functions a few questions and prints the answers. Nothing is saved, and nothing needs the internet.
Do not change this file."""
try:
    from app.guest_list import check_access, read_bearer
except Exception as exc:  # a mistake in the file above would stop the import
    raise SystemExit(f"a file has a problem -> {type(exc).__name__}: {exc}")

# What each token carried when it was made (its claims), by token text.
TOKENS = {
    "t-asha": {"sub": "1", "role": "CUSTOMER"},  # made while Asha was a customer
    "t-ravi": {"sub": "2", "role": "ADMIN"},  # the token says ADMIN, but the guest list does not
    "t-mina": {"sub": "3", "role": "CUSTOMER"},  # Mina's account was deleted later
    "t-bare": {"role": "ADMIN"},  # claims without a "sub"
}
# The guest list: always up to date.
USERS = {
    "1": {"email": "asha@shop.com", "role": "ADMIN"},  # promoted after her token was made
    "2": {"email": "ravi@shop.com", "role": "CUSTOMER"},
}
ADMINS = ("ADMIN",)
EVERYONE = ("CUSTOMER", "ADMIN")


def show(label, text):
    print(f"  {label:<38}: {text}")


def reads(label, header):
    try:
        show(label, repr(read_bearer(header)))
    except Exception as exc:
        show(label, f"something is wrong -> {type(exc).__name__}: {exc}")


def asks(label, header, allowed=ADMINS):
    try:
        show(label, str(check_access(header, TOKENS, USERS, allowed)))
    except Exception as exc:
        show(label, f"something is wrong -> {type(exc).__name__}: {exc}")


print("Task 1: door 1 reads the header")
reads("Bearer t-asha", "Bearer t-asha")
reads("bearer t-asha (small letters)", "bearer t-asha")
reads("Basic t-asha (another word)", "Basic t-asha")
reads("Bearer (no token)", "Bearer")
reads("Bearer and an empty token", "Bearer ")
reads("t-asha (one word)", "t-asha")
reads("Bearer t-asha extra (three words)", "Bearer t-asha extra")
reads("no header at all", None)
print("Task 2: doors 2 and 3 look at the guest list")
asks("no header", None)
asks("another first word", "Basic t-asha")
asks("a token nobody made", "Bearer made-up")
asks("claims without a sub", "Bearer t-bare")
asks("the account was deleted", "Bearer t-mina")
asks("promoted after the token was made", "Bearer t-asha")
asks("token says ADMIN, list says CUSTOMER", "Bearer t-ravi")
asks("Ravi at a door for everyone", "Bearer t-ravi", EVERYONE)
