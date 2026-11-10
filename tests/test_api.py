from fastapi.testclient import TestClient

from agentops import api
from agentops.core import Checkpoints


def test_api_round_trip(tmp_path, monkeypatch):
    monkeypatch.setattr(api, "db", Checkpoints(str(tmp_path / "api.db")))
    client = TestClient(api.app)
    assert client.get("/health").status_code == 200
    r = client.post(
        "/incidents/investigate",
        json={
            "incident_id": "INC-2200",
            "service": "billing",
            "symptom": "slow responses",
        },
    )
    assert r.status_code == 200 and r.json()["status"] == "awaiting_approval"
    assert client.get("/incidents/INC-2200").status_code == 200
    assert (
        client.post(
            "/incidents/INC-2200/approve",
            json={"approved": False, "reviewer": "oncall"},
        ).json()["status"]
        == "rejected"
    )
