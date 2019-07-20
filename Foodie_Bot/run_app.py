from rasa_core.channels import HttpInputChannel
from rasa_core.agent import Agent
from rasa_core.interpreter import RasaNLUInterpreter
from rasa_slack_connector import SlackInput


nlu_interpreter = RasaNLUInterpreter('./models/nlu/default/restaurantnlu')
agent = Agent.load('./models/dialogue', interpreter = nlu_interpreter)

input_channel = SlackInput('xoxp-602549253265-612738563574-612416239447-9c25dfb496f1c779b86fd45a3dcb54b8', #app verification token
							'xoxb-602549253265-608801788853-qIJBg3CYt8fFCP1Dip3ZiK42', # bot verification token
							'YyIuEVvNlE3kdYy5rdKCMCwk', # slack verification token
							True)

agent.handle_channel(HttpInputChannel(5004, '/', input_channel))