# Twitter Accounts management

For this particular project we'll be working specifically with account management. You'll need to build a few common views (registration, password reset, etc; all detailed below). It'll be particularly helpful to use [Class Based Views](https://docs.djangoproject.com/en/1.9/topics/class-based-views/) and [Model Forms](https://docs.djangoproject.com/en/1.9/topics/forms/modelforms/).

There's also a privileged view that will be accessibly only to users with the group _"Admin users"_ (as you can see in [this test](https://github.com/rmotr-group-projects/wdd-w2-twitter-accounts/blob/master/tests/test_accounts.py#L142)). Your life can be much easier if you take a look at `GroupRequiredMixin` from [Django Braces](http://django-braces.readthedocs.io/en/latest/access.html).

### Registration page

![image](https://cloud.githubusercontent.com/assets/872296/18180344/d01e2898-705c-11e6-8fab-28e3f00aa2f8.png)

### Change Password

![image](https://cloud.githubusercontent.com/assets/872296/18180367/ef964570-705c-11e6-95ed-c25dfc2d4399.png)

### Forgot Password

![image](https://cloud.githubusercontent.com/assets/872296/18180394/0e937664-705d-11e6-97dc-301147c3ec2c.png)

![image](https://cloud.githubusercontent.com/assets/872296/18180408/207f578a-705d-11e6-8729-da04f93835f6.png)

### Reset Password

**Important** Note the validation token

![image](https://cloud.githubusercontent.com/assets/872296/18180455/50858eea-705d-11e6-9687-f33cc5b38496.png)
