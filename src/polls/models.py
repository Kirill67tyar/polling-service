from django.db import models

"""
Poll
    owner
    title
    start_date
    end_date
    description
    created?
    
Question
    text
    type_q
    
Answer
    question (ForeignKey - Question)
    respondent (ForeignKey - User)
    
"""
