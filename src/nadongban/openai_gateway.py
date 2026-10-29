from openai import OpenAI


class OpenAIGateway:
    """Small adapter around OpenAI so the application remains testable."""

    def __init__(self, chat_model: str, embedding_model: str) -> None:
        self.client = OpenAI()
        self.chat_model = chat_model
        self.embedding_model = embedding_model

    def embed(self, text: str) -> list[float]:
        response = self.client.embeddings.create(
            model=self.embedding_model,
            input=text,
            encoding_format="float",
        )
        return response.data[0].embedding

    def answer(self, question: str, memories: list[str]) -> str:
        memory_block = "\n".join(f"- {memory}" for memory in memories)
        if not memory_block:
            memory_block = "- 검색된 과거 기억 없음"

        response = self.client.responses.create(
            model=self.chat_model,
            instructions=(
                "당신은 사용자의 장기기억을 보조하는 한국어 챗봇 '나동반'입니다. "
                "제공된 기억에 근거해 답하되, 기억에 없는 사실은 지어내지 마세요. "
                "날짜가 포함된 경우 현재 질문과의 시간 관계를 명확히 설명하세요."
            ),
            input=(
                f"관련 과거 기억:\n{memory_block}\n\n"
                f"현재 사용자 질문:\n{question}"
            ),
        )
        return response.output_text.strip()
