from django.db import models
from accounts.models import ParentModel,User

# Create your models here.

# session member model
class SessionMember(ParentModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    permission = models.JSONField(default=dict, null=True, blank=True)
    
    def __str__(self):
        return self.user.email
    
# session model
class Session(ParentModel):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    session_name = models.CharField(max_length=100, null=True, blank=True)
    members = models.ManyToManyField(SessionMember, related_name="members",null=True,blank=True)

# document model
class Document(ParentModel):
    type = models.CharField(max_length=50)
    title = models.CharField(max_length=100)
    pdf_file = models.FileField(upload_to='documents/')
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)

    
    def __str__(self):
        return self.title
    
# youtube  model
class Youtube(ParentModel):
    type = models.CharField(max_length=50,null=True,blank=True)
    title = models.CharField(max_length=100)
    link = models.CharField(max_length=100)
    text = models.TextField()
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.title

# youtube summery model
class YoutubeSummery(ParentModel):
    youtube = models.ForeignKey(Youtube, on_delete=models.CASCADE)
    summery = models.TextField()
    
    def __str__(self):
        return self.youtube.title
    
# knowledgeBase model
class TextSummery(ParentModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    text= models.TextField()
    summery = models.TextField()

class KnowledgeBase(ParentModel):
    type = models.CharField(max_length=50)
    object_id = models.IntegerField()
    page_no = models.IntegerField()
    text = models.TextField()
    vector = models.JSONField(default=dict, null=True, blank=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    

#  message model
class Message(ParentModel):
    question = models.CharField(max_length=500)
    answer = models.TextField()
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.question
    
# memoryKnowledge model
class MemoryKnowledge(ParentModel):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    knowledge = models.ManyToManyField(KnowledgeBase,blank=True)
    
    def __str__(self):
        return self.id

# note model
class Note(ParentModel):
    title = models.CharField(max_length=100)
    body = models.TextField()
    permission = models.JSONField(default=dict, null=True, blank=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.title
    
