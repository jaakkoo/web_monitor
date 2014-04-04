__author__ = 'Jaakko Aro'

import unittest
from mockito import *
from monitor_app.page_monitor import RequestedPage, MonitoredPage, NoResponse
from requests.exceptions import HTTPError


class MonitoredPageTest(unittest.TestCase):
    def setUp(self):
        self.target_url = 'testurl'
        self.required_string = 'Looking for this'
        self.max_response_time = 2
        self.page = MonitoredPage('Title', self.target_url, self.max_response_time, self.required_string)
        self.request_maker = mock()
        self.request_maker.response_time = 1
        self.request_maker.content = self.required_string
        when(self.request_maker).http_request(any()).thenReturn(self.request_maker)
        self.page.request_maker = self.request_maker
        self.page.refresh_status()

    def test_refresh_status_makes_new_request(self):
        verify(self.request_maker).http_request(self.target_url)

    def test_get_response_time_returns_page_response_time(self):
        self.assertEquals(1, self.page.get_response_time())

    def test_http_errors_are_handled_when_refreshing_status(self):
        when(self.request_maker).http_request(any()).thenRaise(HTTPError("Catch this!"))
        self.page.refresh_status()
        self.assertEquals(self.page._page, None)

    def test_required_string_is_found_from_content(self):
        self.assertTrue(self.page.contains_required_string())

    def test_response_time_is_checked(self):
        self.assertTrue(self.page.responds_fast_enough())

    def test_overall_status_is_true_when_all_requirements_are_met(self):
        self.assertTrue(self.page.get_status())

    def test_raises_exception_on_http_error(self):
        when(self.request_maker).http_request(any()).thenRaise(HTTPError("Catch this!"))
        self.page.refresh_status()
        self.assertRaises(NoResponse, lambda: self.page.get_status())

    def test_status_is_false_when_max_response_time_exceeds(self):
        self.page.max_response_time = 0.5
        self.assertFalse(self.page.get_status())

    def test_status_is_false_if_content_is_not_found(self):
        self.page.should_contain = 'Not there'
        self.assertFalse(self.page.get_status())


class HtmlPageTest(unittest.TestCase):
    def setUp(self):
        self.html_page = RequestedPage()

    def test_response_time_calculation(self):
        self.html_page.start_time = 100000000
        self.html_page.stop_time = 100000123
        self.assertEqual(self.html_page.response_time, 123)

