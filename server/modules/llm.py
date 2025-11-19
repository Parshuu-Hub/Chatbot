from langchain_core.prompts import PromptTemplate
# from langchain_community.chains import PebbloRetrievalQA  # Use standard LangChain chain
# from langchain_core.retrievers import RetrievalQA

from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Prompt template
prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
    You are **Bot**, an AI-powered assistant trained to help users understand documents and doc-related questions.

    Your job is to provide clear, accurate, and helpful responses based **only on the provided context**.

    ---

    🔍 **Context**:
    {context}

    🙋‍♂️ **User Question**:
    {question}

    ---

    💬 **Answer**:
    - Respond in a calm, factual, and respectful tone.
    - Use simple explanations when needed.
    - If the context does not contain the answer, say: "I'm sorry, but I couldn't find relevant information in the provided documents."
    - Do NOT make up facts.
    """
)

def get_llm_chain(retriever):
    # Initialize LLM
    llm = ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name='llama-3.3-70b-versatile'
    )

    

    # Create standard RetrievalQA chain
    # return PebbloRetrievalQA.from_chain_type(
    #     llm=llm,
    #     chain_type="stuff",
    #     retriever=retriever,
    #     app_name="MyRagBot",
    #     description="A medical PDF chatbot.",
    #     owner="praveenmishra",
    #     chain_type_kwargs={"prompt": prompt},
    #     return_source_documents=True
    # )
    def rag_pipeline(question):
        docs = retriever._get_relevant_documents(question)
        context = "\n".join([doc.page_content for doc in docs])
        prompt_text = prompt.format(context=context, question=question)
        # If using LangChain's `invoke` API, use .invoke. Otherwise, just call it as a function.
        result = llm.invoke(prompt_text) if hasattr(llm, "invoke") else llm(prompt_text)
        return {
            "result": result,
            "source_documents": docs
        }
    return rag_pipeline
