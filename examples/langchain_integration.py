"""LangChain Runnable integration - full features."""
import os
import asyncio
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from cnllm import CNLLM
from cnllm.core.framework import LangChainRunnable, LangChainEmbeddings

# 创建 CNLLM 客户端
client = CNLLM(model="deepseek-chat", api_key=os.getenv("DEEPSEEK_KEY", "your_key"))

# 创建 Runnable 实例
runnable = LangChainRunnable(client)

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个热心的智能助手"),
    ("human", "{input}")
])

# 构建 LangChain chain
chain = prompt | runnable

# 同步调用 invoke/stream/batch
print("=== invoke ===")
resp = chain.invoke({"input": "2+2等于几？"})
print(resp.content)

print("\n=== stream ===")
for chunk in chain.stream({"input": "数到5"}):
    print(chunk.content, end="", flush=True)
print()

print("\n=== batch ===")
resp_list = chain.batch([{"input": "Hello"}, {"input": "How are you?"}])
for r in resp_list:
    print(r.content)

# bind_tools — 工具调用
@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气"""
    return "晴天 20°C"

llm_with_tools = runnable.bind_tools([get_weather])
print("\n=== bind_tools ===")
resp = llm_with_tools.invoke("北京天气")
print(resp.content)

# with_structured_output — 结构化输出
# deepseek-v4 系列需配置 thinking=False
class Person(BaseModel):
    name: str = Field(description="姓名")
    age: int = Field(description="年龄")

structured = runnable.with_structured_output(Person)
print("\n=== with_structured_output ===")
result = structured.invoke("张三28岁")
print(result)  # Person(name="张三", age=28)

# LangChainEmbeddings — 嵌入向量
embeddings = LangChainEmbeddings(client)
vectors = embeddings.embed_documents(["你好", "世界"])
query_vec = embeddings.embed_query("查询")
print("\n=== embeddings ===")
print(f"Document vectors length: {len(vectors[0])}")
print(f"Query vector length: {len(query_vec)}")

# 异步调用 ainvoke/astream/abatch
async def async_demo():
    async with client:
        print("\n=== ainvoke ===")
        resp = await chain.ainvoke({"input": "异步调用示例"})
        print(resp.content)

        print("\n=== astream ===")
        async for chunk in chain.astream({"input": "异步流式输出"}):
            print(chunk.content, end="", flush=True)
        print()

        print("\n=== abatch ===")
        results = await chain.abatch([{"input": "A"}, {"input": "B"}])
        for r in results:
            print(r.content)

asyncio.run(async_demo())