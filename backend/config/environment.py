from enum import Enum

class Environment(str, Enum):
    """
    Enum representing the deployment environments.
    """
    LOCAL = "local"
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"
