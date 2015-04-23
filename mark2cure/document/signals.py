from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import Document, Pubtator

from mark2cure.document.tasks import get_pubtator_response

from datetime import datetime, timedelta
import requests


@receiver(post_save, sender=Pubtator)
def pubtator_post_save(sender, instance, created, **kwargs):
    '''
        When a new Pubtator model is created,
        start fetching it's content
    '''
    pubtator = instance

    if created:
        # Make response to post job to pubtator
        payload = {'content-type': 'text/xml'}
        writer = pubtator.document.as_writer()
        data = str(writer)
        url = 'http://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/RESTful/tmTool.cgi/{api_ann}/Submit/'.format(api_ann=pubtator.kind)
        response = requests.post(url, data=data, params=payload)
        pubtator.session_id = response.content
        pubtator.save()

        get_pubtator_response.apply_async(
            args=[pubtator.pk, data, payload, 0],
        )

