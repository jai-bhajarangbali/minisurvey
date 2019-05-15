from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class surveys(models.Model):
    user_id = models.ForeignKey(User, on_delete = models.CASCADE)
    name = models.CharField(max_length = 250, unique = True)
    published = models.BooleanField(default = False)
    private = models.BooleanField(default = False)



class questions(models.Model):
    survey_id = models.ForeignKey(surveys, on_delete = models.CASCADE)
    qtn = models.CharField(max_length = 1000)#, unique = True)
    o1 = models.CharField(max_length = 250)
    o2 = models.CharField(max_length=250)
    o3 = models.CharField(max_length = 250)
    o4 = models.CharField(max_length=250)

    '''
    class Meta:
        unique_together = ('survey_id','qtn')
    '''


class answers(models.Model):
    user_id = models.ForeignKey(User, on_delete = models.CASCADE)
    qtn_id = models.ForeignKey(questions , on_delete = models.CASCADE)
    ans = models.IntegerField()

    class Meta:
        unique_together = ('user_id','qtn_id')



class submissions(models.Model):
    user_id = models.ForeignKey(User, on_delete = models.CASCADE)
    survey_id = models.ForeignKey(surveys, on_delete = models.CASCADE)




class privatedetails(models.Model):
    survey_id = models.ForeignKey(surveys, on_delete = models.CASCADE)
    password = models.CharField(max_length = 50)

