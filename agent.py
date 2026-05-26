from langchain.agents import create_agent
from langchain_mistralai import ChatMistralAI
from tools import web_search, web_scrape
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

# Model for fast, multi-turn tool calling agents (Prevents token/request bottlenecking)
agent_llm = ChatMistralAI(
    model="mistral-small-latest", 
    temperature=0, 
    max_retries=5
)

# Model for high-quality report generation and evaluation
structured_llm = ChatMistralAI(
    model="mistral-large-latest", 
    temperature=0.3, 
    max_retries=5
)

# First Agent - Uses agent_llm
def build_agent():
    return create_agent(
        model=agent_llm,
        tools=[web_search],
    )

# Second Agent - Uses agent_llm
def build_agent2():
    return create_agent(
        model=agent_llm,
        tools=[web_scrape],
    )

# Writer Chain - Uses structured_llm
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured, and insightful reports on the given topic."),
    ("human", """Write a report on the following topic: {topic}
    Research Gathered:
    {research}
    
    Structure the report as:
    - Introduction
    - Key Findings (minimum 2 well-explained points)
    - Conclusion
    - Sources (list all URLs found in the research)
    
    Be detailed, factual, and professional.""")  
])
writer_chain = writer_prompt | structured_llm | StrOutputParser()

# Critic Chain - Uses structured_llm
critic_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an expert critical research analyst and academic reviewer.
Your responsibility is to carefully evaluate research reports, technical documents, and generated content with a highly analytical mindset.

Always organize your response using the following sections:
1. Overall Evaluation and scoring the format like x/10
2. Strengths
3. Weaknesses
4. Missing or Underdeveloped Areas
5. Technical Accuracy Analysis
6. Writing & Structure Review
7. Suggestions for Improvement
8. Final Verdict

Be critical but fair. Do not simply praise the report."""
    ),
    (
        "human",
        """Evaluate the following research report thoroughly.

Research Report:
{report}

Provide a detailed critical analysis with constructive feedback."""
    )
])
critic_chain = critic_prompt | structured_llm | StrOutputParser()