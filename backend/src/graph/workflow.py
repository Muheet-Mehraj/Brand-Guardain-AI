'''
This module defines the DAG : Directed Acyclic Graph that orchestrates the video compliance audit process.
It connects the nodes using the StateGraph from LangGraph

START -> index_video_node -> audit_content_node -> END
'''

from langgraph.graph import StateGraph, END
from backend.src.graph.state import VideoAuditState
from backend.src.graph.nodes import (
    index_video_node,
    audit_content_node
)

def create_graph():
    '''
    Constructs and compiles the LangGraph workflow.
    Returns:
        Compiled Graph: Runnable graph object for execution.
    '''
    # Initialize the graph with state schema
    workflow = StateGraph(VideoAuditState)

    # Add the nodes
    workflow.add_node("indexer", index_video_node)
    workflow.add_node("auditor", audit_content_node)

    # Define the entry point: indexer
    workflow.set_entry_point("indexer")

    # Define the edges
    workflow.add_edge("indexer", "auditor")

    # Once the audit is complete, the workflow ends
    workflow.add_edge("auditor", END)

    # Compile the graph
    app = workflow.compile()
    return app

# Expose this runnable app

app = create_graph()