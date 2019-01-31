# -*- coding: utf-8 -*-
# (c) 2014 Mind Candy Ltd. All Rights Reserved.
# Licensed under the MIT License; you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://opensource.org/licenses/MIT.

from fattoush import (
    util,
    step,
)


def _send_to_search_box(wd, keys):
    search_box = wd.find_element_by_css_selector('form input[title=Search]')
    search_box.send_keys(keys)


@step(u'I open "([^"]*)" in my web browser')
@util.with_wd_from_step()
def i_open_url_in_my_web_browser(wd, url):
    wd.get(url)


@step(u'I expect the url to start with "([^"]*)"')
@util.with_wd_from_step()
def i_expect_the_url_to_start_with(wd, url):
    current_url = wd.current_url

    assert current_url.startswith(url), '{!r} did not start with {!r}'.format(
        current_url, url
    )


@step(u'I type "([^"]*)" into the search box')
@util.with_wd_from_step()
def i_type_search_term_into_the_search_box(wd, search_term):
    _send_to_search_box(wd, search_term)


@step(u'I submit the search')
@util.with_wd_from_step()
def i_submit_the_search(wd):
    _send_to_search_box(wd, '\n')


@step(u'I expect the top result to contain the string "([^"]*)"')
@util.with_wd_from_step()
def i_expect_the_top_result_to_contain_the_string_search_term(
    wd,
    search_term,
):

    @util.retry(times=5, wait=1, catch=IndexError)
    def top_result():
        return wd.find_elements_by_class_name('rc')[0]

    actual = top_result().text

    assert search_term in actual, '{!r} not in {!r}'.format(
        search_term, actual
    )
