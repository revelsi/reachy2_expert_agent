from langchain.chains import RetrievalQA
from langchain.llms import HuggingFacePipeline
import transformers
import torch


def build_llm():
    """
    Build the open-source language model for code generation.
    Choose a model from Hugging Face that is suitable for generating code.
    """
    model_id = "huggingface/CodeGen-350M-multi"  # this is one open-source option
    device = 0 if torch.cuda.is_available() else -1

    tokenizer = transformers.AutoTokenizer.from_pretrained(model_id)
    model = transformers.AutoModelForCausalLM.from_pretrained(model_id)
    
    # Create a Hugging Face pipeline for text generation.
    pipe = transformers.pipeline(
        "text-generation", model=model, tokenizer=tokenizer, device=device
    )
    # Wrap the pipeline in a LangChain LLM interface.
    llm = HuggingFacePipeline(pipeline=pipe)
    return llm


def build_chatbot(vectorstore):
    """
    Create the RetrievalQA chain that uses the vector store (RAG pipeline) and the LLM.
    The chain will first retrieve the most relevant documents before passing the enhanced prompt to the LLM.
    """
    llm = build_llm()
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",  # you can experiment with different chain types (map_reduce, refine, etc.)
        retriever=vectorstore.as_retriever()
    )
    return qa_chain 