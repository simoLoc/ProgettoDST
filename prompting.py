import lmstudio as lms
from openai import OpenAI
import json

# Carica il file JSON
with open("dataset\prova.json", "r", encoding="ISO-8859-1") as f:
    dataset = json.load(f)


model = lms.llm("smollm2-1.7b-instruct")

# Usando l'API gpt4-all
# Token esaurito (DA MODIFICARE)
# client = OpenAI(api_key="g4a-bKeS8JvQiSrnUFyIKKJrYcZNHbuDvNv75pv", base_url="https://api.gpt4-all.xyz/v1")

# def get_response(prompt):
#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[{"role": "user", "content": prompt}],
#         stream=False,
#         # n = 3
#     )

#     return response

for entry in dataset:
    # Mappa i campi del JSON ai campi del prompt
    trigger_channel = entry["trigger_channel"]
    trigger_title = entry["trigger_title"]
    trigger_fields = entry["trigger_fields"]
    action_channel = entry["action_channel"]
    action_title = entry["action_title"]
    action_fields = entry["action_fields"]


    prompt_rules ="""Trigger Action Rules refers to an event-based system. When a specific event occurs, it triggers a predefined action. This helps connect different services so they can work together without manual effort.Trigger Action Rules refers to an event-based system. When a specific event occurs, it triggers a predefined action. This helps connect different services so they can work together without manual effort.
    The trigger-action rule is divided into two subparts, trigger and action, both containing channel, title and fields.
    The key concepts are:
    - trigger_channel: an entity providing various services.
    - trigger_title: a specific functionality or service offered by a trigger_channel.
    - trigger_field: predefined parameters required by a trigger_title to configure the exact behaviour of the event. Each trigger_field has a name and value and may be mandatory or optional.
    - action_channel: the entity that provides the action service resulting from the trigger.
    - action_title: a specific action_channel functionality that is executed when the trigger is activated.
    - action_fields: parameters required to define the behaviour of the action executed by the action_title.
    When the trigger is activated, the system automatically executes the associated action.

    The activation and action rules follow this natural sequence of steps:
    Users choose a channel and select a title.
    If the title requires parameters, these are specified in fields.
    As a result, each level depends on the previous one:
    Titles depend on the specified channels.
    Fields depend on the specified titles and channels.
    Recalling that the trigger-action rule is divided into two subparts, trigger and action, so this natural sequence of steps can begin with the action or the trigger. This choice is defined by the first user statement.

    Each user utterance is associated with a belief state. The belief state is the current state of the frame completion that tracks the progress of the conversation. It contains the various fields of the trigger-action rule, using a frame structure. Here is an example:
    Frame(trigger_channel = ''; trigger_title = ''; action_channel = 'Facebook'; action_title = 'Publish a post'; trigger_fields = ''; action_fields = '')
    """

    prompt_exception = """The steps described above are the normal step sequence. In some cases it may occur:
    1. The utterances may already contain information on trigger-action fields that should be completed in the following steps
        For instance:
        - User: I would like every time I post a photo on Facebook, it is automatically shared on Twitter.
        Frame(trigger_channel = 'Facebook'; trigger_title = ''; trigger_fields = ''; action_channel = 'Twitter'; action_title = '';  action_fields = '')
        In this case, both the trigger_channel and the action_channel can be completed.
    2. The trigger_fields and action_fields can be empty. Therefore, in the output conversation you should not generate utterances that complete these fields. 
    """


    prompt_example = """## INPUT
    # Trigger-action rules
    trigger_channel: Facebook
    trigger_title: New photo post by you with hashtag
    trigger_fields: Hashtag (Text input)
    action_channel: Twitter
    action_title: Post a tweet with image
    action_fields: Tweet (Text input), Photo URL (Text input > Photo)


    ## OUTPUT
    # Conversation
    Frame(trigger_channel = ''; trigger_title = ''; trigger_fields = ''; action_channel = ''; action_title = '';  action_fields = '')
    - User: I would like that every time I post a photo with a certain hashtag, it is automatically shared on Twitter.
        Frame(trigger_channel = ''; trigger_title = 'New photo post by you with hashtag'; trigger_fields = ''; action_channel = 'Twitter'; action_title = ''; action_fields = '')
    - System: Got it! I can help you set up this rule. Which platform do you want to use to track posts with hashtags?
    - User: I use Facebook.
        Frame(trigger_channel = 'Facebook'; trigger_title = 'New photo post by you with hashtag'; trigger_fields = ''; action_channel = 'Twitter'; action_title = ''; action_fields = '')
    - System: Good choice. What should I be looking for in your Facebook posts to enable sharing on Twitter? For example, would you like me to check a specific hashtag?
    - User: Yes, I would like you to check the hashtag #frase_poderosa.
        Frame(trigger_channel = 'Facebook'; trigger_title = 'New photo post by you with hashtag'; trigger_fields = 'Hashtag (Text input)'; action_channel = 'Twitter'; action_title = ''; action_fields = '')
    - System: Perfect, I will monitor your Facebook posts with the hashtag #frase_poderosa. On Twitter, would you like to share only the text of the post or also the associated photo?
    - User: I would like to share both the text and the photo.
        Frame(trigger_channel = 'Facebook'; trigger_title = 'New photo post by you with hashtag'; trigger_fields = 'Hashtag (Text input)'; action_channel = 'Twitter'; action_title = 'Post a tweet with image'; action_fields = '')
    - System: Fine, I will share both the text and the photo. What should I write in the tweet? Do you want to use the same text as the Facebook post or add something specific?
    - User: Write 'New Facebook post: {text of post}'.
        Frame(trigger_channel = 'Facebook'; trigger_title = 'New photo post by you with hashtag'; trigger_fields = 'Hashtag (Text input)'; action_channel = 'Twitter'; action_title = 'Post a tweet with image'; action_fields = 'Tweet (Text input), Photo URL (Text input > Photo)')
    - System: Great, the tweet will be 'New Facebook post: {text of post}'. The photo will automatically be added to the tweet. Is there anything else you want to specify?
    - User: No, that's fine.
        Frame(trigger_channel = 'Facebook'; trigger_title = 'New photo post by you with hashtag'; trigger_fields = 'Hashtag (Text input)'; action_channel = 'Twitter'; action_title = 'Post a tweet with image'; action_fields = 'Tweet (Text input), Photo URL (Text input > Photo)')
    - System: Perfect, the rule has been set up! Whenever you post a photo on Facebook with the hashtag #frase_poderosa, it will automatically be shared on Twitter with the text 'New Facebook post: {post text}' and the attached photo.

    """

    prompt_completo = f"""Generate an example of an incremental conversation between user and system. In such a conversation, the goal is to complete one field of the action activation rule at each step. The trigger-action rule on which to generate the conversation is provided as input.
    The system must ask questions that are related to and consistent with the completion of the various fields in the activation rule. Conversely, the user must provide the values needed to complete the fields.
    The output must contain the utterances between the user and the system, as well as the temporary belief state for each user utterance.


    ### RULES 
    {prompt_rules}

    ## EXCEPTION RULES
    {prompt_exception}

    ### EXAMPLE TRIGGER-ACTION RULES
    {prompt_example}

    ---

    ### CURRENT INPUT
    # Trigger-action rules
    trigger_channel: {trigger_channel}
    trigger_title: {trigger_title}
    trigger_fields: {trigger_fields}
    action_channel: {action_channel}
    action_title: {action_title}
    action_fields: {action_fields}


    By processing the current input, it generates an incremental conversation, between the system and the user, and the temporary belief state for each user utterance. At the end of Conversation, the output contains also the Final Belief State. The purpose of this conversation is to fill in the fields of the trigger-action rule at each step, this must be done using the trigger-action rule provided as input.
    The system must not explicitly ask for that field to be completed. The belief state fields must contain exactly the fields of the input trigger-action rule. Utterances must not refer to the fields of the trigger-action rule. Avoid generating the same statements if the fields of the trigger-action rule have already been processed. 
    """

    # try:
    #         # print('Producing response...')
    #         response = get_response(prompt_completo)
    #         # print("Pipeline executed successfully.")
    # except Exception as e:
    #         print("Error occurred:")
    #         print(e)

    # new_edus = [c.message.content.strip("'") for c in response.choices]

    # print(new_edus)

    result = model.respond(prompt_completo)

    print(result)