from unittest import TestCase

from parameterized import parameterized

from workers_control.core.email import is_possibly_an_email_address


class IsPossiblyAnEmailAddressTests(TestCase):
    @parameterized.expand(
        [
            ("name@example.org",),
            ("name+tag@example.org",),
            ("first.last@example.org",),
            ("o'neil@example.org",),
            ("a_b-c@sub.example.org",),
            ("a!#$%&*/=?^`{|}~b@example.org",),
            ("Jörg@example.org",),
            ("name@bücher.de",),
            ("name@नमस्ते.भारत",),
            ("name@mail.local",),
        ]
    )
    def test_that_plausible_addresses_are_accepted(self, address: str) -> None:
        self.assertTrue(is_possibly_an_email_address(address))

    @parameterized.expand(
        [
            ("",),
            ("word",),
            ("@",),
            (" @ ",),
            ("a@",),
            ("a@ ",),
            ("@b",),
            ("@b.c",),
            ("a@b",),
            ("a@b.",),
            ("a@.b",),
            ("a@b@c.d",),
            ("a b@c.d",),
            (" a@c.d",),
            ("a@c.d ",),
            ("a\t@c.d",),
            ("a​@c.d",),
            ("a\ud800@c.d",),
            ("a@c.d,e@f.g",),
            ("a@c.d\ne@f.g",),
        ]
    )
    def test_that_text_that_is_not_a_single_address_is_rejected(
        self, text: str
    ) -> None:
        self.assertFalse(is_possibly_an_email_address(text))

    @parameterized.expand(
        [
            ("<>@example.org",),
            ("<a@example.org>",),
            ("a<b@example.org",),
            ("a<b@example.org>",),
            ("a:b@example.org",),
            ("a:b@example.org;",),
            ("a;b@example.org",),
            ("a(b)@example.org",),
            ("a@example.org(b)",),
            ('a"@example.org',),
            ('"a b"@example.org',),
            ("a[b@example.org",),
            ("a@[1.2.3.4]",),
            ("a\\b@example.org",),
        ]
    )
    def test_that_addresses_with_special_characters_are_rejected(
        self, address: str
    ) -> None:
        self.assertFalse(is_possibly_an_email_address(address))

    @parameterized.expand(
        [
            (".a@example.org",),
            ("a.@example.org",),
            ("a..b@example.org",),
        ]
    )
    def test_that_misplaced_dots_in_the_local_part_are_rejected(
        self, address: str
    ) -> None:
        self.assertFalse(is_possibly_an_email_address(address))

    @parameterized.expand(
        [
            ("a@.example.org",),
            ("a@example.org.",),
            ("a@example..org",),
            ("a@-example.org",),
            ("a@example-.org",),
            ("a@exa_mple.org",),
            ("a@exam!ple.org",),
            ("a@exam/ple.org",),
            ("a@example.org/",),
        ]
    )
    def test_that_malformed_domains_are_rejected(self, address: str) -> None:
        self.assertFalse(is_possibly_an_email_address(address))

    def test_that_address_of_254_bytes_is_accepted(self) -> None:
        self.assertTrue(is_possibly_an_email_address("a" * 242 + "@example.org"))

    def test_that_address_of_255_bytes_is_rejected(self) -> None:
        self.assertFalse(is_possibly_an_email_address("a" * 243 + "@example.org"))

    def test_that_length_is_counted_in_bytes_instead_of_characters(self) -> None:
        self.assertFalse(is_possibly_an_email_address("ö" * 122 + "@example.org"))
