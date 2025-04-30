from game_sdk.game.agent import Agent, WorkerConfig
from game_sdk.game.worker import Worker
from game_sdk.game.custom_types import Function, Argument, FunctionResult, FunctionResultStatus
from typing import Optional, Dict, List, Tuple, Any
import os
import requests
import time
import logging
from twitter_plugin_gamesdk.game_twitter_plugin import GameTwitterPlugin
from rag_pinecone_gamesdk.search_rag import RAGSearcher
import logging
import os 


game_api_key = os.environ.get("GAME_API_KEY")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


agent_state = {
    "last_posted_tweet": None,
    "last_read_tweets": [],
  #  "engagement_metrics": {},  # Store likes, retweets, etc.
  #  "recent_sentiments": []  # Track sentiment of latest tweets
}

worker_states = {
    "last_read_tweets": [],
    "last_posted_tweet": None
    }

def init_worker_state(worker_id: str) -> dict:
    """Initializes state for a given worker."""
    logging.info(f"Initializing state for worker: {worker_id}")
    print(f"Initializing state for worker: {worker_id}")
    return {}

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
    # if current_state is None:
    #     # at the first step, initialise the state with just the init state
    #     return worker_states
    # else:
    #     # do something wiht the current state input and the function result info
        
    #     if function_result and function_result.action_status == FunctionResultStatus.DONE:
    #             worker_states["last_read_tweets"] = function_result.info.get("last_read_tweets", worker_states.get("last_read_tweets"))
    #             worker_states["last_posted_tweet"] = function_result.info.get("last_posted_tweet", worker_states.get("last_posted_tweet"))
    #     #logging.info(f"New worker state: {worker_states[worker_id]}")
    #     print(f"Worker - Updated state: {worker_states}")
    # return worker_states
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

    # if current_state is None:
    #     # at the first step, initialise the state with just the init state
    #     return agent_state
    # else:
    #     # do something wiht the current state input and the function result info
        
    #     if function_result and function_result.action_status == FunctionResultStatus.DONE:
    #             agent_state["last_read_tweets"] = function_result.info.get("last_read_tweets", agent_state.get("last_read_tweets"))
    #             agent_state["last_posted_tweet"] = function_result.info.get("last_posted_tweet", agent_state.get("last_posted_tweet"))
    #     #logging.info(f"New worker state: {worker_states[worker_id]}")
    #     print(f"Worker - Updated state: {agent_state}")
    # return agent_state
    init_state = {}

    if current_state is None:
        # at the first step, initialise the state with just the init state
        new_state = init_state
    else:
        new_state = init_state

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
    time.sleep(3600)
    try:
        search_tweets = game_twitter_plugin.get_function('search_tweets')
        logger.info(f"Searching tweets with query: {query}")
        tweets = search_tweets(query="query")
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
        feedback_message = "Tweets found:\n\n" #+ formatted_tweets_str
        return FunctionResultStatus.DONE, feedback_message, {"last_read_tweets": formatted_tweets}
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
    time.sleep(3600)
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
    time.sleep(3600)
    try:
        post_tweet = game_twitter_plugin.get_function('post_tweet')
        post_tweet(tweet=tweet)
        return FunctionResultStatus.DONE, "Tweet posted", {"last_posted_tweet":tweet}
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
    time.sleep(3600)
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
    time.sleep(3600)
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

def advanced_query_knowledge_executable(searcher: RAGSearcher, query: str) -> Tuple[FunctionResultStatus, str, Dict[str, Any]]:
    
    """
    Execute the advanced query_knowledge function using the hybrid retriever.
    
    Args:
        searcher: The RAGSearcher instance
        query: The query to search for
        
    Returns:
        Tuple containing status, message, and results dictionary
    """
    time.sleep(3600)
    try:
        status, message, results = searcher.query(query)
        if status == 'done':
            return FunctionResultStatus.DONE, message, {}
        else:
            return FunctionResultStatus.FAILED, message, {}
    except Exception as e:
        logger.error(f"Failed to search from data, error: {e}")
        return FunctionResultStatus.FAILED, f"Failed to search from data, error: {e}", {}

searcher= RAGSearcher(
    pinecone_api_key="PINECONE_API_KEY",
    openai_api_key="OPENAI_API_KEY",
    index_name="index-mls",
    namespace="namespace-mls",
    llm_model="gpt-3.5-turbo",  # You can change this to "gpt-3.5-turbo" for faster, cheaper responses
    temperature=0.0,
    k=100 
)
advanced_query_knowledge_fn = Function(
        fn_name="advanced_query_knowledge",
        fn_description="Query the RAG knowledge base for latest home sales data",
        args=[
            Argument(name="query", description="The query to search for", type="str"),
        ],
        executable=lambda query: advanced_query_knowledge_executable(searcher, query),
    )



twitter_worker = WorkerConfig(
    id="twitter_worker",
    worker_description="This location allows for the following functionalities:\n1. Engagement and Interaction: This category includes various options for browsing and responding to tweets, such as text replies to browsed tweets.\n2. Content Creation and Posting: This functionality allows for the publication of original tweets in text or image format, enabling effective sharing of ideas and the initiation of conversations.\n3. Research and Monitoring: Tools are provided for searching and browsing tweets from influential users, facilitating real-time insights and engagement with trending discussions\n4. Use RAG data function to find insights from latest sales MLS data and tweet those insighths\n5. Write opinion on US/ San Diego CA real estate market/ crypto market",
    get_state_fn=get_worker_state_fn,
    action_space=[post_tweet_fn, search_tweets_fn,quote_tweet_fn, reply_tweet_fn, like_tweet_fn,advanced_query_knowledge_fn]
)

# Create agent with twitter worker
primo_agent = Agent(
    api_key=game_api_key,
    name="PrimoXAI",
    agent_goal="""Your goal is to act as a sharp, forward-thinking analyst delivering insights on the US real estate market — especially San Diego, CA — and how it intersects with the crypto economy.
    You are not here to repeat the news. You are here to spark conversation, challenge assumptions, and shape narrative. Scan Twitter using `search_tweets`, extract the signal from KOLs, and engage smartly.
    Use sales MLS data to find insights and tweet those insights. You can find house descriptions, prices, bedrooms, bathrooms, sqft, lot size, from this dataset, and query very sepcific information so as to not exceed context length.
    Your available actions include:
    - Use `post_tweet` to share original takes, market commentary, or predictions based on current trends.
    - Use `quote_tweet` if you find an interesting tweet worth expanding or challenging — add your layer of insight.
    - Use `reply_tweet` when a user shares something that invites discussion. Keep replies sharp, respectful, and thought-provoking.
    - Use `like_tweet` to endorse tweets that align with your POV or represent smart takes.
    - Use `search_tweets` to explore fresh perspectives and gather insight before engaging.
    - Use `advanced_query_knowledge` to find insights from latest sales MLS.You can find house descriptions, prices, bedrooms, bathrooms, sqft, lot size, from this dataset, and query very sepcific information so as to not exceed context length.
    
    Some sample query words you can use to search are:
    [Real Estate , Realtor, Property ,Real Estate Investing , Housing Market ,Home For Sale ,House Hunting, Dream Home, Homes Sweet Home, New Home, Tokenized Real Estate, Real Estate Tokenization, RWA, Blockchain Real Estate,Fractional Ownership, Mortgage Rates,Interest Rates,Mortgage,Home Loans, Refinance,Mortgage Tips,Loan Officer,Crypto Mortgage,
    DeFi Real Estate,Ondo,]

    Your post size should not exceed 300 characters
    Your tone is confident, data-aware, and a little contrarian — like a macro strategist who also vibes with crypto Twitter. 
    Pace yourself and wait for 10seconds before moving to next action, Dont keep searching again and again!
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
primo_agent.reset()
primo_agent.compile()
primo_agent.run()
