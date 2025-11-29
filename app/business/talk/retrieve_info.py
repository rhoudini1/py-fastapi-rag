from app.domain.dto.response.retrieve_info import RetrieveInfoResponse
from app.infra.gateway import GeminiGateway


class RetrieveInfoUseCase:
    def __init__(self, gemini_gateway: GeminiGateway):
        self.gemini_gateway = gemini_gateway

    async def execute(self, message: str):
        # Use the gateway's async generator method and wrap the result
        response_text = await self.gemini_gateway.generate_response(message)
        return RetrieveInfoResponse(message=message, response=response_text)

