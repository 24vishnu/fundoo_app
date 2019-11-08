from locust import HttpLocust, TaskSet


class UserBehavior(TaskSet):
    def on_start(self):
        """ on_start is called when a Locust start before any task is scheduled """
        self.login()  # done
        # self.signup() # done duplicate not allowed
        # self.upload()
        self.update()
        # self.profile()  # Done
        # self.forgot_password() # Done

    def on_stop(self):
        """ on_stop is called when the TaskSet is stopping """
        # self.profile()

    # @task(1)
    def login(self):
        """
        :return: login with username and password
        """
        self.client.post("/login/", {"username": "admin", "password": "admin"})

    # @task(2)
    def forgot_password(self):
        """
        :return: send mail if user forgot there password
        """
        self.client.post("/forgotpassword/", {'email': 'vishnu23kumar@gmail.com'})

    # @task(3)
    def upload(self):
        """
        :return: upload a file file
        """
        self.client.post("/upload/", {'image': ''})

    def update(self):
        """
        :return: upload a file file
        """
        self.client.post("/upload/1", {'image': '/home/user/Pictures/22.png'})

    # @task(4)
    def signup(self):
        """
        :return: register new users
        """
        self.client.post("/signup/",
                         {'username': 'noothan', 'email': 'noothan1@gmail.com', 'password': 'noothan123'})

    def profile(self):
        """
        :return: show the users profile
        """
        self.client.get("/user/")


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 1
    max_wait = 1
