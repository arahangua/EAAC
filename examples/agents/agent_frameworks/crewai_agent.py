import os,sys
import dotenv
dotenv.load_dotenv('../../../.env')

# define agents 
from crewai import Agent
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import Tool
os.environ["OPENAI_MODEL_NAME"]="gpt-3.5-turbo"

# EAAC
import eaac


search = DuckDuckGoSearchRun()
search_tool = Tool(
    name="duckduckgo_search", #match the name from crewai's Action: duckduckgo_search
    description="A search tool used to query DuckDuckGoSearchRun for search results when trying to find information from the internet.",
    func=search.run
)

# Creating a senior researcher agent with memory and verbose mode
researcher = Agent(
  role='Senior Researcher',
  goal='Uncover groundbreaking technologies in {topic}',
  verbose=True,
  memory=True,
  backstory=(
    "Driven by curiosity, you're at the forefront of"
    "innovation, eager to explore and share knowledge that could change"
    "the world."
  ),
  tools=[search_tool],
  allow_delegation=True
)

# Creating a writer agent with custom tools and delegation capability
writer = Agent(
  role='Writer',
  goal='Narrate compelling tech stories about {topic}',
  verbose=True,
  memory=True,
  backstory=(
    "With a flair for simplifying complex topics, you craft"
    "engaging narratives that captivate and educate, bringing new"
    "discoveries to light in an accessible manner."
  ),
  tools=[search_tool],
  allow_delegation=False
)


# define task
from crewai import Task

# Research task
research_task = Task(
  description=(
    "Identify the next big trend in {topic}."
    "Focus on identifying pros and cons and the overall narrative."
    "Your final report should clearly articulate the key points,"
    "its market opportunities, and potential risks."
  ),
  expected_output='A comprehensive 3 paragraphs long report on the latest AI trends.',
  tools=[search_tool],
  agent=researcher,
)

# Writing task with language model configuration
write_task = Task(
  description=(
    "Compose an insightful article on {topic}."
    "Focus on the latest trends and how it's impacting the industry."
    "This article should be easy to understand, engaging, and positive."
  ),
  expected_output='A 4 paragraph article on {topic} advancements formatted as markdown.',
  tools=[search_tool],
  agent=writer,
  async_execution=False,
  output_file='new-blog-post.md'  # Example of output customization
)

# form the crew

from crewai import Crew, Process

# Forming the tech-focused crew with some enhanced configurations
crew = Crew(
  agents=[researcher, writer],
  tasks=[research_task, write_task],
  process=Process.sequential,  # Optional: Sequential task execution is default
  memory=True,
  cache=True,
  max_rpm=10,
  share_crew=True
)

# wrap the crew class
EAAC_crew = eaac.CustomAgentExecutor(crew, identifier='crewai_test')


# Starting the task execution process with enhanced feedback
response = EAAC_crew.kickoff(inputs={'topic': 'a short overview on AI in healthcare'})
