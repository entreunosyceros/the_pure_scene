"""Rutas de datos cuando The Pure Scene está instalada en el sistema."""
import os
from pathlib import Path


def data_dir(base_dir: str) -> str:
    """Directorio escribible: TPS_DATA_DIR o base_dir del proyecto."""
    override = os.environ.get("TPS_DATA_DIR")
    if override:
        Path(override, "temp").mkdir(parents=True, exist_ok=True)
        Path(override, "descargas").mkdir(parents=True, exist_ok=True)
        return override
    return base_dir
