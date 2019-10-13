from locust import HttpLocust, TaskSet, task


class UserBehavior(TaskSet):
    def on_start(self):
        """ on_start is called when a Locust start before any task is scheduled """
        self.login()
        self.signup()
        self.upload()
        self.profile()
        self.forgot_password()
        self.share_note()

    @task(1)
    def login(self):
        self.client.post("/api/login/", {"username": "admin", "password": "admin"})

    @task(2)
    def forgot_password(self):
        self.client.post("/api/forgot_password/", {'email': 'vishnu23kuamr@gmail.com'})

    @task(3)
    def upload(self):
        self.client.post("/api/upload/", {'file_details': ''})

    @task(4)
    def signup(self):
        self.client.post("/api/signup/",
                         {'username': 'noothan', 'email': 'noothan@gmail.com', 'password': 'noothan123'})

    @task(5)
    def share_note(self):
        self.client.post("/api/share_note/", {'note_title': 'load test', 'note_body': 'this is successful'})

    @task(6)
    def profile(self):
        self.client.get("/api/user/")


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 1
    max_wait = 1
