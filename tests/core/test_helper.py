from app.core.helper import helper

def test_parse_json():
        assert helper.parse_json('{"name": "test"}') == {"name": "test"}