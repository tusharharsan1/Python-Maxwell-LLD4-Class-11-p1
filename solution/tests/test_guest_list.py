"""Tests for app/guest_list.py (standard library only). Run them from the folder that holds `app/` and `tests/`:

    python -m unittest -v          (pytest works too)

The tests check what the README says: door 1 reads the header, door 2 finds the user, door 3 checks the role,
the role comes from the guest list and not from the token, 401 speaks before 403, and nothing crashes."""
import copy
import inspect
import itertools
import random
import unittest

from app import guest_list
from app.guest_list import BAD_TOKEN, NOT_ALLOWED, NOT_AUTHENTICATED, check_access, read_bearer

ADMINS = ("ADMIN",)
EVERYONE = ("CUSTOMER", "ADMIN")


def fixture():
    """The data of try_it.py. A new copy for every test, so that no test can disturb another one."""
    tokens = {
        "t-asha": {"sub": "1", "role": "CUSTOMER"},  # made while Asha was a customer
        "t-ravi": {"sub": "2", "role": "ADMIN"},  # the token says ADMIN, but the guest list does not
        "t-mina": {"sub": "3", "role": "CUSTOMER"},  # Mina's account was deleted later
        "t-bare": {"role": "ADMIN"},  # claims without a "sub"
    }
    users = {
        "1": {"email": "asha@shop.com", "role": "ADMIN"},  # promoted after her token was made
        "2": {"email": "ravi@shop.com", "role": "CUSTOMER"},
    }
    return tokens, users


def reference_bearer(header):
    """The rule of the README, written separately from the student's code."""
    if header is None:
        return None
    parts = header.split(" ")
    if len(parts) == 2 and parts[0].lower() == "bearer" and parts[1] != "":
        return parts[1]
    return None


def reference_access(authorization, tokens, users, allowed_roles):
    token = reference_bearer(authorization)
    if token is None:
        return 401, "Not authenticated"
    claims = tokens.get(token)
    if claims is None or "sub" not in claims or claims["sub"] not in users:
        return 401, "Invalid or expired token"
    user = users[claims["sub"]]
    if user["role"] not in allowed_roles:
        return 403, "You are not allowed to do this"
    return 200, user["email"]


def random_header(rng, token_pool):
    """A header made of one, two or three words. Only shapes that the README answers clearly are made."""
    if rng.randrange(12) == 0:
        return rng.choice([None, "", "Bearer "])
    first = rng.choice(["Bearer", "bearer", "BEARER", "bEaReR", "Basic", "Token", "Bearerx", "Bear"])
    count = rng.choice([1, 2, 2, 2, 2, 3])
    words = [first] + [rng.choice(token_pool + ["extra", "x"]) for _ in range(count - 1)]
    if count == 2:
        return rng.choice([" ", " ", " ", "  ", "\t"]).join(words)
    return " ".join(words)


class FinishedPartsTests(unittest.TestCase):
    def test_the_three_messages_are_unchanged(self):
        self.assertEqual(guest_list.NOT_AUTHENTICATED, "Not authenticated")
        self.assertEqual(guest_list.BAD_TOKEN, "Invalid or expired token")
        self.assertEqual(guest_list.NOT_ALLOWED, "You are not allowed to do this")

    def test_the_names_of_the_functions_and_their_parameters_are_unchanged(self):
        self.assertEqual(list(inspect.signature(read_bearer).parameters), ["header"])
        self.assertEqual(list(inspect.signature(check_access).parameters), ["authorization", "tokens", "users", "allowed_roles"])


class ReadBearerTests(unittest.TestCase):
    def test_the_table_of_the_readme(self):
        table = [
            ("Bearer t-asha", "t-asha"),
            ("bearer t-asha", "t-asha"),
            ("BEARER t-asha", "t-asha"),
            (None, None),
            ("Basic t-asha", None),
            ("Bearer", None),
            ("Bearer ", None),
            ("t-asha", None),
            ("Bearer t-asha extra", None),
        ]
        for header, expected in table:
            with self.subTest(header=header):
                self.assertEqual(read_bearer(header), expected)

    def test_any_capital_letters_in_the_word_bearer_are_fine(self):
        for letters in itertools.product(*[(c.lower(), c.upper()) for c in "bearer"]):
            word = "".join(letters)
            with self.subTest(word=word):
                self.assertEqual(read_bearer(word + " tok"), "tok")

    def test_the_token_is_given_back_exactly_as_it_was_sent(self):
        for token in ["abc", "ABC", "aBc", "a.b.c", "eyJ-_=", "t-1", "0", "caf" + chr(233), "T-ASHA"]:
            with self.subTest(token=token):
                self.assertEqual(read_bearer("Bearer " + token), token)

    def test_the_answer_is_text_or_none_and_nothing_else(self):
        self.assertIs(type(read_bearer("Bearer tok")), str)
        self.assertIsNone(read_bearer(None))
        self.assertIsNone(read_bearer("Basic tok"))

    def test_one_space_between_the_words_not_more(self):
        for header in ["Bearer  tok", "Bearer   tok", "bearer  tok"]:
            with self.subTest(header=header):
                self.assertIsNone(read_bearer(header))

    def test_a_tab_is_not_a_space(self):
        self.assertIsNone(read_bearer("Bearer\ttok"))

    def test_another_first_word_gives_none(self):
        for word in ["Basic", "Token", "Bearerx", "xBearer", "Bear", "Bearer:", "Bearers", "Digest"]:
            with self.subTest(word=word):
                self.assertIsNone(read_bearer(word + " tok"))

    def test_one_word_and_three_or_more_words_give_none(self):
        for header in ["tok", "Bearer", "Bearer a b", "Bearer a b c", "bearer tok extra", "a b c d"]:
            with self.subTest(header=header):
                self.assertIsNone(read_bearer(header))

    def test_empty_texts_give_none(self):
        for header in ["", "Bearer ", "bearer ", " "]:
            with self.subTest(header=header):
                self.assertIsNone(read_bearer(header))

    def test_random_headers_follow_the_rule(self):
        rng = random.Random(11)
        wrong = []
        for _ in range(600):
            header = random_header(rng, ["t-asha", "tok", "TOK", "a.b.c", "x="])
            got = read_bearer(header)
            if got != reference_bearer(header):
                wrong.append((header, reference_bearer(header), got))
        if wrong:
            lines = "\n".join("  header %r: expected %r, got %r" % item for item in wrong[:3])
            self.fail("%d of 600 random headers were read wrong. The first ones:\n%s" % (len(wrong), lines))


class DoorTests(unittest.TestCase):
    def ask(self, header, allowed=ADMINS):
        tokens, users = fixture()
        return check_access(header, tokens, users, allowed)

    def test_the_examples_of_the_readme(self):
        table = [
            (None, ADMINS, (401, "Not authenticated")),
            ("Basic t-asha", ADMINS, (401, "Not authenticated")),
            ("Bearer made-up", ADMINS, (401, "Invalid or expired token")),
            ("Bearer t-bare", ADMINS, (401, "Invalid or expired token")),
            ("Bearer t-mina", ADMINS, (401, "Invalid or expired token")),
            ("Bearer t-asha", ADMINS, (200, "asha@shop.com")),
            ("Bearer t-ravi", ADMINS, (403, "You are not allowed to do this")),
            ("Bearer t-ravi", EVERYONE, (200, "ravi@shop.com")),
        ]
        for header, allowed, expected in table:
            with self.subTest(header=header, allowed=allowed):
                self.assertEqual(self.ask(header, allowed), expected)

    def test_every_answer_is_a_pair_of_a_number_and_a_text(self):
        for header in [None, "Basic x", "Bearer made-up", "Bearer t-asha", "Bearer t-ravi"]:
            with self.subTest(header=header):
                answer = self.ask(header)
                self.assertIs(type(answer), tuple)
                self.assertEqual(len(answer), 2)
                self.assertIs(type(answer[0]), int)
                self.assertIs(type(answer[1]), str)

    def test_no_header_is_401_even_at_an_admin_door(self):
        self.assertEqual(self.ask(None, ADMINS), (401, NOT_AUTHENTICATED))
        self.assertEqual(self.ask(None, ()), (401, NOT_AUTHENTICATED))

    def test_a_header_with_another_first_word_is_401_not_authenticated(self):
        for header in ["Basic t-asha", "Token t-asha", "t-asha", "Bearer", "Bearer ", "Bearer t-asha extra"]:
            with self.subTest(header=header):
                self.assertEqual(self.ask(header), (401, NOT_AUTHENTICATED))

    def test_an_unknown_token_is_401_and_never_403(self):
        for header in ["Bearer made-up", "Bearer ", "Bearer x", "bearer nobody", "BEARER 123"]:
            for allowed in [ADMINS, EVERYONE, ("CUSTOMER",), ()]:
                with self.subTest(header=header, allowed=allowed):
                    answer = self.ask(header, allowed)
                    if header == "Bearer ":
                        self.assertEqual(answer, (401, NOT_AUTHENTICATED))
                    else:
                        self.assertEqual(answer, (401, BAD_TOKEN))

    def test_the_token_text_must_match_exactly(self):
        tokens, users = fixture()
        tokens["tok"] = {"sub": "1"}
        tokens["TOK"] = {"sub": "2"}
        self.assertEqual(check_access("Bearer tok", tokens, users, EVERYONE), (200, "asha@shop.com"))
        self.assertEqual(check_access("Bearer TOK", tokens, users, EVERYONE), (200, "ravi@shop.com"))
        self.assertEqual(check_access("Bearer Tok", tokens, users, EVERYONE), (401, BAD_TOKEN))

    def test_claims_without_a_sub_are_401(self):
        self.assertEqual(self.ask("Bearer t-bare", ADMINS), (401, BAD_TOKEN))
        self.assertEqual(self.ask("Bearer t-bare", EVERYONE), (401, BAD_TOKEN))
        tokens, users = fixture()
        tokens["t-empty"] = {}
        self.assertEqual(check_access("Bearer t-empty", tokens, users, EVERYONE), (401, BAD_TOKEN))

    def test_a_deleted_account_is_401_not_403_and_not_an_error(self):
        for allowed in [ADMINS, EVERYONE, ("CUSTOMER",), ()]:
            with self.subTest(allowed=allowed):
                self.assertEqual(self.ask("Bearer t-mina", allowed), (401, BAD_TOKEN))

    def test_a_promoted_user_gets_in_with_the_old_token(self):
        # the token still says CUSTOMER, but the guest list says ADMIN
        self.assertEqual(self.ask("Bearer t-asha", ADMINS), (200, "asha@shop.com"))

    def test_a_token_that_claims_admin_does_not_make_an_admin(self):
        # the token says ADMIN, but the guest list says CUSTOMER
        self.assertEqual(self.ask("Bearer t-ravi", ADMINS), (403, NOT_ALLOWED))

    def test_the_role_inside_the_token_is_not_needed(self):
        tokens, users = fixture()
        tokens["t-plain"] = {"sub": "1"}
        self.assertEqual(check_access("Bearer t-plain", tokens, users, ADMINS), (200, "asha@shop.com"))

    def test_the_guest_list_is_read_on_every_call(self):
        tokens, users = fixture()
        steps = [("ADMIN", 200), ("CUSTOMER", 403), ("ADMIN", 200), ("CUSTOMER", 403), ("ADMIN", 200)]
        for role, status in steps:
            users["1"]["role"] = role
            with self.subTest(role=role):
                self.assertEqual(check_access("Bearer t-asha", tokens, users, ADMINS)[0], status)
        del users["1"]
        self.assertEqual(check_access("Bearer t-asha", tokens, users, ADMINS), (401, BAD_TOKEN))
        users["1"] = {"email": "asha@shop.com", "role": "ADMIN"}
        self.assertEqual(check_access("Bearer t-asha", tokens, users, ADMINS), (200, "asha@shop.com"))

    def test_the_email_comes_from_the_guest_list(self):
        tokens, users = fixture()
        tokens["t-liar"] = {"sub": "2", "email": "boss@shop.com", "role": "ADMIN"}
        self.assertEqual(check_access("Bearer t-liar", tokens, users, EVERYONE), (200, "ravi@shop.com"))

    def test_several_allowed_roles_in_any_kind_of_collection(self):
        for allowed in [("CUSTOMER", "ADMIN"), ["ADMIN", "CUSTOMER"], {"CUSTOMER", "ADMIN"}, frozenset(["SELLER", "CUSTOMER"])]:
            with self.subTest(allowed=allowed):
                self.assertEqual(self.ask("Bearer t-ravi", allowed), (200, "ravi@shop.com"))
        for allowed in [("ADMIN",), ["SELLER", "ADMIN"], {"SELLER"}]:
            with self.subTest(allowed=allowed):
                self.assertEqual(self.ask("Bearer t-ravi", allowed), (403, NOT_ALLOWED))

    def test_no_allowed_role_means_403_for_a_known_user(self):
        self.assertEqual(self.ask("Bearer t-asha", ()), (403, NOT_ALLOWED))
        self.assertEqual(self.ask("Bearer t-ravi", []), (403, NOT_ALLOWED))

    def test_the_role_must_match_exactly(self):
        tokens, users = fixture()
        users["1"]["role"] = "admin"
        self.assertEqual(check_access("Bearer t-asha", tokens, users, ADMINS), (403, NOT_ALLOWED))

    def test_the_inputs_are_not_changed(self):
        tokens, users = fixture()
        allowed = ["ADMIN"]
        before = copy.deepcopy((tokens, users, allowed))
        for header in [None, "Basic x", "Bearer made-up", "Bearer t-asha", "Bearer t-ravi", "Bearer t-mina", "Bearer t-bare"]:
            check_access(header, tokens, users, allowed)
        self.assertEqual((tokens, users, allowed), before)

    def test_check_access_reads_the_header_the_same_way_as_read_bearer(self):
        tokens, users = fixture()
        headers = [None, "", "Bearer ", "Bearer  t-asha", "Bearer\tt-asha", "bearer t-asha", "BEARER t-asha", "Bearer t-asha x", "Basic t-asha"]
        for header in headers:
            with self.subTest(header=header):
                answer = check_access(header, tokens, users, EVERYONE)
                if read_bearer(header) is None:
                    self.assertEqual(answer, (401, NOT_AUTHENTICATED))
                else:
                    self.assertNotEqual(answer, (401, NOT_AUTHENTICATED))

    def test_random_data_follows_the_rule(self):
        rng = random.Random(7)
        roles = ["CUSTOMER", "ADMIN", "SELLER", "SUPPORT", "admin"]
        wrong = []
        for _ in range(500):
            users = {}
            for number in range(rng.randrange(0, 5)):
                users["u%d" % number] = {"email": "user%d@shop.com" % number, "role": rng.choice(roles)}
            tokens = {}
            for number in range(rng.randrange(0, 6)):
                claims = {}
                if rng.randrange(5) != 0:
                    claims["sub"] = rng.choice(["u0", "u1", "u2", "u3", "u4", "gone"])
                if rng.randrange(2):
                    claims["role"] = rng.choice(roles)
                tokens["tok%d" % number] = claims
            allowed = rng.choice([tuple, list, set, frozenset])(rng.sample(roles, rng.randrange(0, 4)))
            header = random_header(rng, list(tokens) + ["tok9", "made-up"])
            snapshot = copy.deepcopy((tokens, users))
            expected = reference_access(header, tokens, users, allowed)
            got = check_access(header, tokens, users, allowed)
            if got != expected or (tokens, users) != snapshot:
                wrong.append((header, tokens, users, allowed, expected, got))
        if wrong:
            lines = "\n".join(
                "  header %r, tokens %r, users %r, allowed %r:\n    expected %r, got %r" % item for item in wrong[:3]
            )
            self.fail("%d of 500 random cases were wrong. The first ones:\n%s" % (len(wrong), lines))


if __name__ == "__main__":
    unittest.main()
