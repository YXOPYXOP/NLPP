import time
import openai
from prompt import read_prompt, format_response, get_failed
import pickle
import sys
from concurrent.futures import ThreadPoolExecutor

openai.api_key = "your_key_here"
openai.api_version = "2023-07-01-preview"

responses = []
failed_list = []

def post_prompt(prompt):
    message_log = [
        {"role": "user", "content": prompt['prompt']},
    ]
    if prompt['length'] > 9:
        t = 0.3
    else:
        t = 0.7
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=message_log,  # The conversation history up to this point, as a list of dictionaries
            # max_tokens=800,        # The maximum number of tokens (words or subwords) in the generated response
            stop=None,  # The stopping sequence for the generated response, if any (not used here)
            temperature=t,  # The "creativity" of the generated response (higher temperature = more creative)
        )
        response = response["choices"][0]["message"]['content']
        print(prompt['file'])
        print(response)
        formatted, length = format_response(response)
        assert length - 1 == prompt['length']
        responses.append({'file': prompt['file'], 'response': formatted})
    except AssertionError:
        message_log.append({"role": "assistant", "content": formatted})
        message_log.append({"role": "user", "content": "You answer is wrong. You forget some words."})
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=message_log,  # The conversation history up to this point, as a list of dictionaries
                # max_tokens=800,        # The maximum number of tokens (words or subwords) in the generated response
                stop=None,  # The stopping sequence for the generated response, if any (not used here)
                temperature=t,  # The "creativity" of the generated response (higher temperature = more creative)
            )
            response = response["choices"][0]["message"]['content']
            print(prompt['file'])
            print(response)
            formatted, length = format_response(response)
            assert length - 1 == prompt['length']
            responses.append({'file': prompt['file'], 'response': formatted})
        except:
            print(sys.exc_info())
            print(f"Failed in {prompt['file']}")
            failed_list.append(prompt['file'])
    except:
        print(sys.exc_info())
        print(f"Failed in {prompt['file']}")
        failed_list.append(prompt['file'])
    finally:
        # time.sleep(1)
        pass
