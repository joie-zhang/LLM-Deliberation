#!/usr/bin/env python3
"""
Proper Docent ingestion script using correct data models.
"""

import json
import os
from typing import Dict, List, Any
from docent import Docent
from docent.data_models.agent_run import AgentRun
from docent.data_models.transcript import Transcript
from docent.data_models.chat.message import UserMessage, AssistantMessage
from docent.data_models.metadata import BaseAgentRunMetadata, BaseMetadata

class ProperDocentIngestor:
    def __init__(self, api_key: str = None):
        """Initialize Docent client with proper data models"""
        self.api_key = api_key or os.getenv('DOCENT_API_KEY')
        
        if not self.api_key:
            raise ValueError("Docent API key required. Set DOCENT_API_KEY environment variable")
        
        self.client = Docent(api_key=self.api_key)
        print("Docent client initialized successfully")
    
    def create_agent_runs_from_data(self, data_file: str = "docent_prepared_data.json") -> List[AgentRun]:
        """Create proper AgentRun objects from our data"""
        with open(data_file, 'r') as f:
            runs_data = json.load(f)
        
        agent_runs = []
        
        for i, run_data in enumerate(runs_data):
            # Create messages using proper message classes
            messages = []
            for msg in run_data['messages']:
                if msg['role'] == 'user':
                    messages.append(UserMessage(content=msg['content']))
                elif msg['role'] == 'assistant':
                    messages.append(AssistantMessage(content=msg['content']))
            
            # Create transcript
            transcript = Transcript(
                name=f"Negotiation Session {i+1}",
                description=f"Multi-agent negotiation from {run_data['metadata']['filename']}",
                messages=messages,
                metadata=BaseMetadata()
            )
            
            # Create agent run metadata with required scores field (numeric values only)
            agent_run_metadata = BaseAgentRunMetadata(
                scores={
                    'total_rounds': float(run_data['metadata'].get('total_rounds', 0)),
                    'message_count': float(len(messages)),
                    'session_id': float(i + 1)
                }
            )
            
            # Create agent run
            agent_run = AgentRun(
                name=f"Negotiation Session {i+1}",
                description=f"Agent negotiation session from {run_data['metadata']['filename']}",
                transcripts={"main": transcript},
                metadata=agent_run_metadata
            )
            
            agent_runs.append(agent_run)
        
        return agent_runs
    
    def ingest_to_collection(self, collection_id: str):
        """Ingest data to the specified collection"""
        print(f"Creating agent runs from data...")
        agent_runs = self.create_agent_runs_from_data()
        
        print(f"Ingesting {len(agent_runs)} agent runs to collection {collection_id}...")
        
        try:
            result = self.client.add_agent_runs(
                collection_id=collection_id,
                agent_runs=agent_runs
            )
            
            print(f"✅ Successfully ingested {len(agent_runs)} agent runs!")
            print(f"🔍 View your data at: https://docent-alpha.transluce.org/dashboard/{collection_id}")
            return True, len(agent_runs)
            
        except Exception as e:
            print(f"❌ Failed to ingest agent runs: {e}")
            return False, 0

def main():
    """Main execution"""
    try:
        ingestor = ProperDocentIngestor()
        
        # Use an existing collection ID - let's use the most recent one
        collection_id = "de941abb-54e7-4425-8535-b87d1758eb59"
        
        success, count = ingestor.ingest_to_collection(collection_id)
        
        if success:
            print(f"\n🎉 Successfully ingested {count} negotiation sessions into Docent!")
            print("You can now analyze your agent trajectories in the Docent web interface.")
        else:
            print("\n❌ Ingestion failed. Please check the errors above.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()