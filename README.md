# rune_forge

`rune_forge` is a lightweight, structured dependency injection (DI) framework with a magical, compositional twist. Inspired by fantasy lore, it lets you define services as Runes, organize them inside a Grimoire, and summon them when needed. The goal: high traceability, explicit binding, and powerful composability.

## Core Concepts

- **Runeforge**: The overarching framework, a forge for your services.
- **Grimoire**: A container that holds your inscribed Runes (services).
- **Rune**: A single service or dependency.
- **GrimoireConfig**: Defines the set of Runes (service configurations) available.
- **Inscribe**: The act of registering a class as a Rune inside the forge.

Services are composed by layering simple parts together, with full traceability and minimal magic at runtime.

## Installation

```bash
# Recommended to install within a virtual environment
pip install rune_forge

```

_(Note: You'll need to package this properly for `pip install` to work, or adjust if installing locally.)_

## Usage

### 1. Define your Service Interfaces

```python
from abc import ABC

class Service1(ABC):
    def do_something(self) -> str:
        pass

class Service2(ABC):
    def fetch_data(self) -> str:
        pass

class Service3(ABC):
    def another_func(self) -> str:
        pass
```

### 2. Implement and Inscribe your Services

```python
from pydantic import BaseModel
from rune_forge import inscribe

@inscribe("service2.default")
class Service2Default(BaseModel, Service2):
    paramX: str

    def fetch_data(self) -> str:
        return f"Fetched {self.paramX}"

@inscribe("service3.default")
class Service3Default(BaseModel, Service3):
    paramY: str

    def another_func(self) -> str:
        return f"Func {self.paramY}"

@inscribe("service1.concrete1")
class Service1Concrete1(BaseModel, Service1):
    param1: str
    service2: Service2
    service3: Service3

    class Config:
        arbitrary_types_allowed = True

    def do_something(self) -> str:
        return f"{self.param1} + {self.service2.fetch_data()} + {self.service3.another_func()}"
```

Each service implementation can depend on others via constructor injection.

### 3. Define Your GrimoireConfig

```python
from rune_forge import GrimoireConfig

class MyGrimoireConfig(GrimoireConfig):
    _config_files = ["configs/runes.yaml"]
```

Example `configs/runes.yaml`:

```yaml
service1:
  use: concrete1
  implementations:
    concrete1:
      param1: "hello"
      depends_on:
        service2: service2 # Refers to the 'service2' Rune key
        service3: service3 # Refers to the 'service3' Rune key

service2:
  use: default
  implementations:
    default:
      paramX: "world"

service3:
  use: default
  implementations:
    default:
      paramY: "!"
```

Each Rune specifies:

- The implementation to use (`use:`).
- Constructor parameters.
- Dependencies via `depends_on`.

### 4. Build and Summon Services from the Grimoire

```python
from rune_forge import Grimoire

# Create your Grimoire
grimoire = Grimoire(MyGrimoireConfig())

# Summon a service by key
service1 = grimoire.get_service("service1")
print(service1.do_something())

# Or use attribute access (if key is a valid Python identifier)
print(grimoire.service1.do_something())
```

- Runes are lazily built on demand.
- Dependencies are auto-resolved recursively.
- You can call `grimoire.build_all()` to build all Runes eagerly if needed.

## Advanced Features

- **Circular Dependency Detection**: Raises an error if a dependency loop is detected during summoning.
- **Explicit Registry**: Services can be manually registered with `@inscribe` or dynamically resolved by class path.
- **Typed Access**: Using `get_typed()` ensures your summoned instance matches the expected type.

```python
from rune_forge import RuneKey # Assuming RuneKey enum/class exists for type hints

service1 = grimoire.get_typed(RuneKey.service1) # Example if using an Enum/Constant for keys
# Or using the abstract base class
service1_typed = grimoire.get_typed(Service1)
```

## Philosophy

In Runeforge, each service is a Rune, carefully inscribed into a Grimoire. Summon only the Runes you need. Compose mighty applications from small, traceable parts.

No hidden runtime magic. No dynamic chaos. Just crafted composability.
