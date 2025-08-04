"""Génération de la page"""

import logging
import pytest

from src.utils.utils import contexte_actuel
from .contexte import contexte

LOGGER = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def first_page(contexte):
    """
    Création de la première page (fixture niveau session appelée en début de session)
    """

    first_page = contexte.new_page()

    yield first_page


@pytest.fixture(scope="function", autouse=True)
def page(first_page, contexte):
    """
    Fournit la même page et capture un screenshot à la fin de chaque test.
    """
    methode_name = contexte_actuel()
    LOGGER.debug("[FIXTURE PAGE %s] ----  DEBUT ----", methode_name)

    pages = contexte.pages
    page = pages[-1]

    # page.on("request", lambda request: print(request.url + " " + request.failure))

    # page.on("request", lambda request: print(
    #     f"all_headers {request.all_headers}\n",
    #     f"failure {request.failure}\n",
    #     f"frame {request.frame}\n",
    #     f"header_value {request.header_value}\n",
    #     f"headers {request.headers}\n",
    #     f"headers_array {request.headers_array}\n",
    #     f"is_navigation_request {request.is_navigation_request}\n",
    #     f"method {request.method}\n",
    #     f"on {request.on}\n",
    #     f"once {request.once}\n",
    #     f"post_data {request.post_data}\n",
    #     f"post_data_buffer {request.post_data_buffer}\n",
    #     f"post_data_json {request.post_data_json}\n",
    #     f"redirected_from {request.redirected_from}\n",
    #     f"redirected_to {request.redirected_to}\n",
    #     f"remove_listener {request.remove_listener}\n",
    #     f"resource_type {request.resource_type}\n",
    #     f"response {request.response}\n",
    #     f"sizes {request.sizes}\n",
    #     f"timing {request.timing}\n",
    #     f"url {request.url}"
    # ))

    # page.on("response", handle_response)

    # page.on("response", lambda response: print(
    #     f"all_headers : {response.request}\n",
    #     f"body : {response.body}\n",
    #     f"finished : {response.finished}\n",
    #     f"frame : {response.frame}\n",
    #     f"from_service_worker : {response.from_service_worker}\n",
    #     f"header_value : {response.header_value}\n",
    #     f"header_values : {response.header_values}\n",
    #     f"headers : {response.headers}\n",
    #     f"headers_array : {response.headers_array}\n",
    #     f"json : {response.json}\n",
    #     f"ok : {response.ok}\n",
    #     f"on : {response.on}\n",
    #     f"once : {response.once}\n",
    #     f"remove_listener : {response.remove_listener}\n",
    #     f"request : {response.request}\n",
    #     f"security_details : {response.security_details}\n",
    #     f"server_addr : {response.server_addr}\n",
    #     f"status : {response.status}\n",
    #     f"status_text : {response.status_text}\n",
    #     f"text : {response.text}\n",
    #     f"url : {response.url}\n"
    # ))

    # page.on("request", lambda request: print("REQUEST", request.method, request.url))
    # page.on("response", handle_response)
    # page.on("pageerror", lambda exc: print(f"Page error uncaught exception: {exc}"))
    # page.on("crash", lambda exc: print(f"Crash uncaught exception: {exc}"))
    # page.context.on("weberror", lambda web_error: print(f"Weberror uncaught exception: {web_error.error}"))

    yield page

    LOGGER.debug("[FIXTURE PAGE %s] liste des pages : %s", methode_name, page)

    LOGGER.debug("[FIXTURE PAGE %s] ----   FIN  ----", methode_name)
