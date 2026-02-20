from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from core.models import PayloadTemplate, PayloadValidationError


# ------------------------------
# Types
# ------------------------------

GeneratorFunction = Callable[..., List[PayloadTemplate]]


# ------------------------------
# Exceptions
# ------------------------------

class RegistryError(Exception):
    """Raised when registry operations fail."""
    pass


# ------------------------------
# Module Spec
# ------------------------------

@dataclass(frozen=True)
class ModuleSpec:
    """
    Metadata about a module generator.
    """
    name: str
    generator: GeneratorFunction
    requires_db: bool = False
    requires_os: bool = False


# ------------------------------
# Registry
# ------------------------------

class ModuleRegistry:
    """
    Central registry for payload generator modules.
    """

    def __init__(self) -> None:
        self._registry: Dict[str, ModuleSpec] = {}

    # ---------- registration ----------

    def register(
        self,
        module_name: str,
        func: GeneratorFunction,
        *,
        requires_db: bool = False,
        requires_os: bool = False,
    ) -> None:

        if module_name in self._registry:
            raise RegistryError(f"Module '{module_name}' is already registered.")

        self._registry[module_name] = ModuleSpec(
            name=module_name,
            generator=func,
            requires_db=requires_db,
            requires_os=requires_os,
        )

    def register_module(
        self,
        module_name: str,
        *,
        requires_db: bool = False,
        requires_os: bool = False,
    ):
        def decorator(func: GeneratorFunction) -> GeneratorFunction:
            self.register(
                module_name,
                func,
                requires_db=requires_db,
                requires_os=requires_os,
            )
            return func
        return decorator

    # ---------- lookup ----------

    def list_modules(self) -> List[str]:
        return sorted(self._registry.keys())

    def get_spec(self, module_name: str) -> ModuleSpec:
        if module_name not in self._registry:
            raise RegistryError(
                f"Module '{module_name}' is not registered. "
                f"Available: {self.list_modules()}"
            )
        return self._registry[module_name]

    # ---------- validation ----------

    def validate_selectors(
        self,
        module_name: str,
        *,
        db_type: Optional[str] = None,
        os_type: Optional[str] = None,
        context: Optional[str] = None,
    ) -> None:

        spec = self.get_spec(module_name)

        # SQLi requires db_type
        if spec.requires_db and not db_type:
            raise RegistryError(
                f"Module '{module_name}' requires 'db_type' selector."
            )

        # CMD requires os_type
        if spec.requires_os and not os_type:
            raise RegistryError(
                f"Module '{module_name}' requires 'os_type' selector."
            )

        # XSS requires context (test requirement)
        if module_name == "xss" and not context:
            raise RegistryError(
                "Module 'xss' requires 'context' selector."
            )

    # ---------- execution ----------

    def generate(
        self,
        module_name: str,
        *,
        db_type: Optional[str] = None,
        os_type: Optional[str] = None,
        context: Optional[str] = None,
        **kwargs,
    ) -> List[PayloadTemplate]:

        self.validate_selectors(
            module_name,
            db_type=db_type,
            os_type=os_type,
            context=context,
        )

        spec = self.get_spec(module_name)

        if spec.requires_db:
            items = spec.generator(db_type=db_type, **kwargs)
        elif spec.requires_os:
            items = spec.generator(os_type=os_type, **kwargs)
        else:
            items = spec.generator(context=context, **kwargs)

        if not isinstance(items, list):
            raise RegistryError(
                f"Module '{module_name}' must return List[PayloadTemplate]."
            )

        for i, item in enumerate(items):
            if not isinstance(item, PayloadTemplate):
                raise RegistryError(
                    f"Item {i} from module '{module_name}' "
                    f"is not PayloadTemplate."
                )

            try:
                item._validate()
            except PayloadValidationError as e:
                raise PayloadValidationError(
                    f"Invalid payload from module '{module_name}' at index {i}: {e}"
                ) from e

        return items


# ------------------------------
# Global registry instance
# ------------------------------

registry = ModuleRegistry()


# ------------------------------
# Initialize (imports trigger decorators)
# ------------------------------

def initialize_registry() -> None:
    from modules import xss  # noqa: F401
    from modules import sqli  # noqa: F401
    from modules import cmd_injection  # noqa: F401


def get_registry() -> ModuleRegistry:
    initialize_registry()
    return registry
