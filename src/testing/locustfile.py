from locust import HttpUser, TaskSet, task, between


class UserBehavior(TaskSet):
    @task(1)
    def test_endpoint(self):
        # Define the headers and payload for the POST request
        headers = {
            "Content-Type": "application/json",
        }
        payload = {
            "message": "Give me some papers on multimodal large language models."
        }
        # Make the POST request to the specified endpoint
        self.client.post("/v1/complete", json=payload, headers=headers)


class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(
        1, 5
    )  # Simulates a user waiting between 1 and 5 seconds between tasks


if __name__ == "__main__":
    import os

    os.system(
        "locust -f locustfile.py --host=http://localhost:8000"
    )