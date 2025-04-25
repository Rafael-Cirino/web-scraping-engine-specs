from pathlib import Path
from abc import ABC, abstractmethod
from dataclasses import dataclass

from wrappers.selenium_connection import SelConnection
from wrappers.request import Request


# Dataclass used as template for json output
@dataclass
class JsonSchema:
    """
    JsonSchema is a class that defines the structure of a JSON object used for
    representing product-related data.
    Attributes:
        product_id (str): The unique identifier for the product. Defaults to None.
        name (str): The name of the product. Defaults to None.
        description (str): A brief description of the product. Defaults to None.
        specs (dict): A dictionary containing the specifications of 
            the product. Defaults to None.
        bom (list): A list representing the Bill of Materials (BOM) for 
            the product. Defaults to None.
        assets (dict): A dictionary containing asset-related information for 
            the product. Defaults to None.
    """

    product_id: str = None
    name: str = None
    description: str = None
    specs: dict = None
    bom: list = None
    assets: dict = None


class BaseScrapping(ABC):
    def __init__(self) -> None:
        """
        Initializes the base scrapping class with default configurations.
        Attributes:
            connection (SelConnection): An instance of the SelConnection class 
                for managing Selenium connections.
            request (Request): An instance of the Request class for handling HTTP requests.
            product_info (JsonSchema): An instance of the JsonSchema class for managing 
                product information schemas.
            output_path (dict): A dictionary containing default output folder paths 
                for assets and metadata. The folders are created if they do not already exist.
        """

        self.connection = SelConnection()
        self.request = Request()
        self.product_info = JsonSchema()

        # Create default folders
        self.output_path = {
            "assets": Path("output/assets"),
            "metadata": Path("output/metadata"),
        }
        for path in self.output_path.values():
            path.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def get_products(
        self, limit: int, unique: list = None, processed_ids: set = None
    ) -> list:
        """
        Retrieves a list of products with an optional limit and filtering options.
        Args:
            limit (int): The maximum number of products to retrieve.
            unique (list, optional): A list of unique identifiers to filter 
                the products. Defaults to None.
            processed_ids (set, optional): A set of product IDs that have already been processed
                and should be excluded from the results. Defaults to None.
        Returns:
            list: A list of products matching the specified criteria.
        """

        pass

    @abstractmethod
    def run_scrapping(self, product_url: str) -> None:
        """
        Executes the web scraping process for the given product URL.

        Args:
            product_url (str): The URL of the product to scrape data from.

        Returns:
            None
        """

        pass
