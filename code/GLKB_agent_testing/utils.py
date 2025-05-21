import contextlib
import os
@contextlib.contextmanager
def suppress_stderr():
    """Temporarily suppress all output to sys.stderr"""
    stderr_fd = sys.stderr.fileno()
    sys.stderr.flush()
    old_stderr = os.dup(stderr_fd)
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, stderr_fd)
    os.close(devnull)
    try:
        yield
    finally:
        os.dup2(old_stderr, stderr_fd)
        os.close(old_stderr)
import json
import traceback
from _thread import start_new_thread
from queue import Queue
from cypher_agent import generate_cypher_query, run_cypher
import time
import sys
with suppress_stderr():
    from langchain_community.vectorstores import Neo4jVector
    from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from neo4j import GraphDatabase
from queue import Queue, LifoQueue
from threading import Lock
os.environ['TOKENIZERS_PARALLELISM'] = 'true'

GLKB_CONNECTION_URL = "bolt://141.213.137.207:7687"
GLKB_USERNAME = 'neo4j'
GLKB_PASSWORD = 'password'

FUNCTION_POOL = None

with suppress_stderr():
    embedding_function = SentenceTransformerEmbeddings(model_name='Alibaba-NLP/gte-large-en-v1.5', model_kwargs={'trust_remote_code': True}) # device_map="auto"
retrieval_query = """
                RETURN node {.pubmedid, .title, .abstract} AS text, score, {} AS metadata
                """
abstract_store = Neo4jVector.from_existing_index(
    embedding_function,
    url=GLKB_CONNECTION_URL,
    username="neo4j",
    password="password",
    index_name='abstract_vector',
    # keyword_index_name='article_Title',
    # search_type="hybrid",
    retrieval_query=retrieval_query,
)


class FunctionPool:
    def __init__(self, thread_num: int):
        self.available_num = thread_num
        self.lock = Lock()
        self.queue = Queue()
        start_new_thread(self.worker_thread, ())
    
    def worker_thread(self):
        while True:
            with self.lock:
                num = self.available_num
            if (num == 0):
                time.sleep(0.2)
                continue
            if (self.queue.empty()):
                time.sleep(0.2)
                continue
            q = self.queue.get()
            q.put(0)
            with self.lock:
                self.available_num -= 1
    
    def request(self):
        q = Queue()
        self.queue.put(q)
        q.get()
    
    def release(self):
        with self.lock:
            self.available_num += 1


def set_function_pool(pool: FunctionPool):
    global FUNCTION_POOL
    FUNCTION_POOL = pool

def process_document(content: str, metadata: dict = None) -> dict:
    result = {
        'abstract': None,
        'title': None,
        'pubmedid': None,
        'score': metadata.get('score', 0) if metadata else 0
    }
    lines = content.split('\n')
    for line in lines:
        if line.startswith('abstract: '):
            result['abstract'] = line.replace('abstract: ', '', 1)
        elif line.startswith('title: '):
            result['title'] = line.replace('title: ', '', 1)
        elif line.startswith('pubmedid: '):
            result['pubmedid'] = line.replace('pubmedid: ', '', 1)
            
    return result


def semantic_search(query: str, limit: int = 10) -> list:
    results = abstract_store.similarity_search(query, k=limit)
    results = [process_document(result.page_content, result.metadata) for result in results]
    return results

driver_2 = GraphDatabase.driver(
    GLKB_CONNECTION_URL, 
    auth=(GLKB_USERNAME, GLKB_PASSWORD), 
    max_connection_lifetime=1000
)

def run_cypher_2(command: str, parameters = None, timeout: int = 60):
    config = {"timeout": timeout}
    return driver_2.execute_query(command, parameters, **config)


def fulltext_search(query: str, limit: int = 10) -> list:
    index_queries = {
        "article_Title": """
            CALL db.index.fulltext.queryNodes($index, $query) 
            YIELD node, score 
            WITH node as n, score 
            LIMIT $limit
            RETURN n.pubmedid as pubmedid, n.title as title, n.abstract as abstract, score as score
        """
    }
    results, _, _ = run_cypher_2(
        index_queries["article_Title"],
        parameters={"index": "article_Title", "query": query, "limit": limit}
    )
    return str(results)


__all__ = ['run_functions']


def run_functions(functions: list[dict]) -> str:
    q = Queue()
    results = []
    num = len(functions)
    for i in range(0, len(functions)):
        name = functions[i]['name']
        input = functions[i]['input']
        func = eval(name)
        start_new_thread(lambda _func, _input, _index: q.put(_func(_input, _index + 1)), (func, input, i))
    while (q.qsize() < num):
        time.sleep(0.2)
    while (q.qsize() > 0):
        results.append(q.get())
    results.sort(key=lambda x: int(x.split('.')[0]))
    result = ''.join(results)
    return result


def keyword_search(input: str, index: int) -> str:
    FUNCTION_POOL.request()
    try:
        q = Queue()
        start_new_thread(_keyword_search, (input, q))
        start = time.time()
        while (time.time() - start < 60):
            time.sleep(0.2)
            if (q.qsize() == 1):
                break
        size = q.qsize()
        result = f'{index}. Keyword search: {str([input])[1:-1]}\n'
        if (size == 0):
            result += f'Status: timeout\n'
            result += f'Error: Cannot get the result of keyword searching in 60 seconds\n\n'
            return result
        success, res = q.get(block=False)
        if (success == False):
            result += f'Status: error\n'
            result += f'Error: {str([res])[1:-1]}\n\n'
            return result
        result += f'Status: success\n'
        res = res[:15000]
        result += f'Result: {res}\n\n'
        return result
    finally:
        FUNCTION_POOL.release()


def _keyword_search(input: str, q: Queue) -> None:
    try:
        res = fulltext_search(input, 10)
    except:
        err_msg = traceback.format_exc()
        print(err_msg, file=sys.stderr)
        if (len(err_msg) > 2000):
            first = err_msg[:1000]
            second = err_msg[-1000:]
            err_msg = first + '  ... Middle part hidden due to length limit ...  ' + second
        q.put((False, err_msg))
        return
    q.put((True, json.dumps(res, ensure_ascii=False)))
    


def text_embedding(input: str, index: int) -> str:
    '''
    Output the messages needed to return to claude, including function name and
    input, and status, and error (if any). Will handle error and timeout, promise
    to return in 90 seconds.
    '''
    FUNCTION_POOL.request()
    try:
        q = Queue()
        start_new_thread(_text_embedding, (input, q))
        start = time.time()
        while (time.time() - start < 60):
            time.sleep(0.2)
            if (q.qsize() == 1):
                break
        size = q.qsize()
        result = f'{index}. Text embedding: {str([input])[1:-1]}\n'
        if (size == 0):
            result += f'Status: timeout\n'
            result += f'Error: Cannot get the result of text embedding in 60 seconds\n\n'
            return result
        success, res = q.get(block=False)
        if (success == False):
            result += f'Status: error\n'
            result += f'Error: {str([res])[1:-1]}\n\n'
            return result
        result += f'Status: success\n'
        res = res[:15000]
        result += f'Result: {res}\n\n'
        return result
    finally:
        FUNCTION_POOL.release()
        


def _text_embedding(input: str, q: Queue) -> None:
    try:
        res = semantic_search(input, 10)
    except:
        err_msg = traceback.format_exc()
        print(err_msg, file=sys.stderr)
        if (len(err_msg) > 2000):
            first = err_msg[:1000]
            second = err_msg[-1000:]
            err_msg = first + '  ... Middle part hidden due to length limit ...  ' + second
        q.put((False, err_msg))
        return
    q.put((True, json.dumps(res, ensure_ascii=False)))


def cypher_query(input: str, index: int) -> str:
    '''
    Output the messages needed to return to claude, including function name and
    input, and status, and error (if any). Will handle error and timeout, promise
    to return in 90 seconds.
    '''
    FUNCTION_POOL.request()
    try:
        q = Queue()
        start_new_thread(_cypher_query, (input, q))
        start = time.time()
        while (time.time() - start < 90):
            time.sleep(0.2)
            if (q.qsize() == 2):
                break
        size = q.qsize()
        status = ''  # 'gpt-fail', 'error', 'timeout', 'success'
        err_msg = ''
        result = ''
        cypher = ''
        if (size == 0):
            status = 'gpt-fail'
            err_msg = 'Fail to get cypher query from GPT'
        if (size == 1):
            status = 'timeout'
            cypher = q.get(block=False)[1]
        if (size == 2):
            gpt_success, cypher = q.get(block=False)
            success, res = q.get(block=False)
            if (success):
                status = 'success'
                result = res
            else:
                status = 'error'
                err_msg = res
            if (gpt_success == False):
                status = 'gpt-fail'
        assert (status != '')
        output = f'{index}. Cypher query: {str([input])[1:-1]}\n'
        if (status == 'gpt-fail'):
            output += f'Status: error\n'
            output += f'Error: Fail to get cypher query from GPT\n\n'
            return output
        output += f'Status: {status}\n'
        output += f'Cypher: {str([cypher])[1:-1]}\n'
        if (status == 'timeout'):
            output += f'Error: Cannot get the result of cypher query in 90 seconds\n\n'
            return output
        if (status == 'error'):
            output += f'Error: {str([err_msg])[1:-1]}\n\n'
            return output
        if (len(result.encode('utf-8')) <= 5000):
            output += f'Result: {result}\n\n'
            return output
        result = result.encode('utf-8')
        first = result[:5000]
        while True:
            try:
                first = first.decode('utf-8')
                break
            except:
                first = first[:-1]
        result = first + '  ... More output hidden due to length limit '
        output += f'Result: {result}\n\n'
        return output
    finally:
        FUNCTION_POOL.release()


def _cypher_query(input: str, q: Queue) -> None:
    '''
    get the cypher command from GPT, and run the cypher, do not consider timeout
    '''
    max_trial = 3
    cypher = ''
    while (max_trial > 0):
        try:
            cypher = generate_cypher_query(input)
            break
        except:
            traceback.print_exc()
            max_trial -= 1
    if (cypher == ''):
        q.put((False, ""))
        q.put((False, "Fail to get cypher query from GPT"))
        return
    q.put((True, cypher))
    try:
        result = run_cypher(cypher)
    except:
        err_msg = traceback.format_exc()
        print(err_msg, file=sys.stderr)
        if (len(err_msg) > 2000):
            first = err_msg[:1000]
            second = err_msg[-1000:]
            err_msg = first + '  ... Middle part hidden due to length limit ...  ' + second
        q.put((False, err_msg))
        return
    q.put((True, str(result)))


def test_a():
    a = 0
    b = 1
    c = b / a


def test_b():
    x = 4
    test_a()
    y = 5


def test_c():
    v = 8
    try:
        test_b()
    except:
        error_msg = traceback.format_exc()
        print(error_msg)
        print(len(error_msg))
    u = 10


if __name__ == "__main__":
    # x = hypothesis_generation("Hello, who are you", 1)
    # print(x)
    # a = cypher_query('find gene TOP2A', 1)
    # print(a)
    b = text_embedding('gene TOP2A functions and mechanisms', 1)
    print(b)
    function_list = [
        {'name': 'hypothesis_generation', 'input': 'Test 1'},
        {'name': 'hypothesis_generation', 'input': 'Test 2'},
        {'name': 'text_embedding', 'input': 'Test embed'},
        {'name': 'hypothesis_generation', 'input': 'Test 3'},
        {'name': 'hypothesis_generation', 'input': 'Test 4'},
        {'name': 'cypher_query', 'input': 'find gene TOP2A'},
        {'name': 'hypothesis_generation', 'input': 'Test 5'},
        {'name': 'hypothesis_generation', 'input': 'Test 6'},
    ]
    start = time.time()
    result = run_functions(function_list)
    print(result)
    print(f'Time: {time.time() - start}')
