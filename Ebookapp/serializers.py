from unittest.util import _MAX_LENGTH
from rest_framework import serializers

class BookSerializer(serializers.Serializer):
    class Meta:
        BookId = serializers.CharField(max_length=20)  


class BookTextSerializer(serializers.Serializer) :
    class Meta: 
        bookID = serializers.CharField(max_length=20) 
        pageNumber = serializers.CharField(max_length=20)