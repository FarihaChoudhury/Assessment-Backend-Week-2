"""This file contains tests for the API."""

from unittest.mock import patch


class TestAPIClownGet:
    """Contains tests for the /clown GET route"""

    @patch("app.conn")
    def test_get_clown_returns_200(self, mock_conn, test_app, fake_clown):
        """Tests that the /clown endpoint returns 200 on a GET request."""

        mock_conn.cursor.return_value\
            .__enter__.return_value\
            .fetchall.return_value = [fake_clown]

        res = test_app.get("/clown")

        assert res.status_code == 200

    @patch("app.conn")
    def test_get_clown_returns_list_of_dicts(self, mock_conn, test_app, fake_clown):
        """Tests that the /clown endpoint returns a list of valid dicts
        on a GET request"""

        mock_conn.cursor.return_value\
            .__enter__.return_value\
            .fetchall.return_value = [fake_clown]

        res = test_app.get("/clown")
        data = res.json

        assert isinstance(data, list)
        assert all(isinstance(c, dict) for c in data)
        assert all("clown_id" in c
                   for c in data)

    @patch("app.conn")
    def test_get_clown_accesses_database(self, mock_conn, test_app):
        """Tests that the /clown endpoint makes expected calls to the database
        on a GET request."""

        mock_execute = mock_conn.cursor.return_value\
            .__enter__.return_value\
            .execute
        mock_fetch = mock_conn.cursor.return_value\
            .__enter__.return_value\
            .fetchall

        test_app.get("/clown")

        assert mock_execute.call_count == 2
        assert mock_fetch.call_count == 2

    """Test 1) """
    @patch("app.conn")
    def test_get_clown_with_id(self, mock_conn, test_app, fake_data):
        """Test that /clown/id returns data for that specified id"""
        mock_conn.cursor.return_value\
            .__enter__.return_value\
            .fetchall.return_value = [fake_data]

        res = test_app.get("/clown/18")
        data = res.json

        assert isinstance(data, list)
        assert all(isinstance(c, dict) for c in data)
        assert all("clown_id" in c
                   for c in data)
        assert data[0]['clown_name'] == "Fariha"
        assert data[0]['clown_id'] == 18

    @patch("app.conn")
    def test_get_clown_returns_name_speciality(self, mock_conn, test_app, fake_data):
        """Test that /clown returns name and speciality for that specified id"""
        mock_conn.cursor.return_value\
            .__enter__.return_value\
            .fetchall.return_value = [fake_data]

        res = test_app.get("/clown")
        data = res.json
        print(data[0].keys())

        assert isinstance(data, list)

        assert 'clown_name' in data[0]
        assert 'speciality_id' in data[0]


class TestAPIClownPost:
    """Contains tests for the /clown POST route"""

    @patch("app.conn")
    def test_post_clown_returns_201(self, mock_conn, test_app, fake_clown):
        """Tests that the /clown endpoint returns 201 on a POST request."""

        mock_conn.cursor.return_value\
            .__enter__.return_value\
            .fetchone.return_value = [fake_clown]

        res = test_app.post("/clown", json=fake_clown)

        assert res.status_code == 201

    @patch("app.conn")
    def test_post_clown_returns_400_on_invalid(self, mock_conn, test_app):
        """Tests that the /clown endpoint returns 400 on a POST request
        with an invalid body."""

        mock_conn.cursor.return_value\
            .__enter__.return_value\
            .fetchone.return_value = {}

        assert test_app.post("/clown", json={}).status_code == 400
        assert test_app.post("/clown", json={"clown_name": "A",
                                             "speciality_id": "r"}).status_code == 400

    @patch("app.conn")
    def test_post_clown_calls_db(self, mock_conn, test_app):
        """Tests that the /clown endpoint makes the expected calls to the db
        on a POST request."""

        mock_execute = mock_conn.cursor.return_value\
            .__enter__.return_value\
            .execute
        mock_fetch = mock_conn.cursor.return_value\
            .__enter__.return_value\
            .fetchone

        mock_fetch.return_value = {}

        _ = test_app.post("/clown", json={"clown_name": "Miriam",
                                          "speciality_id": 1})

        assert mock_fetch.call_count == 1
        assert mock_execute.call_count == 1


class TestAPIReviewPost:
    """Contains tests for the /clown/id/review POST route
        Test 2) """

    @patch("app.conn")
    def test_post_review_returns_201(self, mock_conn, test_app, fake_review):
        """Tests that the /clown/id/review endpoint returns 201 on a POST request."""

        mock_conn.cursor.return_value\
            .__enter__.return_value\
            .fetchone.return_value = [fake_review]

        res = test_app.post("/clown/17/review", json=fake_review)

        assert res.status_code == 201

    @patch("app.conn")
    def test_invalid_post_review_returns_404(self, mock_conn, test_app, fake_invalid_review):
        """Tests that the /clown/id/review endpoint returns 404 on an invalid POST request."""

        mock_conn.cursor.return_value\
            .__enter__.return_value\
            .fetchone.return_value = [fake_invalid_review]

        res = test_app.post("/clown/17/review", json=fake_invalid_review)

        assert res.status_code == 404

    @patch("app.conn")
    def test_post_review_calls_db(self, mock_conn, test_app, fake_review):
        """Tests that the /clown/id/review endpoint makes the expected calls to the db
        on a POST request."""

        mock_execute = mock_conn.cursor.return_value\
            .__enter__.return_value\
            .execute
        mock_fetch = mock_conn.cursor.return_value\
            .__enter__.return_value\
            .fetchone

        mock_fetch.return_value = {}

        _ = test_app.post("/clown/17/review", json=fake_review)

        assert mock_fetch.call_count == 1
        assert mock_execute.call_count == 1
