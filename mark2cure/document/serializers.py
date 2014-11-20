from mark2cure.document.models import Annotation

from rest_framework import serializers


class AnnotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Annotation
        fields = ('text', 'start',)

