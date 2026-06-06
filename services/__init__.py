"""Website-side service modules."""


def __getattr__(name):
    """Provide temporary legacy access to admin-owned service modules."""
    if name == "pod_storage":
        from importlib import import_module
        import sys

        module = import_module("app.admin.services.pod_storage")
        sys.modules.setdefault("app.services.pod_storage", module)
        return module
    raise AttributeError(name)


__all__ = []
