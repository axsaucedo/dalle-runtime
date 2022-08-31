import numpy as np
from mlserver.model import MLModel
from mlserver.settings import ModelSettings
from mlserver.types import (
    InferenceRequest,
    InferenceResponse,
)
from mlserver.codecs import NumpyCodec
from mlserver.codecs.string import StringRequestCodec
from dalle_runtime.common import DalleRuntimeSettings, dalle_text_to_image

class DalleRuntime(MLModel):
    """Runtime class for specific DALLE models"""

    def __init__(self, settings: ModelSettings):

        self._extra_settings = DalleRuntimeSettings(**settings.parameters.extra)  # type: ignore

        super().__init__(settings)

    async def predict(self, payload: InferenceRequest) -> InferenceResponse:
        """
        Prediction request
        """
        # For more advanced request decoding see MLServer codecs documentation
        model_input = StringRequestCodec.decode(payload)
        seed = payload.parameters.seed if payload.parameters and payload.parameters.seed else 0 # type: ignore

        encoded_outputs = []
        for instance in model_input:
            model_output = dalle_text_to_image(instance, seed)
            encoded_output = NumpyCodec.encode("predict", model_output)
            encoded_outputs.append(encoded_output)

        return InferenceResponse(
            model_name=self.name,
            model_version=self.version,
            outputs=encoded_outputs,
        )
