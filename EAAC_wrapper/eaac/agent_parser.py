import os,sys
from pydantic import BaseModel
import re
import json


# EAAC_conntent declaration
class EAAC_content(BaseModel):
    agent_prog:str
    agent_type: list[str]
    role: list[str]
    task: list[str]
    background: list[str]
    content: dict
    urls: list[str]




# util functions
def get_urls(text):
    # Regex pattern to find URLs
    url_pattern = r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+\~#?&//=]{2,256}\.[a-z]{2,6}\b(?:[-a-zA-Z0-9@:%_\+.~#?&//=]*)'
    # text = "Example text with URLs: https://www.example.com and http://example.org/something.html"
    # Find all matches
    urls = re.findall(url_pattern, text)
    return urls # returns a list

# crewai specific
def make_role_list(agents):
    role_list = []
    for agent in agents:
        role_list.append(agent.role)
    return role_list

# crewai specific
def make_task_list(tasks):
    task_list = []
    for task in tasks:
        task_list.append('description: '+ task.description + '\nexpected_output: '+ task.expected_output)  
    return task_list

# crewai specific
def make_bg_list(agents):
    bg_list = []
    for agent in agents:
        bg_list.append('goal: '+ agent.goal + '\nbackstory: '+ agent.backstory)
    return bg_list
    


def parse_langchain_agent(agent_instance, response):
    agent_config_dict= agent_instance.agent_executor.agent.dict()['runnable']
    
    # convert langchain specific class to string and check for urls
    processed_urls = []
    for k,v in response.items():
        processed_urls = processed_urls + get_urls(str(v))
        response[k] = str(v)

    content = EAAC_content(
        agent_prog="langchain",
        agent_type=[agent_config_dict['last']['_type']],
        role=[agent_config_dict['middle'][0]['messages'][0]['prompt']['template']], #assumes the first message prompt is a system message
        task=[response['input']],
        background=[],
        content=response,
        urls=processed_urls
    )
    return content

def parse_crewai_agent(agent_instance, response):
    # agent_config_dict = agent_instance.agent_executor.model_dump() #//gives circular reference error for pydantic v2
    tasks = agent_instance.agent_executor.tasks
    agents = agent_instance.agent_executor.agents

    # makes 
    role_list = make_role_list(agents) 
    task_list = make_task_list(tasks)
    bg_list = make_bg_list(agents)
    processed_urls = []
    if(response is not dict):
        response_dict = {}
        response_dict['output'] = response

    for k,v in response_dict.items():
        processed_urls = processed_urls + get_urls(str(v))

    ag_type_list = []
    for agent in agents:
        ag_type_list.append('crewai') # functional placeholder. At the moment, agent_type is not explicitly declared for crewai workflow
    
    content = EAAC_content(
        agent_prog="crewai",
        agent_type=ag_type_list,
        role=role_list,
        task=task_list,
        background=bg_list,
        content=response_dict,
        urls=processed_urls
    )
    return content


def parse_autogen_agent(agent_instance, response):
    content = EAAC_content(
        agent_type="autogen",
        role="Conversational Agent",
        task="Chat",
        content=response,
        urls=[]
    )
    return content


def save_to_json(content, output_file_path):

    # Serialize the struct to a JSON string
    json_data = content.model_dump(mode='json')
    # print(json_data)

    # Optionally, you could save this to a file
    with open(f'{output_file_path}', 'w') as f:
        json.dump(json_data, f)
    print(f'json file saved to {output_file_path}')    



