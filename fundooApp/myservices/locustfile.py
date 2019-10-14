from locust import HttpLocust, TaskSet, task


class UserBehavior(TaskSet):
    def on_start(self):
        """ on_start is called when a Locust start before any task is scheduled """
        self.login()
        self.signup()
        self.upload()
        self.forgot_password()
        self.share_note()

    def on_stop(self):
        """ on_stop is called when the TaskSet is stopping """
        self.profile()

    @task(1)
    def login(self):
        """
        :return: login with username and password
        """
        self.client.post("/api/login/", {"username": "admin", "password": "admin"})

    @task(2)
    def forgot_password(self):
        """
        :return: send mail if user forgot there password
        """
        self.client.post("/api/forgot_password/", {'email': 'vishnu23kuamr@gmail.com'})

    @task(3)
    def upload(self):
        """
        :return: upload a file file
        """
        self.client.post("/api/upload/", {'file_details': ''})

    @task(4)
    def signup(self):
        """
        :return: register new users
        """
        self.client.post("/api/signup/",
                         {'username': 'noothan', 'email': 'noothan@gmail.com', 'password': 'noothan123'})

    @task(5)
    def share_note(self):
        """
        :return: share note title and note containt
        """
        self.client.post("/api/share_note/", {'note_title': 'load test', 'note_body': 'this is successful'})

    def profile(self):
        """
        :return: show the users profile
        """
        self.client.get("/api/user/")


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 1
    max_wait = 1
