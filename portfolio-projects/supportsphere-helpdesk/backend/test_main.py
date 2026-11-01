import os
import tempfile
import unittest
from fastapi.testclient import TestClient
import main

class HelpdeskTests(unittest.TestCase):
    def setUp(self):
        self.previous=main.DB
        self.temp=tempfile.TemporaryDirectory()
        main.DB=__import__("pathlib").Path(self.temp.name)/"test.db"
        main.setup()
        self.client=TestClient(main.app)
    def tearDown(self):
        main.DB=self.previous
        self.temp.cleanup()
    def test_ticket_lifecycle(self):
        created=self.client.post("/tickets",json={"title":"Test laptop issue","description":"Windows does not boot","requester":"Test User","priority":"High"})
        self.assertEqual(created.status_code,201)
        tid=created.json()["id"]
        updated=self.client.patch(f"/tickets/{tid}",json={"status":"In Progress","assignee":"Lab Tech"})
        self.assertEqual(updated.status_code,200)
        self.assertEqual(updated.json()["assignee"],"Lab Tech")
        comment=self.client.post(f"/tickets/{tid}/comments",json={"author":"Lab Tech","body":"Checking logs"})
        self.assertEqual(comment.status_code,201)
        detail=self.client.get(f"/tickets/{tid}").json()
        self.assertEqual(len(detail["comments"]),1)
        self.assertGreaterEqual(len(detail["history"]),2)
    def test_bad_status_and_missing_ticket(self):
        self.assertEqual(self.client.patch("/tickets/1",json={"status":"INVALID"}).status_code,422)
        self.assertEqual(self.client.get("/tickets/999999").status_code,404)
    def test_mock_directory_is_labelled(self):
        data=self.client.get("/lab/directory/jsmith").json()
        self.assertFalse(data["connected_to_ad"])
        self.assertEqual(data["source"],"mock-fixture")

if __name__=="__main__": unittest.main()
