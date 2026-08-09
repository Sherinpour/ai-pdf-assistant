# from openai import OpenAI

# from app.core.config import OPENAI_API_KEY


# client = OpenAI(api_key=OPENAI_API_KEY)


# def generate_answer(
#     question: str,
#     context: str,
# ) -> str:

#     prompt = f"""
# You are an assistant that answers questions based only on the provided context.

# Context:
# {context}

# Question:
# {question}

# Instructions:
# - Answer only based on the context.
# - If the answer cannot be found in the context, say that you don't have enough information.
# - Do not make up information.
# - Answer in the same language as the question.
# """

#     response = client.responses.create(
#         model="gpt-5-mini",
#         input=prompt,
#     )

#     return response.output_text