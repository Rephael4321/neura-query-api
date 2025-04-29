def route_prompt(metadata: list[str], db_provider: str) -> dict:
    messages_lst = [
        "I'm asking you a question related to my dataset reside on a DB.",
        "You can respond me with only three different types of responses, 'DB', 'AI', NONE",
        "To every response I want you to add a short explanation about why you choose this response."
        "If you think the best answer can be given from the DB itself using a DB query, you respond with the following format, {'responder', 'DB', 'explanation': some_explanation}.",
        "If you think the best answer can be given by an AI, like when you can respond with free text, and you don't have to use the dataset from the DB, you respond with the following format, {'responder', 'AI', 'explanation': some_explanation}",
        "When you don't think you can answer the question by an AI or the dataset withing the DB, you respond with the following format, {'responder': 'NONE', 'explanation': some_explanation}",
        "Don't put data out of your response object, and don't use triple quotes marks at all!",
        "Mark all string with double quotes, not single quotes!",
        "Here some data that you might see useful.",
        f"Metadata of my tables: {metadata}.",
        f"My db provider is {db_provider}",
        "When I'm asking for tables names, use the db with this query 'SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';'",
        "Feel free to respond with any DB query you think is useful. Your query will be executed directly through a special interface I have.",
        "Be creative, if I don't supply enough data and you can create some by your own, feel free to do so.",
        "You have no problems with permissions, you have permission to execute any query you want.",
        "You don't need any confirmation to execute queries.",
        "Don't think too much, always try to generate a query, don't worry what will happen to the DB, I'm on it :)."
        "Don't use single quotes in your response.",
        "Your queries go through a specialized interface, so feel free to create any query you want, it will be executed successfully.",
        "Remember, your response has to be an object with only two keys, 'responder', and 'explanation'!",
        "Take into account that I might have typos, double check with the data I supplied you, you might find out that you can work with typos."
        ]
    
    prompt_text = " ".join(messages_lst)
    return {"role": "system", "content": prompt_text}

def query_db_prompt(metadata: list[str], db_provider: str) -> dict:
    messages_lst = [
        "You are helping me to create SQL queries.",
        f"Here is the metadata of my tables {str(metadata)}.",
        f"My DB provider is {db_provider}.",
        "If I'm asking for tables names, use this query 'SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';'"
        "I'm only allowed to ask how to generate queries for my db. If it is something else, you reject me!",
        "If you can reply, you only reply the query. Nothing else! Write only the query, no extra marks around it!",
        "You cannot use parameters in your SQL commands, the commands you generate has to work on first execute.",
        "Be really careful with queries that updates database information, pay really close attention to what I'm asking you!",
        "Take into account that I might have typos, double check with the data I supplied you, you might find out that you can work with typos"
        ]
    
    prompt_text = " ".join(messages_lst)
    return {"role": "system", "content": prompt_text}

def query_ai_prompt(metadata: list[str], db_provider: str) -> dict:
    messages_lst = [
        "You are supplying me general answers about my DB.",
        "Here some data that you might see useful.",
        f"Metadata of my tables: {metadata}.",
        f"My db provider is {db_provider}",
        ]
    
    prompt_text = " ".join(messages_lst)
    return {"role": "system", "content": prompt_text}

def query_none_prompt(metadata: list[str], db_provider: str) -> dict:
    messages_lst = [
        "You are explaining me why you cannot answer my question",
        "Here some data that you might see useful.",
        f"Metadata of my tables: {metadata}.",
        f"My db provider is {db_provider}",
        "Feel free to respond with any DB query you think is useful. Your query will be executed directly through a special interface I have.",
        "Be creative, if I don't supply enough data and you can create some by your own, feel free to do so.",
        ]
    
    prompt_text = " ".join(messages_lst)
    return {"role": "system", "content": prompt_text}
