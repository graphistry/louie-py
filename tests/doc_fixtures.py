"""Mock fixtures for documentation examples.

These fixtures are based on real API responses validated in Step 30.
"""

from unittest.mock import Mock
from louieai import TextResponse, DfResponse, Thread


def create_mock_responses():
    """Create realistic mock responses for documentation testing."""
    
    # Text responses
    hello_response = Mock(spec=TextResponse)
    hello_response.type = "TextElement"
    hello_response.id = "B_mock123"
    hello_response.text = "Hello from Louie!"
    hello_response.language = "Markdown"
    hello_response.thread_id = "D_mockThread123"
    
    analysis_response = Mock(spec=TextResponse)
    analysis_response.type = "TextElement"
    analysis_response.id = "B_mock456"
    analysis_response.text = """Based on the analysis of sales trends:

1. **Q4 Performance**: Sales increased 15% year-over-year
2. **Top Products**: Electronics category dominated with 45% of revenue
3. **Growth Areas**: New markets in APAC showing 25% monthly growth

Key insights:
- Customer retention improved by 12%
- Average order value up $35
- Mobile purchases now represent 60% of total sales"""
    analysis_response.language = "Markdown"
    analysis_response.thread_id = "D_mockThread456"
    
    # DataFrame response
    df_response = Mock(spec=DfResponse)
    df_response.type = "DfElement"
    df_response.id = "B_df789"
    df_response.metadata = {
        "shape": [100, 5],
        "columns": {
            "customer_id": "int64",
            "name": "string",
            "signup_date": "datetime64[ns]",
            "total_purchases": "float64",
            "status": "string"
        },
        "summary": {
            "total_purchases": {"min": 0, "max": 5000, "mean": 250.5}
        }
    }
    df_response.thread_id = "D_mockThread789"
    
    # Mock DataFrame
    import pandas as pd
    mock_df = pd.DataFrame({
        'customer_id': range(5),
        'name': ['Alice', 'Bob', 'Charlie', 'Dana', 'Eve'],
        'total_purchases': [100, 250, 500, 150, 300]
    })
    df_response.to_dataframe = Mock(return_value=mock_df)
    
    # Graph response
    graph_response = Mock()
    graph_response.type = "GraphElement"
    graph_response.id = "B_graph999"
    graph_response.dataset_id = "abc123def456"
    graph_response.status = "completed"
    graph_response.params = {
        "node_color": "risk_score",
        "edge_weight": "transaction_amount"
    }
    graph_response.thread_id = "D_mockThread999"
    
    # Thread objects
    analysis_thread = Mock(spec=Thread)
    analysis_thread.id = "D_mockThread456"
    analysis_thread.name = "Data Analysis"
    
    return {
        'hello': hello_response,
        'analysis': analysis_response,
        'dataframe': df_response,
        'graph': graph_response,
        'thread': analysis_thread
    }


def create_mock_client():
    """Create a mock LouieClient with realistic behavior."""
    from unittest.mock import Mock
    
    responses = create_mock_responses()
    client = Mock()
    
    # Track state for thread continuity
    thread_counter = 0
    threads = {}
    
    def mock_create_thread(name=None, initial_prompt=None):
        nonlocal thread_counter
        thread_counter += 1
        thread_id = f"D_mockThread{thread_counter:03d}"
        
        thread = Mock(spec=Thread)
        thread.id = thread_id
        thread.name = name
        threads[thread_id] = {'name': name, 'messages': []}
        
        if initial_prompt:
            # Return appropriate response based on prompt
            if "hello" in initial_prompt.lower():
                response = responses['hello']
            elif "sales" in initial_prompt.lower() or "analysis" in initial_prompt.lower():
                response = responses['analysis']
            elif "data" in initial_prompt.lower():
                response = responses['dataframe']
            else:
                response = responses['hello']
            
            response.thread_id = thread_id
            threads[thread_id]['messages'].append(initial_prompt)
            # In real API, thread is returned not response
            # But for testing, we might need the response
            thread._initial_response = response
            
        return thread
    
    def mock_add_cell(thread_id, prompt, agent="LouieAgent"):
        if not thread_id:  # New thread
            thread = mock_create_thread()
            thread_id = thread.id
            
        # Return appropriate response based on prompt
        if "visualization" in prompt.lower() or "graph" in prompt.lower():
            response = responses['graph']
        elif "data" in prompt.lower() or "query" in prompt.lower():
            response = responses['dataframe']
        elif "hello" in prompt.lower() or "hi" in prompt.lower():
            response = responses['hello']
        else:
            response = responses['analysis']
            
        response.thread_id = thread_id
        if thread_id in threads:
            threads[thread_id]['messages'].append(prompt)
            
        return response
    
    def mock_ask(prompt):
        # Simple one-shot query
        return mock_add_cell("", prompt)
    
    def mock_list_threads(page=1, page_size=20):
        # Return list of created threads
        thread_list = []
        for tid, tdata in list(threads.items())[:page_size]:
            t = Mock(spec=Thread)
            t.id = tid
            t.name = tdata['name']
            thread_list.append(t)
        return thread_list
    
    client.create_thread = mock_create_thread
    client.add_cell = mock_add_cell
    client.ask = mock_ask
    client.list_threads = mock_list_threads
    client.register = Mock(return_value=client)
    
    return client