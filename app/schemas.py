from pydantic import BaseModel, Field, field_validator
from typing import Optional
import numpy as np

class ClaimInput(BaseModel):
    claim_id: int
    marca_vehiculo: str = Field(default="nan")
    antiguedad_vehiculo: int = Field(default=1)
    tipo_poliza: int = Field(default=1)
    taller: int = Field(default=1)
    partes_a_reparar: int = Field(default=3)
    partes_a_reemplazar: int = Field(default=1)

    @field_validator('*', mode='before')
    def handle_nulls(cls, v):
        return "nan" if v is None or (isinstance(v, float) and np.isnan(v)) else v

class ModelFeatures(BaseModel):
    log_total_piezas: float = Field(default=1.4545)
    marca_vehiculo_encoded: int = Field(default=0)
    valor_vehiculo: int = Field(default=3560)
    valor_por_pieza: int = Field(default=150)
    antiguedad_vehiculo: int = Field(default=1)

    @field_validator('*', mode='before')
    def validate_finite(cls, v, info):
        if v is None or not np.isfinite(v):
            return cls.model_fields[info.field_name].default
        return v
    
class PredictionOutput(BaseModel):
    claim_id: int
    prediction: float