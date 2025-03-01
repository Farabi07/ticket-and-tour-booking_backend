# from distutils.command.upload import upload
import imp

from PIL import Image
from django.db import models
from django.conf import settings


# Create your models here.

class CMSMenu(models.Model):
    parent = models.ForeignKey('self', on_delete=models.PROTECT, related_name='children', null=True, blank=True)
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='cms/MenuImage/', null=True)
    note = models.TextField(null=True)
    position = models.IntegerField(unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)

    class Meta:
        verbose_name_plural = 'CMSMenus'
        ordering = ('position',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            max_width, max_height = 960, 550
            path = self.image.path
            image = Image.open(path)
            width, height = image.size
            if width > max_width or height > max_height:
                w_h = (960, 550)
                if width > height:
                    w_h = (960, 550)
                elif height > width:
                    w_h = (550, 960)
                    img = image.resize(w_h)
                    img.save(path)


class CMSMenuContent(models.Model):
    cms_menu = models.ForeignKey(CMSMenu, on_delete=models.PROTECT, related_name='cms_menu_contents')
    name = models.TextField()
    value = models.TextField(null=True, blank=True)
    name_link = models.URLField(max_length=1000, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)

    class Meta:
        verbose_name_plural = 'CMSMenuContents'
        ordering = ('-id',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class CMSMenuContentImage(models.Model):
    cms_menu = models.ForeignKey(CMSMenu, on_delete=models.PROTECT, related_name='cms_menu_content_images')
    head = models.CharField(max_length=500)
    image = models.ImageField(upload_to='cms/ContentImage/')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True,
                                   blank=True)

    class Meta:
        verbose_name_plural = 'CMSMenuContentImages'
        ordering = ('-id',)

    def __str__(self):
        return self.head

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
