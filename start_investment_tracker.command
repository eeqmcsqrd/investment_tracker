#!/bin/bash
cd /Users/io/Downloads/investment_tracker
nohup streamlit run app_enhanced.py &
nohup python3 auto_sync.py --daemon &
