class PromptRatingResponse():
    def __init__(self, prompt_prosona, prompt_question, prompt_addtext, out_text_rd, ret_answer, user_rating_radio, user_rating_comments, user_email):
        self.Prompt_Persona = prompt_prosona
        self.Prompt_Question = prompt_question
        self.Prompt_AddText = prompt_addtext
        self.RelevantDocumentsText = out_text_rd
        self.retAnswer = ret_answer
        self.userRatingRadio = user_rating_radio
        self.userRatingComments = user_rating_comments
        self.comments = user_rating_comments
        self.user_email = user_email

class Choices():
    def __init__(self, context):
        self.Zero = 0