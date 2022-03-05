import utils.config
import utils.log


if __name__ == '__main__':
    config = utils.config.Config("config.yaml")
    config.read()
    logger = utils.log.init_logging(config.log_level)
    logger.warning(config)
