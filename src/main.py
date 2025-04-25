from pathlib import Path

import hydra
from omegaconf import DictConfig, OmegaConf
from hydra.utils import instantiate
from loguru import logger
from tqdm import tqdm


def get_processed_ids(output_path: str) -> set:
    """
    Retrieves a set of processed IDs from id in metadata folder.
    Args:
        output_path (str): The path to the directory containing the JSON files.
    Returns:
        set: A set of file stem names (IDs).
        None: If the specified directory does not exist.
    """

    output_path = Path(output_path)
    if output_path.exists():
        return {fpath.stem for fpath in output_path.glob("*.json")}

    return None


@logger.catch
@hydra.main(version_base=None, config_path="../config", config_name="config")
def main(cfg: DictConfig) -> None:
    """
    Main function to execute the web scraping process.
    Args:
        cfg (DictConfig): Configuration object containing all necessary parameters
                          for the scraping process.
    """

    # Start log
    log_verbose = cfg.log_verbose
    if not log_verbose:
        logger.remove()
    logger.add(f"{cfg.log_output}")
    logger.info("start")

    # Getting processed ids
    processed_ids = None
    if cfg.only_new:
        processed_ids = get_processed_ids(cfg.output_paths["metadata"])

    # Converting hydra config types to primirives
    cfg = OmegaConf.to_container(cfg)

    # Getting products ids
    scrapper_obj = instantiate(cfg).sites
    products_list = scrapper_obj.get_products(
        cfg["scraping_limit"], cfg["unique"], processed_ids
    )

    logger.info(f"Products id({len(products_list)}): {products_list}")
    if not products_list:
        logger.warning("No products to scrapping")
        return

    # Run scrapping
    for prod_url in tqdm(
        products_list, desc="Scrapping: ", unit="product id", disable=log_verbose
    ):
        abb_scrapping = instantiate(cfg).sites
        abb_scrapping.run_scrapping(prod_url)


if __name__ == "__main__":
    main()
