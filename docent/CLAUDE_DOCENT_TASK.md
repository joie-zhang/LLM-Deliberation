# Using Transluce Docent to Analyze Agent Trajectories

## Overview
This document outlines the steps to use Transluce Docent for analyzing agent negotiation trajectories from the LLM-Deliberation project. The data consists of multi-agent negotiation sessions with different agent strategies (cooperative vs greedy) using GPT-4 models.

## Step-by-Step Implementation Plan

### 1. Environment Setup
- **Install docent-python**: `pip install docent-python`
- **Sign up** at docent-alpha.transluce.org
- **Create API key** in Docent dashboard
- **Set up environment variables** for authentication

### 2. Data Analysis and Preparation
- **Parse JSON trajectory files** (history17_39_08.json, etc.) to extract:
  - Agent conversations and negotiations
  - Decision-making patterns
  - Deal proposals and responses
  - Scratchpad reasoning (internal thought processes)
- **Extract metadata** from config.txt (agent types, strategies, models used)
- **Identify key conversation elements** (deals, reasoning, negotiations)

### 3. Docent Integration Setup
- **Initialize Docent client** with API credentials
- **Create a collection** for the negotiation experiment
- **Design metadata schema** to capture:
  - Agent roles (Mayor, SportCo, Environmental League, etc.)
  - Strategy types (cooperative vs greedy)
  - Model used (gpt-4.1-mini-2025-04-14)
  - Round numbers and timestamps
  - Deal proposals and outcomes

### 4. Data Ingestion
- **Transform JSON trajectory data** into Docent-compatible format
- **Create conversation transcripts** from agent interactions
- **Map agent messages** to Docent message format
- **Include scratchpad content** as internal reasoning metadata
- **Ingest all negotiation sessions** with appropriate metadata tags

### 5. Analysis and Exploration
- **Use Docent web UI** to explore negotiation patterns
- **Compare performance** across different agent strategies
- **Analyze decision-making patterns** in scratchpad data
- **Track deal evolution** and convergence patterns
- **Generate insights** on negotiation effectiveness

### 6. Validation and Testing
- **Verify data integrity** in Docent platform
- **Test querying and filtering** capabilities
- **Ensure all metadata** is properly captured
- **Validate that insights** match expected patterns from raw data

## Data Structure Overview

### Agent Configuration
- Mayor: cooperative strategy, gpt-4.1-mini-2025-04-14
- Other cities: cooperative strategy, gpt-4.1-mini-2025-04-14
- Local Labour Union: cooperative strategy, gpt-4.1-mini-2025-04-14
- SportCo: greedy strategy, gpt-4.1-mini-2025-04-14
- Department of Tourism: greedy strategy, gpt-4.1-mini-2025-04-14
- Environmental League: greedy strategy, gpt-4.1-mini-2025-04-14

### Trajectory Data Features
- **Rounds**: Sequential negotiation rounds with agent interactions
- **Deals**: Structured proposals with format A1,B1,C4,D1,E5
- **Scratchpad**: Internal reasoning and calculation processes
- **Public answers**: External negotiation statements
- **Plans**: Strategic planning for future rounds

## Expected Outcomes
- Comprehensive analysis of multi-agent negotiation dynamics
- Insights into cooperative vs greedy strategy effectiveness
- Understanding of deal convergence patterns
- Evaluation of reasoning quality in scratchpad data
- Performance metrics across different agent roles