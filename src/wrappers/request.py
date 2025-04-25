import shutil
import requests
from lxml import etree
from loguru import logger

from wrappers import HEADER


class Request:
    @staticmethod
    def get_response(src_url: str) -> requests.Response:
        """
        Sends a GET request to the specified URL and returns the response object if successful.
        Args:
            src_url (str): The URL to send the GET request to.
        Returns:
            requests.Response: The response object if the request is successful.
            bool: False if an error occurs during the request.
        Raises:
            requests.exceptions.Timeout: If the request times out.
            requests.ConnectionError: If there is no internet connection.
            requests.exceptions.HTTPError: If the HTTP request returns an unsuccessful status code.
            Exception: For any other exceptions that may occur.
        """
        error = ""
        try:
            response = requests.get(src_url, headers=HEADER, stream=True, timeout=180)
            response.raise_for_status()

            return response
        except requests.exceptions.Timeout:
            error = f"Timeout connection: {src_url}"
        except requests.ConnectionError:
            error = "No internet connection"
        except requests.exceptions.HTTPError:
            error = f"Not found: {src_url}"
        except Exception as error:
            pass

        logger.error(error)
        return False

    def download(self, src_url: str, dst_path: str) -> None:
        """
        Downloads a file from the specified source URL and saves it to the given destination path.
        Args:
            src_url (str): The URL of the file to be downloaded.
            dst_path (str): The local file path where the downloaded file will be saved.
        Returns:
            None
        Raises:
            Any exceptions raised by the `get_response` method or file operations.
        """

        response = self.get_response(src_url)
        if not response:
            logger.error(f"Failed to download file from {src_url}")
            return
        
        with open(dst_path, "wb") as file:
            shutil.copyfileobj(response.raw, file)

    def get_xml_respone(self, src_url: str, tg=None) -> set:
        """
        Fetches and parses an XML response from the given source URL.
        Args:
            src_url (str): The source URL to fetch the XML data from.
            tg (str, optional): The tag to filter XML elements during 
                parsing. Defaults to None.
        Returns:
            set: A set containing the text content of the parsed XML 
                elements matching the specified tag.
        """

        response = self.get_response(src_url)
        xml_parser = etree.iterparse(response.raw, tag=tg)

        return {elem.text for _, elem in xml_parser}
