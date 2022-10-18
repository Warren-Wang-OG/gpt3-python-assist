# GPT-3 Prompting with Ability to Get Python Assistance When Responding

## Last updated: 10/17/2022

### Inspired by this tweet: https://twitter.com/goodside/status/1581805503897735168

The idea is that you want to do Q&A with GPT3, and what if the question is too hard for GPT-3 to answer? Well, if the user is reasonably minded, you can get GPT-3 to generate Python code that would compute the answer you are looking for, and then regurgitate that back to you.

Taking the idea from the tweet linked above, I modified the prompt shown in the screenshots to try to get GPT-3 to answer questions and produce short python scripts that could be immediately run, if the question cannot be immediately answered by GPT-3. The user will be prompted to double check the generated Python code to confirm if it is safe to run as a subprocess. If it is not or you immediately see that it won't work, you can abort. If you want to proceed, you can and it will run. The output (should be printed as coded by GPT-3) will be saved and written back to the prompt file. Then, a second GPT-3 query will be made to answer the original question given the code output just run. 

Process:
0. Set up `.env`, a template is provided. 
1. Set up a `conda` or whatever python env you want with at least the `openai` package
1. Set up question in prompt file.
2. Run `main.py` 

Short Demo:
https://youtu.be/c2e6_6Ex6vE