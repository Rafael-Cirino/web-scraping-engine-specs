import re
import ast
import random
from pathlib import Path
from loguru import logger

from wrappers.request import Request
from base_scrapping import BaseScrapping
from utils import convert_html_table, json_write

CATALOG_URL = (
    "https://www.baldor.com/api/products?include=results&language=en-US&pageSize=20000"
)
PRODUCT_URL = "https://www.baldor.com/catalog/"
PRODUCT_CODE_TAG = (
    "{http://schemas.datacontract.org/2004/07/Baldor.ProductData.Service}Code"
)


class ABBScrapping(BaseScrapping):
    def __init__(self, default_url_download: str):
        super().__init__()

        self.driver_page = None
        self.default_url_download = default_url_download

    @staticmethod
    def get_products(
        limit: int, unique: list = None, processed_ids: set = None
    ) -> list:
        """
        Retrieves a list of product URLs based on the specified criteria.
        Args:
            limit (int): The maximum number of product IDs to retrieve.
                If None, retrieves all available product IDs.
            unique (list, optional): A list of specific product IDs to retrieve.
                If None, retrieves all product IDs.
            processed_ids (set, optional): A set of product IDs to exclude from the results.
                If None, no filtering is applied.
        Returns:
            list: A list of product URLs corresponding to the retrieved product IDs.
        Raises:
            ValueError: If the `unique` parameter is provided but is not a list.
        """

        logger.info("Getting products id")

        # Get products ids, if unique is None get all products, else get only pruducts in unique
        if unique is None:
            products = Request().get_xml_respone(CATALOG_URL, tg=PRODUCT_CODE_TAG)

            if limit is not None:
                products = random.sample(list(products), limit)
        elif isinstance(unique, list):
            products = set(unique)
        else:
            raise ValueError(f"The unique config must be a list not {unique}")

        # Filter processed ids
        if processed_ids is not None:
            products = set(products).difference(processed_ids)

        return [PRODUCT_URL + prod for prod in products]

    def get_head(self) -> None:
        """
        Extracts and assigns product information such as product ID and description
        from the web page using the specified CSS selectors.
        Note:
            The product name is not retrieved as the site does not provide it.
        """

        # name: Site doesn't have

        self.product_info.product_id = self.connection.get_element_text(
            "CSS_SELECTOR", "div.page-title"
        )
        self.product_info.description = self.connection.get_element_text(
            "CSS_SELECTOR", "div.product-description"
        )

    def get_specs(self) -> None:
        """
        Extracts product specifications from the web page and stores them in the
        `specs` attribute of the `product_info` object.
        Returns:
            None: The method updates the `specs` attribute of the `product_info`
            object and does not return any value.
        Raises:
            ValueError: If the "specs" tab cannot be accessed.
        """

        try:
            self.connection.go_to_tab("//li[@data-tab='specs']")
        except ValueError:
            return

        spec_labels = self.connection.get_element_text(
            "CSS_SELECTOR", "span.label", elements=True
        )
        spec_values = self.connection.get_element_text(
            "CSS_SELECTOR", "span.value", elements=True
        )

        if (spec_labels is None) or (spec_values is None):
            logger.warning(f"{self.product_info.product_id}: Product without specs")
            return

        spec_labels = filter(lambda a: a != "", spec_labels)
        spec_values = filter(lambda a: a != "", spec_values)
        spec_dict = {}
        for label, value in zip(spec_labels, spec_values):
            label = label.replace(" ", "_").lower()

            all_finds = re.findall(r"\d+\.*\d*", value)
            spec_dict[label] = "/".join(all_finds)

        self.product_info.specs = spec_dict

    def get_bom(self) -> None:
        """
        Retrieves the Bill of Materials (BOM) for the current product
            and updates the product information.
        Returns:
            None: If the BOM is not found or the table is empty, the method exits early.
        Raises:
            ValueError: If navigation to the "parts" tab fails.
        Notes:
            - The BOM table is expected to be in HTML format and is
                converted into a pandas DataFrame.
            - The "quantity" column is processed to extract numerical values and converted to float.
            - Logs a warning if the product does not have a BOM.
        """

        try:
            self.connection.go_to_tab("//li[@data-tab='parts']")
        except ValueError:
            return

        tables = self.connection.find_element(
            "XPATH", "//div[@class='pane active' and @data-tab='parts']"
        )
        df_table = convert_html_table(tables.get_attribute("outerHTML"))
        if df_table.empty:
            logger.warning(f"{self.product_info.product_id}: Product without bom")
            return

        df_table["quantity"] = df_table["quantity"].str.split(" ", expand=True)[0]
        df_table["quantity"] = df_table["quantity"].astype(float)
        self.product_info.bom = df_table.to_dict(orient="records")

    def download_assets(self) -> None:
        """
        Downloads various assets related to a product and organizes them into a structured
        directory. The assets include an image, a manual in PDF format, and CAD files.
        Returns:
            None: This method does not return any value. It updates the `product_info.assets`
            attribute with metadata about the downloaded assets.
        Raises:
            ValueError: If the specified tab cannot be accessed, the method exits early.
        """

        try:
            self.connection.go_to_tab("//li[@data-tab='drawings']")
        except ValueError:
            return

        prod_id = self.product_info.product_id
        prod_out_path = self.output_path["assets"] / prod_id
        prod_out_path.mkdir(exist_ok=True)

        assets_metadata = {}
        # Image
        assets_metadata["image"] = self.download_files(
            xpath="//img[@class='product-image']",
            atribute="src",
            out_path=prod_out_path / "img.jpg",
        )

        # Pdf
        assets_metadata["manual"] = self.download_files(
            xpath="//a[@id='infoPacket']",
            atribute="href",
            out_path=prod_out_path / "manual.pdf",
        )

        # Cads
        assets_metadata["cad"] = self.download_cad(prod_out_path)

        self.product_info.assets = assets_metadata

    def download_cad(self, prod_out_path: Path) -> dict:
        """
        Downloads CAD files for a product and saves them to the specified output path.
        Args:
            prod_out_path (Path): The directory path where the CAD files will be saved.
        Returns:
            dict: A dictionary containing metadata about the downloaded CAD files, where
                  the keys are the CAD file names and the values are their respective paths.
                  Returns None if the product does not have CAD files.
        Raises:
            ValueError: If the CAD data cannot be properly parsed or processed.
        """

        cad_element = self.connection.find_element(
            "XPATH", "//div[@class='section cadfiles ng-scope']"
        )
        if cad_element is None:
            logger.warning(f"{self.product_info.product_id}: Product without cad")
            return None

        cad_str_list = re.sub(r"\s+", "", cad_element.get_attribute("ng-init"))
        cad_list = ast.literal_eval(cad_str_list.replace("init", ""))
        cad_list = ast.literal_eval(cad_list[3])

        if not cad_list:
            logger.warning(f"{self.product_info.product_id}: Product without cad")
            return None

        assets_metadata = {}
        for cad_info in cad_list:
            url_string = cad_info["url"]
            non_words_char = set(re.findall(r"\W", url_string))
            for c in non_words_char:
                hex_ascii = hex(ord(c)).replace("0x", "%").upper()
                url_string = re.sub(rf"\{c}", hex_ascii, url_string)

            url_download = (
                f"{self.default_url_download}{cad_info['value']}&url={url_string}"
            )
            dst_path = prod_out_path / cad_info["value"]
            self.request.download(url_download, dst_path)

            str_path = dst_path.as_posix().replace("output/", "")
            assets_metadata[cad_info["name"]] = str_path

        return assets_metadata

    def download_files(self, xpath: str, atribute: str, out_path: Path) -> str:
        """
        Downloads a file from a web element identified by the given XPath and saves
            it to the specified output path.
        Args:
            xpath (str): The XPath of the web element containing the file to download.
            atribute (str): The attribute of the web element that contains the file URL.
            out_path (Path): The output path where the downloaded file will be saved.
        Returns:
            str: The relative path of the downloaded file (excluding the "output/" prefix),
                 or None if the file element is not found.
        """

        file = self.connection.find_element("XPATH", xpath)
        if file is None:
            return None

        self.request.download(file.get_attribute(atribute), out_path)
        return out_path.as_posix().replace("output/", "")

    def run_scrapping(self, product_url: str) -> None:
        """
        Executes the web scraping process for a given product URL.
        This method performs the following steps:
        1. Sends a request to the product URL to check its availability.
        2. Loads the product page using the connection driver.
        3. Extracts the product's header information, specifications, and bill of materials (BOM).
        4. Downloads any associated assets for the product.
        5. Closes the connection to the product page.
        6. Saves the scraped product metadata to a JSON file.
        Args:
            product_url (str): The URL of the product to scrape.
        Returns:
            None
        """

        logger.info(f"Scrapping: {product_url}")
        if not self.request.get_response(product_url):
            return

        # Run pipe
        self.driver_page = self.connection.load_page(product_url)
        self.get_head()
        self.get_specs()
        self.get_bom()
        self.download_assets()
        self.connection.close()

        # Saving
        prod_id = self.product_info.product_id
        json_path = self.output_path["metadata"] / f"{prod_id}.json"
        json_write(json_path, self.product_info.__dict__)
        logger.success(f"{prod_id}: Sucefully scrapping")
