from django.db import models

class ExperienceLevelManager(models.Manager):
    def get_experience_floor(self):
        return self.all()[1].experience_required

    def get_experience_ceiling(self):
        return self.last().experience_required + 75