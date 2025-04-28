from typing import Any, Dict, cast, Union, TypeVar
from backend.di_lite.container import ServicesConfig, logger
from backend.di_lite.decorators import EXPLICIT_REGISTRY
from backend.di_lite.exceptions import (
    CircularDependencyError,
    ImplementationNotFoundError,
    InvalidServiceConfigError,
    ServiceNotFoundError,
    ServiceTypeMismatchError,
)
from backend.di_lite.loader import import_from_path
from backend.di_lite.service_keys import ServiceKey
import logging


from enum import Enum
from typing import Any, Dict, cast

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ServiceContainer:
    def __init__(
        self, config: ServicesConfig, type_hints: Dict[ServiceKey, type] | None = None
    ):
        self.config = config.services
        self.instances: Dict[str, Any] = {}
        self.resolving: set[str] = set()
        self.type_hints = type_hints

    def get_service(self, key: Union[str, ServiceKey]) -> Any:
        if isinstance(key, Enum):
            name = key.value
        else:
            name = str(key)
        print(f"[get_service] {name}")

        if name in self.instances:
            return self.instances[name]

        if name in self.resolving:
            raise CircularDependencyError(
                f"Circular dependency detected while resolving '{name}'"
            )

        if name not in self.config:
            raise ServiceNotFoundError(f"Service '{name}' is not defined in config.")

        self.resolving.add(name)
        service_config = self.config[name]
        implementation_name = service_config.use
        full_impl_key = f"{name}.{implementation_name}"
        impl_conf = dict(service_config.implementations[implementation_name])

        class_path = impl_conf.pop("class", None)
        impl_class = EXPLICIT_REGISTRY.get(full_impl_key)
        if impl_class is None:
            if not class_path:
                raise ImplementationNotFoundError(
                    f"No registered or class path found for {full_impl_key}"
                )
            impl_class = import_from_path(class_path)

        # Resolve dependencies
        deps = impl_conf.pop("depends_on", {})
        resolved_deps = {
            dep_name: self.get_service(dep_key) for dep_name, dep_key in deps.items()
        }

        try:
            instance = impl_class(**impl_conf, **resolved_deps)
        except ValidationError as e:
            raise InvalidServiceConfigError(f"Config error in '{full_impl_key}':\n{e}")

        self.instances[name] = instance
        self.resolving.remove(name)
        print(f"[Wired] {name} -> {full_impl_key}")
        return instance

    def get_typed(self, key: ServiceKey) -> T:
        instance = self.get_service(key.value)
        expected_type = self.type_hints.get(key)
        if expected_type and not isinstance(instance, expected_type):
            raise ServiceTypeMismatchError(
                f"{key} is not an instance of {expected_type.__name__}"
            )
        return cast(T, instance)

    def build_all(self):
        for name in self.config:
            logger.info(f"Building service: {name}")
            self.get_service(name)

    # Optional accessors
    def __getattr__(self, name: str) -> Any:
        if name in self.config:
            return self.get_service(name)
        raise AttributeError(f"'ServiceContainer' has no service named '{name}'")
