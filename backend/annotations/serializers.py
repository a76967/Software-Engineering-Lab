from rest_framework import serializers
from .models import Annotation

class AnnotationSerializer(serializers.ModelSerializer):
    project_id = serializers.IntegerField(
        source="project.id",
        read_only=True
    )
    class Meta:
        model = Annotation
        fields = '__all__'   # now includes project & project_id
        read_only_fields = ('id', 'created_at', 'updated_at', 'annotator')