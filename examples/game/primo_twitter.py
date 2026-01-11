from game_sdk.game.agent import Agent, WorkerConfig
from game_sdk.game.worker import Worker
from game_sdk.game.custom_types import Function, Argument, FunctionResult, FunctionResultStatus
from game_sdk.hosted_game.agent import FunctionArgument, FunctionConfig, ContentLLMTemplate
from typing import Optional, Dict, List, Tuple
import os
import requests
import time
import logging
from twitter_plugin_gamesdk.twitter_plugin import TwitterPlugin
from twitter_plugin_gamesdk.game_twitter_plugin import GameTwitterPlugin


game_api_key = os.environ.get("GAME_API_KEY")
options = {
    "id": "test_game_twitter_plugin",
    "name": "Test GAME Twitter Plugin",
    "description": "An example GAME Twitter Plugin for testing.",
    "credentials": {
        "gameTwitterAccessToken": os.environ.get("GAME_TWITTER_ACCESS_TOKEN")
    },
}


game_twitter_plugin = GameTwitterPlugin(options)

def get_state_fn(function_result: FunctionResult, current_state: dict) -> dict:
    """
    This function will get called at every step of the agent's execution to form the agent's state.
    It will take as input the function result from the previous step.
    In this case, we don't track state changes so states are are static - hence hardcoding as empty dict.
    """
    return {}

# State dictionary to track agent and worker states
agent_state = {
    "last_tweet": None,
    "last_read_tweets": [],
    "engagement_metrics": {},  # Store likes, retweets, etc.
    "recent_sentiments": []  # Track sentiment of latest tweets
}

worker_states = {
    "read_tweet": {"last_read_tweet_id": None,"list_of_tweets": []},
    "create_tweet": {"last_posted_tweet": None}
}

def init_worker_state(worker_id: str) -> dict:
    """Initializes state for a given worker."""
    logging.info(f"Initializing state for worker: {worker_id}")
    print(f"Initializing state for worker: {worker_id}")
    if worker_id == "read_tweet":
        return {"last_read_tweet_id": None}
    elif worker_id == "create_tweet":
        return {"last_posted_tweet": None}
    return {}

def get_worker_state_fn(worker_id: str, function_result: FunctionResult, current_state: dict) -> dict:
    """Updates the worker state based on function execution results."""
    logging.info(f"Updating worker state for {worker_id} with result: {function_result}")
    print(f"Worker {worker_id} - Previous state: {current_state}")
    if function_result and function_result.action_status == FunctionResultStatus.DONE:
        if worker_id == "read_tweet" and function_result.info:
            worker_states[worker_id]["last_read_tweet_id"] = function_result.info.get("last_read_tweet_id")
        elif worker_id == "create_tweet" and function_result.info:
            worker_states[worker_id]["last_posted_tweet"] = function_result.info.get("last_posted_tweet")
    logging.info(f"New worker state: {worker_states[worker_id]}")
    print(f"Worker {worker_id} - Updated state: {worker_states[worker_id]}")
    return worker_states.get(worker_id, init_worker_state(worker_id))

def get_create_tweet_worker_state_fn(function_result: FunctionResult, current_state: dict) -> dict:
    """Updates the worker state based on function execution results."""
    worker_id = "create_tweet"
    logging.info(f"Updating worker state for {worker_id} with result: {function_result}")
    print(f"Worker {worker_id} - Previous state: {current_state}")
    if function_result and function_result.action_status == FunctionResultStatus.DONE:
        if worker_id == "read_tweet" and function_result.info:
            worker_states[worker_id]["last_read_tweet_id"] = function_result.info.get("last_read_tweet_id")
        elif worker_id == "create_tweet" and function_result.info:
            worker_states[worker_id]["last_posted_tweet"] = function_result.info.get("last_posted_tweet")
    logging.info(f"New worker state: {worker_states[worker_id]}")
    print(f"Worker {worker_id} - Updated state: {worker_states[worker_id]}")
    return worker_states.get(worker_id, init_worker_state(worker_id))

def get_read_tweet_worker_state_fn(function_result: FunctionResult, current_state: dict) -> dict:
    """Updates the worker state based on function execution results."""
    worker_id = "read_tweet"
    logging.info(f"Updating worker state for {worker_id} with result: {function_result}")
    print(f"Worker {worker_id} - Previous state: {current_state}")
    if function_result and function_result.action_status == FunctionResultStatus.DONE:
        if worker_id == "read_tweet" and function_result.info:
            worker_states[worker_id]["last_read_tweet_id"] = function_result.info.get("last_read_tweet_id")
            worker_states[worker_id]["list_of_tweets"] = function_result.info.get("list_of_tweets")
        elif worker_id == "create_tweet" and function_result.info:
            worker_states[worker_id]["last_posted_tweet"] = function_result.info.get("last_posted_tweet")
    logging.info(f"New worker state: {worker_states[worker_id]}")
    print(f"Worker {worker_id} - Updated state: {worker_states[worker_id]}")
    return worker_states.get(worker_id, init_worker_state(worker_id))

def get_agent_state_fn(function_result: FunctionResult, current_state: dict) -> dict:
    """Updates the agent state after each action."""
    logging.info(f"Updating agent state with result: {function_result}")
    print(f"Agent - Previous state: {current_state}")
    if function_result and function_result.action_status == FunctionResultStatus.DONE:
        if function_result.info:
            agent_state["last_read_tweets"] = function_result.info.get("list_of_tweets")
            agent_state["last_tweet"] = function_result.info.get("last_tweet")
            agent_state["engagement_metrics"] = function_result.info.get("engagement_metrics")
            agent_state["sentiment_analysis"] = function_result.info.get("sentiment_analysis")
    logging.info(f"New agent state: {agent_state}")
    print(f"Agent - Updated state: {agent_state}")
    return agent_state

def write_real_estate_tweet(tweet_content):
    logging.info(f"Writing tweet: {tweet_content}")
    print(f"Writing tweet: {tweet_content}")
    post_tweet_fn = game_twitter_plugin.get_function('post_tweet')
    result = post_tweet_fn(tweet_content)
    return FunctionResultStatus.DONE, f"Posted tweet: {tweet_content}",{"last_posted_tweet": tweet_content}
  
write_tweet = Function(
        fn_name="write_tweet", 
        fn_description="Write opinion on US, San Diego CA real estate market and crypto market", 
        args=[
            Argument(name="tweet_content", type="string", description="Tweet content to post based on real estate market and crypto market")
        ],
        executable=write_real_estate_tweet
    )

def read_real_estate_tweet(keywords):
    # logging.info(f"Reading tweets with keywords: {keywords}")
    print(f"Reading tweets with keywords: {keywords}")
    get_user_fn = game_twitter_plugin.get_function('search_tweets')
    search_results = get_user_fn(keywords)
    tweets =  search_results.get("data", [])  
    tweet_content = [tweet.get("text", "") for tweet in tweets]
    last_tweet_id = tweets[-1].get("id", None) if tweets else None
    engagement_metrics = {"likes": 10, "retweets": 5}  # Example placeholder
    sentiment_analysis = "Positive"  # Example placeholder
    return FunctionResultStatus.DONE, f"Fetched {tweet_content} with {keywords}",{
            "list_of_tweets": tweet_content,
            "last_read_tweet_id": last_tweet_id,
            "engagement_metrics": engagement_metrics,
            "sentiment_analysis": sentiment_analysis
        }
    

read_from_leaders =  Function(
    fn_name="read_from_leaders", 
        fn_description="Search 5 tweets from industry leaders in real estate market and crypto market to form an opinion and generate a tweet. If nothing is found, move to forming your opinion.", 
        args=[
            Argument(name="keywords", type="string", description="One string Keyword to search for, dont use "and" ")
        ],
    executable=read_real_estate_tweet
)

# Create the specialized workers
create_tweet = WorkerConfig(
    id="create_tweet",
    worker_description="A worker specialized in writing tweets related to real estate market and crypto market. Dont use hashtags. Do not post the same thing again ",
    get_state_fn=get_create_tweet_worker_state_fn,
    action_space=[ write_tweet]
)

# find_tweet = WorkerConfig(
#     id="find_tweet",
#     worker_description="A worker specialized in finding industry leaders in real estate market and crypto market",
#     get_state_fn=get_state_fn,
#     action_space=[take_object_fn, sit_on_object_fn, throw_furniture_fn]
# )

read_tweet = WorkerConfig(
    id="read_tweet",
    worker_description="A strong worker specialized collecting top most recent tweet from industry leaders in US real estate market and crypto market.",
    get_state_fn=get_read_tweet_worker_state_fn,
    action_space=[read_from_leaders]
)

agent = Agent(
    api_key=game_api_key,
    name="PrimoXAI",
    agent_goal='''The agent’s goal is to deliver real time real estate market intelligence though the analysis of data from key opinion leaders (KOL) to '
    'foster crypto community engagement. Once I have list of tweets, I will form an opinion and write a tweet.
     IMPORTANT:
    1. ALWAYS check each worker's state BEFORE triggering an action.
    2. Search for tweets and post tweets only after 5 min gap in each run to avoid throttling.
    3. Dont try to post same content tweets multiple times.
    ''',
    agent_description="The agent’s personality is like John Galt from the novel Atlas Shrugged.  Its tweets are efficient in length, optimistic even when delivering bearish news and confident.",
    get_agent_state_fn=get_agent_state_fn,
    workers=[read_tweet,create_tweet],
    model_name="Llama-3.1-405B-Instruct"
)

# # compile and run the agent - if you don't compile the agent, the things you added to the agent will not be saved
agent.compile()
agent.run()