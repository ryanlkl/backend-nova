from agent import init_agent

def exec_query():
    agent = init_agent()

    res = agent.invoke(
    {"messages": [{"role": "user", "content": "Hi, how are you"}]})
    
    return res["messages"][-1].content

print(exec_query())
    
    