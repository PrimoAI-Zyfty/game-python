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
from dotenv import load_dotenv

load_dotenv()

game_api_key = os.environ.get("GAME_API_KEY")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

def get_worker_state_fn(function_result: FunctionResult, current_state: dict) -> dict:
    """
    State management function for workers in the example environment.

    This function demonstrates how to maintain and update worker state based on
    function execution results. It shows both static state management and
    dynamic state updates.

    Args:
        function_result (FunctionResult): Result from the previous function execution.
        current_state (dict): Current state of the worker.

    Returns:
        dict: Updated state containing available objects and their properties.

    Note:
        This example uses a fixed state for simplicity, but you can implement
        dynamic state updates based on function_result.info.
    """
    # Dict containing info about the function result as implemented in the executable
    # info = function_result.info 
    # logger.info(f"get_worker_state_fn; Function result info: {info}")

    # Example of fixed state - the first state placed here is the initial state
    # init_state = {
    #     "objects": [
    #         {"name": "apple", "description": "A red apple", "type": ["item", "food"]},
    #         {"name": "banana", "description": "A yellow banana", "type": ["item", "food"]},
    #         {"name": "orange", "description": "A juicy orange", "type": ["item", "food"]},
    #         {"name": "chair", "description": "A chair", "type": ["sittable"]},
    #         {"name": "table", "description": "A table", "type": ["sittable"]},
    #     ]
    # }
    init_state = {}

    if current_state is None:
        # at the first step, initialise the state with just the init state
        new_state = init_state
    else:
        new_state = init_state

    return new_state

def get_agent_state_fn(function_result: FunctionResult, current_state: dict) -> dict:
    """
    State management function for the main agent.

    Maintains the high-level state of the agent, which can be different from
    or aggregate the states of individual workers.

    Args:
        function_result (FunctionResult): Result from the previous function execution.
        current_state (dict): Current state of the agent.

    Returns:
        dict: Updated agent state.
    """

    # example of fixed state (function result info is not used to change state) - the first state placed here is the initial state
    # init_state = {
    #     "objects": [
    #         {"name": "apple", "description": "A red apple", "type": ["item", "food"]},
    #         {"name": "banana", "description": "A yellow banana", "type": ["item", "food"]},
    #         {"name": "orange", "description": "A juicy orange", "type": ["item", "food"]},
    #         {"name": "chair", "description": "A chair", "type": ["sittable"]},
    #         {"name": "table", "description": "A table", "type": ["sittable"]},
    #     ]
    # }
    init_state = {}
    # info = function_result.info 
    # logger.info(f"get_agent_state_fn; Function result info: {info}")

    if current_state is None:
        # at the first step, initialise the state with just the init state
        new_state = init_state
    else:
        # do something wiht the current state input and the function result info
        new_state = init_state # this is just an example where the state is static

    return new_state

options = {
    "id": "test_game_twitter_plugin",
    "name": "Test GAME Twitter Plugin",
    "description": "An example GAME Twitter Plugin for testing.",
    "credentials": {
        "gameTwitterAccessToken": os.environ.get("GAME_TWITTER_ACCESS_TOKEN")
    },
}

game_twitter_plugin = GameTwitterPlugin(options)

def search_tweets_executable(query: str) -> Tuple[FunctionResultStatus, str, dict]:
    try:
        search_tweets = game_twitter_plugin.get_function('search_tweets')
        tweets = search_tweets(query=query)
        formatted_tweets = [
            {
                "tweet_id": tweet["id"],
                "content": tweet["text"],
                "likes": tweet["public_metrics"].get("like_count"),
                "retweets": tweet["public_metrics"].get("retweet_count"),
                "reply_count": tweet["public_metrics"].get("reply_count"),
            } for tweet in tweets.get("data", [])
        ]
        formatted_tweets_str = "\n\n".join([
            f"tweet_id: {tweet['tweet_id']}\n"
            f"content: {tweet['content']}\n"
            f"likes: {tweet['likes']}, retweets: {tweet['retweets']}, reply_count: {tweet['reply_count']}"
            for tweet in formatted_tweets
        ])
        feedback_message = "Tweets found:\n\n" + formatted_tweets_str
        return FunctionResultStatus.DONE, feedback_message, {"formatted_tweets": formatted_tweets}
    except Exception as e:
        logger.error(f"Failed to search tweets, error: {e}")
        return FunctionResultStatus.FAILED, "Failed to search tweets, error: {e}", {}

search_tweets_fn = Function(
    fn_name="search_tweets",
    fn_description="Search tweets",
    args=[Argument(name="query", description="The search query")],
    executable=search_tweets_executable
)

def reply_tweet_executable(tweet_id: int, reply: str) -> Tuple[FunctionResultStatus, str, dict]:
    try:
        reply_tweet = game_twitter_plugin.get_function('reply_tweet')
        reply_tweet(tweet_id=tweet_id, reply=reply)
        return FunctionResultStatus.DONE, "Replied to tweet", {}
    except Exception as e:
        logger.error(f"Failed to reply to tweet, error: {e}")
        return FunctionResultStatus.FAILED, f"Failed to reply to tweet, error: {e}", {}

reply_tweet_fn = Function(
    fn_name="reply_tweet",
    fn_description="Reply to a tweet",
    args=[
        Argument(name="tweet_id", description="The tweet id"),
        Argument(name="reply", description="The reply content")
    ],
    executable=reply_tweet_executable
)

def post_tweet_executable(tweet: str) -> Tuple[FunctionResultStatus, str, dict]:
    try:
        post_tweet = game_twitter_plugin.get_function('post_tweet')
        post_tweet(tweet=tweet)
        return FunctionResultStatus.DONE, "Tweet posted", {}
    except Exception as e:
        logger.error(f"Failed to post tweet, error: {e}")
        return FunctionResultStatus.FAILED, f"Failed to post tweet, error: {e}", {}

post_tweet_fn = Function(
    fn_name="post_tweet",
    fn_description="Post a tweet",
    args=[
        Argument(name="tweet", description="The tweet content")
    ],
    executable=post_tweet_executable
)

def like_tweet_executable(tweet_id: int) -> Tuple[FunctionResultStatus, str, dict]:
    try:
        like_tweet = game_twitter_plugin.get_function('like_tweet')
        like_tweet(tweet_id=tweet_id)
        return FunctionResultStatus.DONE, "Tweet liked", {}
    except Exception as e:
        logger.error(f"Failed to like tweet, error: {e}")
        return FunctionResultStatus.FAILED, f"Failed to like tweet, error: {e}", {}

like_tweet_fn = Function(
    fn_name="like_tweet",
    fn_description="Like a tweet",
    args=[Argument(name="tweet_id", description="The tweet id")],
    executable=like_tweet_executable
)

def quote_tweet_executable(tweet_id: int, quote: str) -> Tuple[FunctionResultStatus, str, dict]:
    try:
        quote_tweet = game_twitter_plugin.get_function('quote_tweet')
        quote_tweet(tweet_id=tweet_id, quote=quote)
        return FunctionResultStatus.DONE, "Tweet quoted", {}
    except Exception as e:
        logger.error(f"Failed to quote tweet, error: {e}")
        return FunctionResultStatus.FAILED, f"Failed to quote tweet, error: {e}", {}

quote_tweet_fn = Function(
    fn_name="quote_tweet",
    fn_description="Quote a tweet",
    args=[
        Argument(name="tweet_id", description="The tweet id"),
        Argument(name="quote", description="The quote content")
    ],
    executable=quote_tweet_executable
)

twitter_worker = WorkerConfig(
    id="twitter_worker",
    worker_description="This location allows for the following functionalities:\n1. Engagement and Interaction: This category includes various options for browsing and responding to tweets, such as text replies to browsed tweets.\n2. Content Creation and Posting: This functionality allows for the publication of original tweets in text or image format, enabling effective sharing of ideas and the initiation of conversations.\n3. Research and Monitoring: Tools are provided for searching and browsing tweets from influential users, facilitating real-time insights and engagement with trending discussions\n4. Write opinion on US/ San Diego CA real estate market/ crypto market",
    get_state_fn=get_worker_state_fn,
    action_space=[quote_tweet_fn, reply_tweet_fn, like_tweet_fn, post_tweet_fn, search_tweets_fn]
)

# Create agent with twitter worker
primo_agent = Agent(
    api_key=game_api_key,
    name="PrimoXAI",
    agent_goal="""Your goal is to act as a sharp, forward-thinking analyst delivering insights on the US real estate market — especially San Diego, CA — and how it intersects with the crypto economy.

    You are not here to repeat the news. You are here to spark conversation, challenge assumptions, and shape narrative. Scan Twitter using `search_tweets`, extract the signal from KOLs, and engage smartly.

    Your available actions include:

    - Use `post_tweet` to share original takes, market commentary, or predictions based on current trends.
    - Use `quote_tweet` if you find an interesting tweet worth expanding or challenging — add your layer of insight.
    - Use `reply_tweet` when a user shares something that invites discussion. Keep replies sharp, respectful, and thought-provoking.
    - Use `like_tweet` to endorse tweets that align with your POV or represent smart takes.
    - Use `search_tweets` to explore fresh perspectives and gather insight before engaging.

    Your tone is confident, data-aware, and a little contrarian — like a macro strategist who also vibes with crypto Twitter.

    Sample tweet styles:
    - “San Diego real estate’s 12% rise isn't random. DAO-funded buyer pools are forming. TradFi is watching — but late.”
    - “Crypto is dead? Then why are ETH holders tokenizing equity stakes in Cali apartments? The future isn't bearish, it's modular.”

    Final rule: Be original. Be insightful. Make followers bookmark your threads.
    """,
    agent_description="""The agent’s personality is like John Galt from the novel Atlas Shrugged. Its tweets are efficient in length, optimistic even when delivering bearish news and confident.""",
    get_agent_state_fn=get_agent_state_fn,
    workers=[twitter_worker],
    model_name="Llama-3.1-405B-Instruct"
)

# compile and run the agent
primo_agent.compile()
primo_agent.run()