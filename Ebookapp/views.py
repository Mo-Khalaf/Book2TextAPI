#django packages
from django.shortcuts import render
#restframework packages
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
#models packages
from .models import *
from .serializers import BookSerializer, BookTextSerializer
from Ebookapp import serializers

class BookConverter(APIView):
    def __init__(self, ) -> None:
        super().__init__()
        self.dbConnection =  db_Connection()
        self.base = os.getcwd()

    def post(self, request):
        
        bookId = self.request.data['bookId']
        serializer = BookSerializer(data=request.data)

        if serializer.is_valid() and self.dbConnection.getTextBook(bookId) == None :
            
            bookURL = self.dbConnection.getBookUrl(bookId)
            bookName = Downloader().bookDownloader(bookURL)
            bookPath = os.path.join(os.getcwd()+rf'\Ebookapp\bookPDFs\{bookName}')
            # convert to images 
            bookText = PDfConverter().convert2Text(bookPath, bookId)
            # insert bookText to db
            insertedDoc = self.dbConnection.addTextBook(bookText)
            try:
                # delete bookPdfs 
                os.remove(bookPath)
                # delete bookImgs
                bookImgsDir = os.path.join(self.base+ r'\Ebookapp\bookIMGs\\')
                for img in os.listdir(bookImgsDir):
                    imgPath = os.path.join(bookImgsDir+ img)
                    os.remove(imgPath)
            except:
                pass
            return Response(serializer.data,status=201)
        else :
            return Response(serializer.data,status=404 )
        # { "bookId":"" }  
    def get(self , request) : 
        bookIDs = self.dbConnection.getBookIds()
        return Response(bookIDs)


class BookText(APIView):
    def __init__(self) -> None:
        self.dbConnection =  db_Connection() 
    def post (self,request): 
        bookId = self.request.data['bookId']
        pageNumber = self.request.data['pageNumber']
        serializer = BookTextSerializer(data=request.data)
        if serializer.is_valid(): 
            pageText = self.dbConnection.getTextBookPage(bookId, pageNumber )
            return Response(pageText ,status=200) 
        else : 
            return Response(serializer.data,status=404 )
        # { "bookId":"","pageNumber":"" }
    def get(self,request) :
        bookIDs = self.dbConnection.getBookIds()
        return Response(bookIDs)
        
class DeleteBookText(APIView):
    def __init__(self) -> None: 
        self.dbConnection =  db_Connection()    
    def post (self, request):
        bookId = self.request.data['bookId']
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid() and self.dbConnection.getTextBook(bookId) != None :
            deletedBook = self.dbConnection.deleteTextBook(bookId)
            return Response(serializer.data, status=202)
        else: 
            return Response(serializer.data, status=204)
    def get(self , request) : 
        bookIDs = self.dbConnection.getBookIds()
        return Response(bookIDs)


