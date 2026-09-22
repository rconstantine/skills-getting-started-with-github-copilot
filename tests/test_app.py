from src import app as app_module


class TestRoot:
    def test_root_redirects_to_static_index(self, client):
        # Arrange
        expected_location = "/static/index.html"

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_location


class TestActivities:
    def test_get_activities_returns_activity_data(self, client):
        # Arrange
        expected_activity = app_module.activities["Chess Club"]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        assert response.json()["Chess Club"] == expected_activity


class TestSignup:
    def test_signup_adds_participant(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "new.student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup", params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {
            "message": f"Signed up {email} for {activity_name}"
        }
        assert email in app_module.activities[activity_name]["participants"]

    def test_signup_rejects_unknown_activity(self, client):
        # Arrange
        activity_name = "Unknown Club"
        email = "new.student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup", params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json() == {"detail": "Activity not found"}

    def test_signup_rejects_duplicate_participant(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = app_module.activities[activity_name]["participants"][0]
        initial_count = app_module.activities[activity_name]["participants"].count(email)

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup", params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert response.json() == {
            "detail": "Student is already signed up for this activity"
        }
        assert app_module.activities[activity_name]["participants"].count(email) == initial_count

    def test_signup_requires_email(self, client):
        # Arrange
        activity_name = "Chess Club"

        # Act
        response = client.post(f"/activities/{activity_name}/signup")

        # Assert
        assert response.status_code == 422
        assert response.json()["detail"][0]["loc"] == ["query", "email"]


class TestUnregister:
    def test_unregister_removes_participant(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = app_module.activities[activity_name]["participants"][0]

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup/{email}"
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {
            "message": f"Unregistered {email} from {activity_name}"
        }
        assert email not in app_module.activities[activity_name]["participants"]

    def test_unregister_rejects_unknown_activity(self, client):
        # Arrange
        activity_name = "Unknown Club"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup/{email}"
        )

        # Assert
        assert response.status_code == 404
        assert response.json() == {"detail": "Activity not found"}

    def test_unregister_rejects_nonparticipant(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "not.registered@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup/{email}"
        )

        # Assert
        assert response.status_code == 404
        assert response.json() == {
            "detail": "Student is not signed up for this activity"
        }
