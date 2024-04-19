import os,sys
import dotenv
dotenv.load_dotenv('../../../.env')

#langchain
from langchain_openai import ChatOpenAI
from langchain import hub
from langchain.agents import AgentExecutor
from langchain.agents import create_openai_functions_agent
from langchain_community.tools import DuckDuckGoSearchRun # somehow langchain-community definition of ddgs is not working at the moment v0.0.30
from langchain.agents import Tool

# EAAC
sys.path.append('../../../EAAC_wrapper')
import EAAC


#prompt
prompt = hub.pull("hwchase17/openai-functions-agent")

# llm model
llm = ChatOpenAI(model='gpt-3.5-turbo')

#tools
# tools = [TavilySearchResults()]

search = DuckDuckGoSearchRun()
search_tool = Tool(
    name="duckduckgo_search", #match the name from crewai's Action: duckduckgo_search
    description="A search tool used to query DuckDuckGoSearchRun for search results when trying to find information from the internet.",
    func=search.run
)
tools = [search_tool]

agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, return_intermediate_steps=True)
# agent_executor.invoke({"input": "What is the capital of France?"})


# Wrap the AgentExecutor
EAAC_agent_executor = EAAC.CustomAgentExecutor(agent_executor, identifier='test')

# Use the wrapped executor
response = EAAC_agent_executor.invoke({"input": "What is the capital of France?"})

