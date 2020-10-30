from django.db import models
from django.shortcuts import reverse
from django.contrib.auth.models import User
from .utils import get_random_code
from django.template.defaultfilters import slugify
from django.db.models import Q

# models here.

class ProfileManager(models.Manager):
    def get_all_profiles_to_invite(self, sender):
        profiles = Profile.objects.all().exclude(user=sender)
        profile = Profile.objects.get(user=sender)
        qs = Relationship.objects.filter(Q(sender=profile) | Q(receiver=profile))
        print(qs)
        print("#########")

        accepted = set([])
        for rel in qs:
            if rel.status == 'accepted':
                accepted.add(rel.receiver)
                accepted.add(rel.sender)
        print(accepted)
        print("#########")

        available = [profile for profile in profiles if profile not in accepted]
        print(available)
        print("#########")
        return available
        

    def get_all_profiles(self, me):
        profiles = Profile.objects.all().exclude(user=me)
        return profiles
    

class Profile(models.Model):
    first_name = models.CharField(max_length=200,blank = True)
    last_name = models.CharField(max_length=100,blank=True)
    user = models.OneToOneField(User ,on_delete=models.CASCADE)
    bio = models.TextField(default="User has no Bio!",max_length =500)
    email = models.EmailField(max_length= 200,blank = True)
    country = models.CharField(max_length= 200,blank = True)
    avatar = models.ImageField(default='avatar.png', upload_to ='avatars/')
    friends = models.ManyToManyField(User , blank=True , related_name ='friends')
    slug = models.SlugField(unique=True , blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    
    objects = ProfileManager()

    def get_friends(self):
        return self.friends.all()
    
    def get_friends_no(self):
        return self.friends.all().count()

    def get_posts_no(self):
        return self.posts.all().count()

    def get_all_authors_posts(self):
        return self.posts.all()

    def get_likes_given(self):
        likes = self.like_set.all()
        total_liked = 0
        for item in likes:
            if item.value=='Like':
                total_liked += 1
        return total_liked

    def get_likes_recieved_no(self):
        posts=self.posts.all()
        total_liked=0
        for item in posts:
            total_liked +=item.liked.all().count()
        return total_liked
 
    def __str__(self):
        return f"{self.user.username}-{self.created.strftime('%d-%m-%Y')}"

    def save(self,*args,**kwargs):
        ex=False
        if self.first_name and self.last_name: 
            to_slug = slugify(str(self.first_name) + " " + str(self.last_name))
            ex = Profile.objects.filter(slug=to_slug).exists()
            while ex:
                to_slug = slugify(to_slug + " " + str(get_random_code()))
                ex = Profile.objects.filter(slug=to_slug).exists()
        else:
             to_slug = str(self.user)
        self.slug = to_slug
        super().save(*args, **kwargs)


STATUS_CHOICES=(
    ('send','send'),
    ('accepted','accepted')
)

class RelationshipManager(models.Manager):
    def invitations_received(self,receiver):
        qs = Relationship.objects.filter(receiver=receiver, status= 'send')
        return qs
    
class Relationship(models.Model):
    sender = models.ForeignKey(Profile , on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(Profile , on_delete=models.CASCADE, related_name='receiver')
    status = models.CharField(max_length=9 ,choices=STATUS_CHOICES)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = RelationshipManager()

    def __str__(self):
        return f"{self.sender}-{self.receiver}-{self.status}"
