> **Where the files are:** this branch holds the finished solution in the `solution/` folder: the finished code, and the tests in `solution/tests/`. Every path below (such as `app/guest_list.py` and `try_it.py`) is inside `solution/`. Open a terminal in `solution/` to run the commands. To run the tests, type `python -m unittest -v` (or `pytest`) there. The starter files with the TODO notes are on the `main` branch, in `base/`.

# The Guest List at ShopNest

## Problem Statement
ShopNest's front door has three small checks in a row. **Door 1** reads the `Authorization` header and picks out the token. **Door 2** asks *who are you?*: it looks at the pass (the token), and then at the **guest list** (the users table) to see that the person is still there. **Door 3** asks *what may you do?*: it checks the **role**. In class, a library did door 1 and FastAPI ran the chain for us. Now you write the doors yourself, in plain Python, so you see exactly what they do: read the header, find the user, and take the role **from the guest list, not from the pass**. You need about 10 lines of code, in 2 small tasks. There is no web server and no database, and nothing needs to be installed.

## Requirements
### What `check_access` receives
| Name | What it is | Example |
|---|---|---|
| `authorization` | the text of the `Authorization` header, or `None` if the caller sent none | `"Bearer t-asha"` |
| `tokens` | the passes we know: the token text, and the claims it carried when it was made | `{"t-asha": {"sub": "1", "role": "CUSTOMER"}}` |
| `users` | the guest list: the id (as text), with the email and the role **today** | `{"1": {"email": "asha@shop.com", "role": "ADMIN"}}` |
| `allowed_roles` | the roles that may open this door | `("ADMIN",)` |

`check_access` gives back a pair `(status, message)`.

### What `read_bearer` does (door 1)
The header must be **exactly two words with one space between them**. The first word is `Bearer` (in any capital letters), and the second is the token. It must not be empty.

| The header | `read_bearer` gives |
|---|---|
| `"Bearer t-asha"` | `"t-asha"` |
| `"bearer t-asha"` or `"BEARER t-asha"` | `"t-asha"` |
| `None` (no header) | `None` |
| `"Basic t-asha"` (another first word) | `None` |
| `"Bearer"` or `"Bearer "` (no token, or an empty one) | `None` |
| `"t-asha"` (one word) | `None` |
| `"Bearer t-asha extra"` (three words) | `None` |

### What `check_access` does, in this order
| Step | The check | If it fails | Written already? |
|---|---|---|---|
| 1 | `read_bearer` finds a token | `(401, "Not authenticated")` | **yes** (the first lines of `check_access`) |
| 2 | the token is in `tokens`, its claims have a `"sub"`, and that id is in `users` | `(401, "Invalid or expired token")` | **no** (Task 2) |
| 3 | the role of that user **in `users`** is one of `allowed_roles` | `(403, "You are not allowed to do this")` | **no** (Task 2) |
| 4 | give back the email of the user | `(200, email)` | **no** (Task 2) |

The three messages are already written for you as `NOT_AUTHENTICATED`, `BAD_TOKEN` and `NOT_ALLOWED`.

### Examples (with the data used by `try_it.py`)
| The call | `check_access` gives |
|---|---|
| no header | `(401, "Not authenticated")` |
| `"Basic t-asha"` | `(401, "Not authenticated")` |
| `"Bearer made-up"` (nobody made this token) | `(401, "Invalid or expired token")` |
| a known token whose claims have no `"sub"` | `(401, "Invalid or expired token")` |
| a known token, but the account was deleted | `(401, "Invalid or expired token")` |
| the token says `CUSTOMER`, the guest list says `ADMIN` (promoted later), at an admin door | `(200, "asha@shop.com")` |
| the token says `ADMIN`, the guest list says `CUSTOMER`, at an admin door | `(403, "You are not allowed to do this")` |
| the same customer, at a door for `("CUSTOMER", "ADMIN")` | `(200, "ravi@shop.com")` |

### The rules
- **The order matters.** Door 2 speaks before door 3. Somebody we do not know gets `401`, **never** `403`, even at an admin door.
- **The role comes from the guest list, not from the token.** A token is a wristband printed in the morning, and it never changes. The guest list is always up to date. If they disagree, the **list wins**, in both directions: a promoted user gets in, and a token that claims `ADMIN` does not make anybody an admin.
- **Never crash.** A token with no `"sub"`, a deleted account, or any odd header text must end in a pair `(status, message)`, never in an error.
- **Do not change the dictionaries you receive.**

To achieve these requirements we need to do 2 things:
- **Task 1:** finish `read_bearer` (door 1).
- **Task 2:** finish `check_access`: the guest-list checks (steps 2, 3 and 4).

## Instructions
1. Open `app/guest_list.py`. We need to finish two functions: `read_bearer` has one TODO note (`TODO 1`) and `check_access` has one (`TODO 2`). The first lines of each function are already written, and they are your examples of a refusal.
2. **Task 1** is `TODO 1`: the header. **Task 2** is `TODO 2`: the token, the guest list, the role and the answer.
3. Do not modify the three message names (`NOT_AUTHENTICATED`, `BAD_TOKEN`, `NOT_ALLOWED`), the names of the two functions, their parameter names, or the lines that are already written. Feel free to add new functions if required.
4. Run `python try_it.py` from this folder (the one that contains `app/` and `try_it.py`) to see what your code does. When both tasks are finished, you should see exactly this:
   ```
   Task 1: door 1 reads the header
     Bearer t-asha                         : 't-asha'
     bearer t-asha (small letters)         : 't-asha'
     Basic t-asha (another word)           : None
     Bearer (no token)                     : None
     Bearer and an empty token             : None
     t-asha (one word)                     : None
     Bearer t-asha extra (three words)     : None
     no header at all                      : None
   Task 2: doors 2 and 3 look at the guest list
     no header                             : (401, 'Not authenticated')
     another first word                    : (401, 'Not authenticated')
     a token nobody made                   : (401, 'Invalid or expired token')
     claims without a sub                  : (401, 'Invalid or expired token')
     the account was deleted               : (401, 'Invalid or expired token')
     promoted after the token was made     : (200, 'asha@shop.com')
     token says ADMIN, list says CUSTOMER  : (403, 'You are not allowed to do this')
     Ravi at a door for everyone           : (200, 'ravi@shop.com')
   ```
   Before you start, `try_it.py` already runs: the Task 1 lines show the header text unchanged, and the Task 2 lines show `(200, 'nobody')`.
5. Your code will be checked with the test file `tests/test_guest_list.py`. It checks the cases in the Requirements above and the rules. While you write your code, use `python try_it.py` (instruction 4) to check your work.
6. You do not need to install anything, and you do not need a server, a database, the internet or a key. Only Python's standard library is used. It works with Python 3.8 or newer.
7. Hints (all of these use ideas from class):
   - **Door 1 (TODO 1).** `header.split(" ")` cuts the text at each space and gives a list of words. `.lower()` makes all letters small, so `Bearer`, `bearer` and `BEARER` look the same:
     ```python
     parts = header.split(" ")
     if len(parts) != 2 or parts[0].lower() != "bearer" or parts[1] == "":
         return None
     return parts[1]
     ```
   - **Doors 2 and 3 (TODO 2).** `dictionary.get(key, default)` gives the default when the key is missing, instead of an error. So `tokens.get(token, {})` gives an empty dictionary for a token nobody made, and `.get("sub")` on it gives `None`. The user is then looked up in `users`, **not** in the claims:
     ```python
     claims = tokens.get(token, {})
     user = users.get(claims.get("sub"))
     if user is None:
         return 401, BAD_TOKEN
     if user["role"] not in allowed_roles:
         return 403, NOT_ALLOWED
     return 200, user["email"]
     ```
   - **If something looks wrong.** If `token says ADMIN, list says CUSTOMER` shows `(200, ...)`, you read the role from the token: read `user["role"]` instead. If a line says `something is wrong -> KeyError: 'sub'`, the claims have no `"sub"`: use `.get("sub")`. If `the account was deleted` says `403` or an error, check that the user exists **before** you read the role. If `Bearer and an empty token` shows `''`, the second word must not be empty. If `Bearer (no token)` says `something is wrong -> IndexError`, check that there are exactly two words before you read the second.
