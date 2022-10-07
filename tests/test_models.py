from models import MessageAdapter


class TestMessageAdapter:
    def test_trim_wrong_characters_from_header(self, message_constructor):
        text = "\u200bA test title to be trimmed  \n\nnext line"
        msg = message_constructor(text=text)
        expected_title = "A test title to be trimmed"

        title = MessageAdapter.get_header([msg])

        assert title == expected_title
