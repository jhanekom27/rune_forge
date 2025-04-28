class ServiceNotFoundError(Exception):
    pass


class CircularDependencyError(Exception):
    pass


class ImplementationNotFoundError(Exception):
    pass


class InvalidServiceConfigError(Exception):
    pass


class ServiceTypeMismatchError(Exception):
    pass
