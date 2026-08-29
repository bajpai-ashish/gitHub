import logging
from dataclasses import dataclass
from pathlib import Path

import yaml


# ============================================================
# CONNECTION RESULT
# ============================================================

@dataclass
class ConnectionResult:

    is_connected: bool
    connection_type: str
    message: str
    connection: object = None
    error: str = None


# ============================================================
# CONNECTION MANAGER
# ============================================================

class ConnectionManager:

    def __init__(self, config_file=None):

        # ----------------------------------------------------
        # Default configuration location
        # ----------------------------------------------------

        if config_file is None:

            config_file = (
                Path(__file__).resolve()
                .parents[2]
                / "Config"
                / "platform_config.yaml"
            )

        self.config_file = Path(config_file)

        # ----------------------------------------------------
        # Load configuration
        # ----------------------------------------------------

        self.config = self._load_config()

        # ----------------------------------------------------
        # Logger
        # ----------------------------------------------------

        self.logger = self._create_logger()

    # ========================================================
    # LOAD CONFIGURATION
    # ========================================================

    def _load_config(self):

        try:

            with open(
                self.config_file,
                "r",
                encoding="utf-8"
            ) as file:

                return yaml.safe_load(file)

        except Exception as e:

            raise RuntimeError(
                f"Unable to load configuration file: "
                f"{self.config_file}\n"
                f"Reason: {str(e)}"
            )

    # ========================================================
    # LOGGER
    # ========================================================

    def _create_logger(self):

        logger = logging.getLogger(
            "InventoryDataPlatform"
        )

        if not logger.handlers:

            logger.setLevel(logging.INFO)

            # ------------------------------------------------
            # Log directory
            # ------------------------------------------------

            log_directory = (
                Path(__file__).resolve()
                .parents[2]
                / "Logs"
            )

            log_directory.mkdir(
                parents=True,
                exist_ok=True
            )

            log_file = (
                log_directory
                / "connection.log"
            )

            handler = logging.FileHandler(
                log_file,
                encoding="utf-8"
            )

            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)s | %(message)s"
            )

            handler.setFormatter(formatter)

            logger.addHandler(handler)

        return logger

    # ========================================================
    # MINIO CONNECTION
    # ========================================================

    def connect_minio(self):

        try:

            from minio import Minio

            storage = self.config["storage"]

            endpoint = storage["endpoint"]

            # Remove protocol because Minio expects:
            # localhost:9000
            endpoint = (
                endpoint
                .replace("http://", "")
                .replace("https://", "")
            )

            access_key = storage["access_key"]
            secret_key = storage["secret_key"]
            secure = storage["secure"]

            client = Minio(
                endpoint,
                access_key=access_key,
                secret_key=secret_key,
                secure=secure
            )

            # ------------------------------------------------
            # Test connection
            # ------------------------------------------------

            list(client.list_buckets())

            message = (
                f"Successfully connected to MinIO "
                f"at {endpoint}"
            )

            self.logger.info(
                f"MINIO | {message}"
            )

            return ConnectionResult(
                is_connected=True,
                connection_type="minio",
                message=message,
                connection=client,
                error=None
            )

        except Exception as e:

            message = (
                "Unable to connect to MinIO."
            )

            self.logger.error(
                f"MINIO | {message} | "
                f"Reason: {str(e)}"
            )

            return ConnectionResult(
                is_connected=False,
                connection_type="minio",
                message=message,
                connection=None,
                error=str(e)
            )

    # ========================================================
    # SPARK CONNECTION
    # ========================================================

    def connect_spark(self):

        try:

            from pyspark.sql import SparkSession

            spark_config = self.config["spark"]
            storage = self.config["storage"]

            application = self.config["application"]

            app_name = application["name"]

            # ------------------------------------------------
            # Driver configuration
            # ------------------------------------------------

            driver_memory = (
                spark_config["driver"]["memory"]
            )

            driver_cores = (
                spark_config["driver"]["cores"]
            )

            # ------------------------------------------------
            # Executor configuration
            # ------------------------------------------------

            executor_memory = (
                spark_config["executor"]["memory"]
            )

            executor_cores = (
                spark_config["executor"]["cores"]
            )

            executor_instances = (
                spark_config["executor"]["instances"]
            )

            shuffle_partitions = (
                spark_config["sql"]["shuffle_partitions"]
            )

            # ------------------------------------------------
            # MinIO
            # ------------------------------------------------

            endpoint = storage["endpoint"]

            access_key = storage["access_key"]
            secret_key = storage["secret_key"]

            secure = storage["secure"]

            # ------------------------------------------------
            # Spark Builder
            # ------------------------------------------------

            builder = (
                SparkSession.builder

                .appName(app_name)

                # Driver
                .config(
                    "spark.driver.memory",
                    driver_memory
                )

                .config(
                    "spark.driver.cores",
                    driver_cores
                )

                # Executor
                .config(
                    "spark.executor.memory",
                    executor_memory
                )

                .config(
                    "spark.executor.cores",
                    executor_cores
                )

                .config(
                    "spark.executor.instances",
                    executor_instances
                )

                # SQL
                .config(
                    "spark.sql.shuffle.partitions",
                    shuffle_partitions
                )

                # ------------------------------------------------
                # MinIO / S3A
                # ------------------------------------------------

                .config(
                    "spark.hadoop.fs.s3a.endpoint",
                    endpoint
                )

                .config(
                    "spark.hadoop.fs.s3a.access.key",
                    access_key
                )

                .config(
                    "spark.hadoop.fs.s3a.secret.key",
                    secret_key
                )

                .config(
                    "spark.hadoop.fs.s3a.path.style.access",
                    "true"
                )

                .config(
                    "spark.hadoop.fs.s3a.connection.ssl.enabled",
                    str(secure).lower()
                )
            )

            # ====================================================
            # ICEBERG
            # ====================================================

            iceberg = self.config.get(
                "iceberg",
                {}
            )

            if iceberg.get("enabled", False):

                catalog = iceberg["catalog"]

                catalog_name = catalog["name"]
                catalog_type = catalog["type"]

                warehouse = iceberg["warehouse"]

                if catalog_type == "hadoop":

                    builder = (
                        builder

                        .config(
                            f"spark.sql.catalog.{catalog_name}",
                            "org.apache.iceberg.spark.SparkCatalog"
                        )

                        .config(
                            f"spark.sql.catalog.{catalog_name}.type",
                            "hadoop"
                        )

                        .config(
                            f"spark.sql.catalog.{catalog_name}.warehouse",
                            warehouse
                        )
                    )

            # ====================================================
            # CREATE SPARK SESSION
            # ====================================================

            spark = builder.getOrCreate()

            # ------------------------------------------------
            # Set log level
            # ------------------------------------------------

            log_level = spark_config.get(
                "log_level",
                "WARN"
            )

            spark.sparkContext.setLogLevel(
                log_level
            )

            # ------------------------------------------------
            # Test Spark
            # ------------------------------------------------

            spark.range(1).count()

            message = (
                f"Spark connection established. "
                f"Application: {app_name}"
            )

            self.logger.info(
                f"SPARK | {message}"
            )

            return ConnectionResult(
                is_connected=True,
                connection_type="spark",
                message=message,
                connection=spark,
                error=None
            )

        except Exception as e:

            message = (
                "Unable to start Spark session."
            )

            self.logger.error(
                f"SPARK | {message} | "
                f"Reason: {str(e)}"
            )

            return ConnectionResult(
                is_connected=False,
                connection_type="spark",
                message=message,
                connection=None,
                error=str(e)
            )

    # ========================================================
    # DISCONNECT SPARK
    # ========================================================

    def disconnect_spark(self, spark):

        try:

            spark.stop()

            message = (
                "Spark session stopped successfully."
            )

            self.logger.info(
                f"SPARK | {message}"
            )

            return ConnectionResult(
                is_connected=False,
                connection_type="spark",
                message=message,
                connection=None,
                error=None
            )

        except Exception as e:

            message = (
                "Unable to stop Spark session."
            )

            self.logger.error(
                f"SPARK | {message} | "
                f"Reason: {str(e)}"
            )

            return ConnectionResult(
                is_connected=True,
                connection_type="spark",
                message=message,
                connection=spark,
                error=str(e)
            )