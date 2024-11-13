# ollama-cli-oracle
Use ollama locally plus search engine to check online real time information when needed.

# how to use: 
1. Run this command to install the search engine dependency + ollama:
```
pip install git+https://github.com/tasos-py/Search-Engines-Scraper ollama
```
2. Start the python script on cmd with arguments: 
- --model (Name of the model available on ollama library to be used (default: llama3.2))
- --search (Activate if you want to have an oracle to search the internet for information . (default: None), google, bing, yahoo, duckduckgo, brave, etc)

Example:
```
python ollama-cli-oracle.py --search='google' 
```
![image](https://github.com/user-attachments/assets/09423e76-2797-44fa-a8e6-c2ff025f3e25)


Then, just chat.

Enjoy.

# Thanks to:
- Tazos-py for the great search engine plugin. (tasos-py/Search-Engines-Scraper)
- Ollama for the great local LLM software.
