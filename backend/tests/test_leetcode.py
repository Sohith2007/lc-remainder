import pytest

from app.leetcode import html_to_text


@pytest.mark.parametrize(
    "html, expected",
    [
        ("<p>Hello <strong>world</strong></p>", "Hello world"),
        ("<p>You are given a <code>words</code> array.</p>", "You are given a words array."),
        ("<p>Intro</p><ul><li>One</li><li>Two</li></ul>", "Intro\n\n- One\n- Two"),
    ],
)
def test_html_to_text_strips_tags(html, expected):
    assert html_to_text(html) == expected