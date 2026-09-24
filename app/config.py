
import os

APP_NAME = os.getenv(
    "APP_NAME",
    "EKS CI/CD Demo Application",
)

APP_VERSION = os.getenv(
    "APP_VERSION",
    "v1.0.0",
)

APP_ENVIRONMENT = os.getenv(
    "APP_ENVIRONMENT",
    "local",
)

