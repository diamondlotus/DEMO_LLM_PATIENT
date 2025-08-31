from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

# 1. Parser Agent - Extract structured entities from patient notes
def parser_agent(llm):
    prompt = ChatPromptTemplate.from_template(
        "Extract diagnoses, medications, and lab values from this patient note:\n{note}"
    )
    return lambda note: llm.invoke(prompt.format_messages(note=note))

# 2. Evaluator Agent - Validate terminology
def evaluator_agent(llm):
    prompt = ChatPromptTemplate.from_template(
        "Validate this structured data against ICD-10/SNOMED. "
        "Return JSON with validity flags:\n{data}"
    )
    return lambda data: llm.invoke(prompt.format_messages(data=data))

# 3. Synthesizer Agent - Generate patient-friendly summary
def synthesizer_agent(llm):
    prompt = ChatPromptTemplate.from_template(
        "Generate a simple patient-friendly health report based on:\n{validated_data}"
    )
    return lambda validated_data: llm.invoke(prompt.format_messages(validated_data=validated_data))

