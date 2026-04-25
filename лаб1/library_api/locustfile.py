from locust import HttpUser, task, between


class LibraryUser(HttpUser):
    wait_time = between(1, 2)
    host = "http://host.docker.internal:8000"

    @task
    def login(self):
        self.client.post(
            "/auth/login",
            json={
                "username": "admin",
                "password": "admin123"
            },
        )