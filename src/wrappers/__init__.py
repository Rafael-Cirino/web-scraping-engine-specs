"""
This module defines constants for HTTP request headers.

Constants:
    USER_AGENT (str): A string representing the User-Agent 
        header to identify the client making the request.
    HEADER (dict): A dictionary containing default HTTP headers, 
        including the User-Agent and Accept headers.
"""

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
HEADER = {"Accept": "application/xml; charset=utf-8", "User-Agent": USER_AGENT}
