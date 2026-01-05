#!/bin/bash

mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"vishwaksen21@example.com\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCORS = false\n\
port = \$PORT\n\
\n\
[browser]\n\
gatherUsageStats = false\n\
" > ~/.streamlit/config.toml
