#!/usr/bin/env python3
# coding: utf-8

__all__ = ["create_cookie", "cookie_list_to_cookiejar"]

from http.cookiejar import Cookie, CookieJar


def create_cookie(name, value, **kwargs) -> Cookie:
    result = {
        'version': 0,
        'name': name,
        'value': value,
        'port': None,
        'domain': '',
        'path': '/',
        'secure': False,
        'expires': None,
        'discard': True,
        'comment': None,
        'comment_url': None,
        'rest': {'HttpOnly': None},
        'rfc2109': False, 
    }
    result.update((name, kwargs[name])
        for name in ("version", "name", "value", "port", "port_specified",
                     "domain", "domain_specified", "domain_initial_dot",
                     "path", "path_specified", "secure", "expires", "discard", 
                     "comment", "comment_url") 
        if name in kwargs
    )
    result['port_specified'] = bool(result['port'])
    result['domain_specified'] = bool(result['domain'])
    result['domain_initial_dot'] = result['domain'].startswith('.')
    result['path_specified'] = bool(result['path'])

    return Cookie(**result)


def cookie_list_to_cookiejar(cookie_list, cookiejar=None) -> CookieJar:
    if cookiejar is None:
        cookiejar = CookieJar()

    for cookie in cookie_list:
        if not isinstance(cookie, Cookie):
            cookie = create_cookie(**cookie)
        cookiejar.set_cookie(cookie)

    return cookiejar

