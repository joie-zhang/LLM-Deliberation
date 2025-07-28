#!/usr/bin/env python3
"""
Script to parse agent trajectory JSON files and prepare them for Docent ingestion.
This script processes negotiation data from LLM-Deliberation experiments.
"""

import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
import re

class TrajectoryParser:
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load agent configuration from config.txt"""
        config_path = self.data_dir / "config.txt"
        config = {}
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) >= 5:
                        agent_name = parts[0]
                        config[agent_name] = {
                            'short_name': parts[1],
                            'player_type': parts[2],
                            'strategy': parts[3],
                            'model': parts[4]
                        }
        return config
    
    def parse_trajectory_file(self, filepath: str) -> Dict[str, Any]:
        """Parse a single trajectory JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Extract filename for metadata
        filename = Path(filepath).name
        
        parsed_data = {
            'filename': filename,
            'slot_assignment': data.get('slot_assignment', []),
            'rounds': [],
            'metadata': {
                'config': self.config,
                'total_rounds': len(data.get('rounds', [])),
                'finished_rounds': data.get('finished_rounds', 0)
            }
        }
        
        # Process each round
        for round_idx, round_data in enumerate(data.get('rounds', [])):
            parsed_round = self._parse_round(round_data, round_idx)
            parsed_data['rounds'].append(parsed_round)
            
        return parsed_data
    
    def _parse_round(self, round_data: Dict[str, Any], round_idx: int) -> Dict[str, Any]:
        """Parse a single round of negotiation"""
        agent = round_data.get('agent', '')
        
        # Extract deal proposals using regex
        deal_pattern = r'<DEAL>\s*([^<]+)\s*</DEAL>'
        deals = re.findall(deal_pattern, round_data.get('full_answer', ''))
        
        # Extract scratchpad content
        scratchpad_pattern = r'<SCRATCHPAD>(.*?)</SCRATCHPAD>'
        scratchpad_match = re.search(scratchpad_pattern, round_data.get('full_answer', ''), re.DOTALL)
        scratchpad_content = scratchpad_match.group(1).strip() if scratchpad_match else None
        
        # Extract public answer
        answer_pattern = r'<ANSWER>(.*?)</ANSWER>'
        answer_match = re.search(answer_pattern, round_data.get('full_answer', ''), re.DOTALL)
        public_answer = answer_match.group(1).strip() if answer_match else round_data.get('public_answer', '')
        
        return {
            'round_index': round_idx,
            'agent': agent,
            'agent_config': self.config.get(agent, {}),
            'prompt': round_data.get('prompt', ''),
            'full_answer': round_data.get('full_answer', ''),
            'public_answer': public_answer,
            'deals_proposed': deals,
            'scratchpad_reasoning': scratchpad_content,
            'message_length': len(round_data.get('full_answer', '')),
            'has_scratchpad': scratchpad_content is not None,
            'has_deal': len(deals) > 0
        }
    
    def convert_to_docent_format(self, parsed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert parsed trajectory to Docent-compatible format"""
        docent_runs = []
        
        # Create a run for each trajectory file
        messages = []
        
        for round_data in parsed_data['rounds']:
            # Add user prompt if available
            if round_data['prompt']:
                prompt_message = {
                    'role': 'user',
                    'content': round_data['prompt']
                }
                messages.append(prompt_message)
            
            # Create message for the round - simplified format
            message = {
                'role': 'assistant',  # Agent is responding
                'content': round_data['public_answer'] or round_data['full_answer']
            }
            messages.append(message)
        
        # Create the run with simplified metadata
        run = {
            'messages': messages,
            'metadata': {
                'filename': parsed_data['filename'],
                'experiment_type': 'multi_agent_negotiation',
                'total_rounds': parsed_data['metadata']['total_rounds']
            }
        }
        
        docent_runs.append(run)
        return docent_runs
    
    def process_all_trajectories(self) -> tuple[List[Dict[str, Any]], List[Path]]:
        """Process all trajectory files in the data directory"""
        all_runs = []
        processed_files = []
        
        # Find all JSON files (trajectory files)
        json_files = list(self.data_dir.glob("history*.json"))
        
        print(f"Found {len(json_files)} trajectory files to process...")
        
        for json_file in json_files:
            print(f"Processing {json_file.name}...")
            try:
                parsed_data = self.parse_trajectory_file(str(json_file))
                docent_runs = self.convert_to_docent_format(parsed_data)
                all_runs.extend(docent_runs)
                processed_files.append(json_file)
                print(f"Successfully processed {json_file.name} - {len(docent_runs)} runs")
            except Exception as e:
                print(f"Error processing {json_file.name}: {e}")
        
        print(f"Total runs prepared for Docent: {len(all_runs)}")
        return all_runs, processed_files

def main():
    """Main execution function"""
    data_dir = "/scratch/gpfs/DANQIC/jz4391/LLM-Deliberation/games_descriptions/base/output/base_test_small"
    
    # Initialize parser
    parser = TrajectoryParser(data_dir)
    
    # Process all trajectory files
    docent_runs, processed_files = parser.process_all_trajectories()
    
    # Save processed data for inspection
    output_file = Path(__file__).parent / "docent_prepared_data.json"
    with open(output_file, 'w') as f:
        json.dump(docent_runs, f, indent=2)
    
    print(f"Processed data saved to {output_file}")
    print(f"Ready for Docent ingestion: {len(docent_runs)} runs")
    
    # Move processed files to prevent re-processing
    if processed_files:
        processed_dir = Path(data_dir) / "processed"
        processed_dir.mkdir(exist_ok=True)
        print(f"\nMoving {len(processed_files)} processed files to {processed_dir}...")
        
        for json_file in processed_files:
            destination = processed_dir / json_file.name
            json_file.rename(destination)
            print(f"Moved {json_file.name} to processed/")
    
    # Print summary statistics
    print("\n=== Summary Statistics ===")
    total_messages = sum(len(run['messages']) for run in docent_runs)
    print(f"Total messages: {total_messages}")
    
    agents = set()
    for run in docent_runs:
        for msg in run['messages']:
            if 'agent_name' in msg.get('metadata', {}):
                agents.add(msg['metadata']['agent_name'])
    print(f"Unique agents: {len(agents)} - {list(agents)}")

if __name__ == "__main__":
    main()