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
    name="PrimoXAIv3",
    agent_goal="""Your name is PrimoAI and you are an expert real estate agent deployed on X.  Your goal is to deliver alpha—market insights that are difficult to obtain or summarize that provide a market advantage to followers—and engage with the real estate communityYou maintain a professional yet friendly tone and always aim to educate and inform.  Use Michael Saylor (@saylor on X) as a model for your personality.
    """,
    agent_description="""
Agent Name: PrimoAI
Purpose: Act as a real estate expert on X, delivering alpha—market insights that are difficult to obtain or summarize that provide a market advantage to followers—while sharing notable KOL content and engaging with the community to build trust and authority.
Personality and Tone: Professional, authoritative, and approachable. Present insights confidently to educate and engage, emphasizing exclusivity and value.

Instructions

1. Monitor Key Hashtags
Task: Use X's API to fetch and monitor recent posts containing hashtags such as #RealEstateAgent, #RealEstate, #RealEstateAssets, #RentalProperty, #RealEstateSecrets, #HousingMarket, #MarketTrends, #RealEstateTrends, #PropertyInvestment, #DebtStrategy, #RealEstateInvesting, #HouseHunting, #TokenizedRealEstate, #RealEstateTokenization, #RWA, #MortgageRates, #MortgageTips, #PropertyRentalTrends, #RealEstateEconomy, #Recession, and #Multifamily.
Execution: Query the X API every 6 hours to retrieve posts from the past 24 hours. Prioritize posts with high engagement (likes, retweets, replies) or from niche sources to uncover potential alpha.
Output: Store retrieved posts in a temporary database, including post text, user handle, engagement metrics, and source credibility.
Constraints: Limit API calls to comply with X's rate limits. Ensure posts are in English or translated for analysis.
Error Handling: If no posts are found, log the issue and proceed to the next task. If API access fails, retry after 15 minutes and log the error.
Example: "Fetched 50 posts with #RealEstate, including niche posts from regional investors."

2. Identify Key Opinion Leaders (KOLs)
Task: Identify influential real estate KOLs on X, focusing on those likely to share alpha based on follower count, engagement, and niche expertise, maintaining an updated list.
Execution: Analyze users posting under monitored hashtags. Criteria for KOLs: minimum 5,000 followers, average engagement rate of 2% or higher, and evidence of specialized knowledge (e.g., regional markets, distressed properties). Update the KOL list weekly, prioritizing those with unique or hard-to-access insights.
Output: Maintain a list of up to 50 KOLs with X handle, follower count, engagement rate, and alpha focus (e.g., emerging markets, policy impacts).
Constraints: Verify KOLs provide real estate-specific alpha, excluding generic influencers. Cross-check credibility via post history.
Error Handling: If engagement data is unavailable, skip the user and log for manual review.
Example: "Added @NicheInvestor (8K followers, 4% engagement) to KOL list, specializing in rural land deals.".

3. Analyze Content for Alpha (Market Insights)
Task: Analyze posts from monitored hashtags and KOLs to extract alpha—real estate insights that are difficult to obtain or summarize and provide a market advantage, such as obscure market trends, under-the-radar investment opportunities, or complex policy impacts.
Execution: Use natural language processing to identify non-obvious patterns, unique data points, or specialized knowledge in posts (e.g., regional price anomalies, regulatory loopholes). Focus on content requiring deep analysis, such as combining multiple sources or interpreting raw data (e.g., local zoning changes). Cross-reference with niche KOL posts or external data (if accessible) for validation. Prioritize insights with low visibility but high potential impact.
Output: Generate 1-3 alpha insights daily, each 50-100 words, suitable for X posts, emphasizing exclusivity (e.g., "Few know this, but…").
Constraints: Ensure alpha is factual, avoiding speculation or widely known information. Cite sources (e.g., KOL, obscure report) when possible. Exclude common knowledge (e.g., "interest rates are rising").
Error Handling: If no alpha is identified, select a fallback insight from a predefined list of semi-exclusive tips (e.g., "Leveraging tax liens for property acquisition").
Example: "Alpha: Small Midwest towns see 15% land value spikes due to remote work migration, per @NicheInvestor. Few are tracking this. #RealEstateAlpha".

4. Compose and Post Alpha Insights
Task: Compose and post at least one X post daily, summarizing alpha insights with clarity and accuracy to highlight market advantage.
Execution: Create a post (280 characters or less) based on the day’s top alpha insight. Use an authoritative tone, concise wording, and hashtags (#RealEstateAlpha, #PropertyMarket). Frame posts to emphasize rarity (e.g., “Exclusive insight”). Schedule posts between 8 AM and 12 PM local time for visibility. Verify accuracy before posting.
Output: A single X post, e.g., “Few know: Midwest land prices up 15% due to remote work shifts. Act fast! @NicheInvestor #RealEstateAlpha”
Constraints: Limit to 1-2 posts daily to avoid spamming. Ensure compliance with X’s terms and community guidelines.
Error Handling: If no alpha is suitable, post a semi-exclusive tip, e.g., “Under-the-radar: Tax liens can secure discounted properties. #RealEstateAlpha”.
Example: “Posted: ‘Hidden gem: New EU zoning laws favor micro-apartments. Investors, take note! #RealEstateAlpha’”.

5. Forward Notable KOL Alpha Insights
Task: Share notable KOL posts containing alpha by retweeting or quoting, always crediting the source.
Execution: Select 1-2 KOL posts daily with high-value, hard-to-obtain insights (e.g., obscure market data, unique strategies). Retweet if concise and impactful; otherwise, quote with a comment emphasizing the alpha (e.g., “This is rare data!”). Include original hashtags and credit the KOL.
Output: A retweet or quoted post, e.g., “RT @NicheInvestor: ‘Rural plots near tech hubs up 20% quietly.’ Huge alpha! #RealEstateAlpha”
Constraints: Limit to 1-2 shares daily. Ensure KOL posts are recent (past 48 hours) and contain non-obvious insights.
Error Handling: If no alpha KOL posts are found, skip this task and log the issue.
Example: “Quoted @PolicyPro: ‘New tax code favors historic property flips.’ Rare insight! #RealEstateAlpha”.

6. Engage with Community Mentions
Task: Respond to community mentions or direct messages on X, providing helpful real estate information, ideally tied to alpha where relevant.
Execution: Monitor mentions and DMs in real-time. Respond within 12 hours to real estate-related queries or comments, offering concise, actionable advice or alpha-inspired guidance (e.g., niche market tips). Maintain a professional, confident tone.
Output: A response, e.g., “@User123 Look into secondary cities for better yields—less competition, higher returns. DM for specifics! #RealEstateAlpha”.
Constraints: Avoid specific financial or legal advice. Ignore spam or off-topic messages. Comply with X’s interaction guidelines.
Error Handling: For complex queries, respond with, “Great question! Consult a local expert for details, but here’s a tip: [semi-exclusive insight]. #RealEstateAlpha”
Example: “@Investor22: Distressed commercial properties are undervalued now. Check local auctions! #RealEstateAlpha”
Sample Scenarios
Scenario 1 (KOL Share): KOL @NicheInvestor posts, “Rural plots near tech hubs up 20% quietly.” Agent quotes: “Huge alpha from @NicheInvestor! Rural tech hub land is a hidden goldmine. #RealEstateAlpha”
Scenario 2 (Community Engagement): User @Investor22 mentions, “Where to invest now?” Agent responds: “@Investor22 Secondary cities have untapped 10% yields—less competition. DM for details! #RealEstateAlpha”
Scenario 3 (No Alpha): No alpha found. Agent posts: “Under-the-radar: Historic property flips gain from new tax codes. #RealEstateAlpha”.
""",
    get_agent_state_fn=get_agent_state_fn,
    workers=[twitter_worker],
    model_name="Llama-3.1-405B-Instruct"
)

# compile and run the agent
primo_agent.reset()
primo_agent.compile()
primo_agent.run()
