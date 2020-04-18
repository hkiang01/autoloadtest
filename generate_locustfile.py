import importlib

from fastapi import FastAPI

FASTAPI_APP_MODULE = "app"
FASTAPI_APP_OBJECT = "app"

app_module = importlib.import_module(FASTAPI_APP_MODULE)
app: FastAPI = eval(f"app_module.{FASTAPI_APP_OBJECT}")
app_openapi_spec: dict = app.openapi()


hypothesis_methods = {
    "integer": "hypothesis.strategies.integers().example()",
    "string": "hypothesis.strategies.text().example()",
}


def generate_route_test_method(
    openapi_path_name: str, openapi_path_dict: dict
) -> str:
    """
    Assumes:
    - even sampling of methods
    """
    http_verb = list(openapi_path_dict.keys())[0]
    method_name = (
        openapi_path_dict[http_verb]["summary"].lower().replace(" ", "_")
    )

    locust_url = openapi_path_name

    if "parameters" in list(openapi_path_dict[http_verb].keys()):
        parameters = openapi_path_dict[http_verb]["parameters"]

        # path params
        path_parameters = list(filter(lambda p: p["in"] == "path", parameters))
        for path_param in path_parameters:

            to_replace = "{" + path_param["name"] + "}"
            replacement = (
                "{" + hypothesis_methods[path_param["schema"]["type"]] + "}"
            )
            locust_url = locust_url.replace(to_replace, replacement)

        # query params
        query_parameters = list(
            filter(lambda p: p["in"] == "query", parameters)
        )
        if len(query_parameters) > 0:
            locust_url = locust_url + "?"
        for query_param in query_parameters:
            locust_url = (
                locust_url
                + f"{query_param['name']}="
                + "{"
                + hypothesis_methods[query_param["schema"]["type"]]
                + "}"
            )
        locust_url = locust_url.rstrip("&")

    # generate method string
    route_test_method = f"""
def {method_name}(l):
    l.client.{http_verb}(f"{locust_url}")
    """

    return (method_name, route_test_method)


locustfile_contents = """
import hypothesis
from locust import HttpLocust, TaskSet, between

"""

locust_tasks = []
for route_name in list(app_openapi_spec["paths"].keys()):
    locust_task, route_test_method = generate_route_test_method(
        route_name, app_openapi_spec["paths"][route_name]
    )
    locustfile_contents = locustfile_contents + (route_test_method)
    locust_tasks.append(locust_task)

locustfile_contents = (
    locustfile_contents
    + f"""
class UserBehavior(TaskSet):
    tasks = {repr(locust_tasks).replace("'", "")}


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    wait_time = between(5.0, 9.0)

"""
)

with open("locustfile.py", "wt") as fp:
    fp.write(locustfile_contents)
