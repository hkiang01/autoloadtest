from locust import HttpLocust, TaskSet, between


def index(l):
    l.client.get("/")


def item(l):
    l.client.post(f"/items/1?q=asdfasdf")


class UserBehavior(TaskSet):
    tasks = {index: 1, item: 1}


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    wait_time = between(5.0, 9.0)
