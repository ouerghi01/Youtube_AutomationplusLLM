from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
import os

load_dotenv()  
class Agent:
    def __init__(self,temp):
        self.llm=Ollama(model=os.getenv("MODEL_NAME") ,base_url="http://localhost:11434")
        self.template=temp
    def run(self,input_variables):

        QA_CHAIN_PROMPT = PromptTemplate(
        template=self.template,
        input_variables=input_variables,
        )
        
        llm_chain = LLMChain(
            llm=self.llm, 
            prompt=QA_CHAIN_PROMPT, 
            callbacks=None, 
            verbose=True
        )
        return llm_chain