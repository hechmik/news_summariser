import sys
sys.path.insert(1, "../src/")
from main import activate_endpoint, load_model

import pytest


@pytest.fixture
def client():
    import json
    with open("../src/config/settings.json", "r") as f:
        settings = json.load(f)
    load_model(settings)
    app = activate_endpoint(settings)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_endpoint(client):
    text = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras in massa eleifend, vulputate orci eget, commodo massa. Integer et lorem sed dui rutrum porta. Vivamus in aliquam leo. Phasellus sit amet elit porta, fringilla quam vitae, iaculis magna. Nam et vestibulum leo. Quisque lacus nisl, convallis quis massa eget, pretium accumsan diam. Quisque eget maximus nunc. Duis efficitur, augue vitae tincidunt finibus, eros sem facilisis leo, vel aliquam sapien leo placerat metus. Praesent nec pretium lacus, ut scelerisque quam. In hac habitasse platea dictumst. Maecenas lacinia, lectus nec lacinia tempus, risus nulla cursus ligula, condimentum placerat neque lorem quis eros. Cras euismod orci massa, at fermentum massa pretium in. Nullam rhoncus laoreet euismod. In accumsan iaculis augue in fermentum. Nulla ligula velit, fringilla a iaculis quis, dignissim ut ante. '

    summary = client.post("/", data={'rawtext': text})
    import logging
    logging.info(summary.data)
    assert summary.data is not None