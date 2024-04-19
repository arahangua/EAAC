# autogen is not supported for now. As EAAC uses pydantic v2 for now. 
import os,sys
import dotenv
dotenv.load_dotenv('../../../.env')

#autogen
import autogen
from autogen import AssistantAgent, UserProxyAgent

# EAAC
sys.path.append('../../../EAAC_wrapper')
import EAAC

print("autogen is not supported for now. As EAAC uses pydantic v2 for now.")


# llm_config = {"model": "gpt-3.5-turbo", "api_key": os.environ["OPENAI_API_KEY"]}
# assistant = AssistantAgent("assistant", llm_config=llm_config)

# user_proxy = UserProxyAgent(
#     "user_proxy", code_execution_config={"executor": autogen.coding.LocalCommandLineCodeExecutor(work_dir="coding")}
# )

# # wrap agent with EAAC
# EAAC_agent = EAAC.CustomAgentExecutor(user_proxy, identifier='test')


# # Start the chat
# user_proxy.initiate_chat(
#     assistant,
#     message="Plot a chart of NVDA and TESLA stock price change YTD.",
# )