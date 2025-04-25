from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException

from wrappers import USER_AGENT


class SelConnection:
    def __init__(self):
        """
        Attributes:
            options (webdriver.ChromeOptions): Configuration options for the Chrome WebDriver.
            service (Service): The WebDriver service instance.
            driver (webdriver.Chrome or None): The WebDriver instance, initially set to None.
        """

        self.options = webdriver.ChromeOptions()
        self.options.add_argument(f"--user-agent={USER_AGENT}")
        self.options.add_argument("--headless=new")

        self.service = Service()
        self.driver = None

    def find_element(self, by: object, value: str, elements=False) -> object:
        """
        Locate an element or elements on a web page using Selenium.
        Args:
            by (object): The type of locator to use (e.g., "ID", "XPATH", "CSS_SELECTOR").
            value (str): The value of the locator to search for.
            elements (bool, optional): If True, returns a list of matching elements.
                                       If False, returns a single matching element.
                                       Defaults to False.
        Returns:
            object: The located WebElement(s) if found.
                    Returns None if no element is found or an exception occurs.
        """

        by_object = getattr(By, by)
        try:
            if elements:
                return self.driver.find_elements(by_object, value)
            return self.driver.find_element(by_object, value)
        except NoSuchElementException:
            return None

    def get_element_text(self, by: object, value: str, elements=False) -> str:
        """
        Retrieves the text content of a web element or a list of web elements.
        Args:
            by (object): The strategy to locate the element(s) (e.g., By.ID, By.XPATH).
            value (str): The value used with the locating strategy to find the element(s).
            elements (bool, optional): If True, retrieves text from multiple elements.
                                       Defaults to False.
        Returns:
            list | str | None:
                - A list of strings containing the text of each element if `elements` is True.
                - A single string containing the text of the element if `elements` is False.
                - None if no element is found.
        """

        element = self.find_element(by, value, elements)
        if element is None:
            return None
        if elements:
            return [el.text for el in element]

        return element.text

    def click(self, element_object: object) -> None:
        """
        Simulates a click action on a given web element using JavaScript execution.
        Args:
            element_object (object): The web element to be clicked. This should be
                                     an object compatible with Selenium's WebElement.
        Returns:
            None
        """

        self.driver.execute_script("arguments[0].click();", element_object)

    def load_page(self, url: str, save=False) -> object:
        """
        Loads a webpage using Selenium WebDriver and optionally saves the page source to a file.
        Args:
            url (str): The URL of the webpage to load.
            save (bool, optional): If True, saves the page source to a file
                named "page.html". Defaults to False.
        Returns:
            object: The Selenium WebDriver instance after loading the webpage.
        """

        self.driver = webdriver.Chrome(service=self.service, options=self.options)
        self.driver.get(url)

        if save:
            with open("page.html", "w+", encoding="utf-8") as f:
                f.write(self.driver.page_source)

        return self.driver

    def go_to_tab(self, xpath: str) -> None:
        """
        Navigates to a specific tab in the web application using its XPath.
        Args:
            xpath (str): The XPath of the tab to navigate to.
        Raises:
            ValueError: If the tab with the specified XPath is not found.
        """

        tab = self.find_element("XPATH", xpath)
        if tab is None:
            raise ValueError(f"{xpath} not found")

        # Go to tab
        self.click(tab)

    def close(self):
        """
        Closes the Selenium WebDriver session.
        """

        self.driver.quit()
