import openai
import os
from dotenv import load_dotenv
import subprocess

load_dotenv()

NUM_TRIES = 5

openai.api_key = os.getenv("GPT3_OPENAI_API_KEY")

PROMPT_FILENAME = os.getenv("PROMPT_FILENAME")
PYTHON_BIN = os.getenv("PYTHON_BIN")
SCRIPT_FILEPATH = os.getenv("SCRIPT_FILEPATH")

# trying to get it to write an entire python script
GPT3_SETTINGS = { 
    "engine": "text-davinci-002",
    "temperature": 0.0,
    "max_tokens": 500,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,
    "stop": ["Question:", "Out:", "Err:"]
}

def gen_gpt3(usr_msg : str, settings_dict: dict = GPT3_SETTINGS) -> str:
    '''
    retrieves a GPT3 response given a string input and a dictionary containing the settings to use
    returns the response str
    '''
    response = openai.Completion.create(
        engine = settings_dict["engine"],
        prompt = usr_msg,
                temperature = settings_dict["temperature"],
                max_tokens = settings_dict["max_tokens"],
                top_p = settings_dict["top_p"],
                frequency_penalty = settings_dict["frequency_penalty"],
                presence_penalty = settings_dict["presence_penalty"],
                stop = settings_dict["stop"]
    )

    return response.choices[0].text

def gen_gpt3_from_prompt():
    '''
    return 0 if good and want to stay
    return 1 if want to exit immediately
    '''

    with open(PROMPT_FILENAME, "r+") as f:
        prompt = f.read()
        response = gen_gpt3(prompt)
        f.write(response)

    # check to see if we need to run python code...
    lines, status = check_if_need_run_python_code()
    if not status:
        return 1

    # need to run python code, get the python script
    lines = lines[:-1] # ignore the last ```
    python_script = []
    for i in range(len(lines)-1, 0, -1):
        if(lines[i].strip("\n") != "```"):
            line = lines[i]
            python_script.insert(0, line)
        else:
            break
    full_python_script = "".join(python_script)
    # ask user if python code looks ok to run ....
    print(f"This is the full script:\n\n{full_python_script}")
    tmp = input("Does this look ok to run? [y/n]")
    if( tmp.lower() == 'n' ):
        print("Aborting running the python code.")
        return 1
    # run the code and append the output to the file with no newline
    with open("runme.py", "w") as f:
        f.write(full_python_script)
    # run the code
    print("Running a subprocess with the code...")
    cmd = f"{PYTHON_BIN} {SCRIPT_FILEPATH} 1> out.txt 2> err.txt"
    try:
        subprocess.run(cmd, shell=True)
    except Exception as e:
        print(f"Got the following error trying to run subprocess: {e}")
        return 1
    return 0

def check_if_need_run_python_code():
     # check to see if we need to run python code...
    lines = []
    with open(PROMPT_FILENAME, "r+") as f:
        lines = f.readlines()

        # ignore final blank line if exists
        if lines[-1] == "":
            lines = lines[:-1]

        if lines[-1].strip("\n") != "```":
            # don't need to run python code, just return
            return [], False

    return lines, True

def check_error():
    '''returns True if there was an error, False otherwise
    '''
    err_flag = False
    with open("err.txt", "r") as f:
        f_contents = f.read()
        if(f_contents == ""):
            # no err
            pass
        else:
            # yes err, write this to the output file...
            err_flag = True

    return err_flag

def cleanup():
    # deletes specific files
    names = ["out.txt", "runme.py", "err.txt"]
    for file in os.listdir("."):
        if file in names:
            os.unlink(file)

def answer_one_question():
    # generate the gpt3 response
    if(gen_gpt3_from_prompt() == 1):
        cleanup()
        return

    # check for an error
    if not check_error():
        # read the output from out.txt, write it back to the prompt file
        ans = ""
        with open("out.txt", "r") as f:
            ans = f.read()

        cleanup()

        with open(PROMPT_FILENAME, "a") as f:
            f.write(f"Out: {ans}")

        # generate one more response to finish things off
        if(gen_gpt3_from_prompt() == 1):
            cleanup()
            return
    else:
        # we had an error....
        for _ in range(NUM_TRIES):
            # every time we error out, increase the temperature...it needs
            # more creativity to solve this problem xD
            GPT3_SETTINGS["temperature"] += 0.10

            # read the error from err.txt, write it back to the prompt file
            err = ""
            with open("err.txt", "r") as f:
                err = f.read()
            
            cleanup()

            with open(PROMPT_FILENAME, "a") as f:
                f.write(f"Err: {err}")

            # generate response
            if(gen_gpt3_from_prompt() == 1):
                cleanup()
                return

            # check if had error, if so, repeat loop
            if not check_error():
                # cleanup and leave
                cleanup()
                return
        print("OUT OF TRIES!!!")
        cleanup()

    print("end of answer_one_question")

answer_one_question()