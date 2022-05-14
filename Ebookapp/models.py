#django packages
from django.db import models
#converter packages
from pdf2image import convert_from_path
import os , re 
import pytesseract
from PIL import Image
#database packages
import pymongo 
from bson.objectid import ObjectId
from dotenv import load_dotenv

# environment variables
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
load_dotenv()
DB_KEY = os.getenv('SECRET_KEY')

class db_Connection():
    def __init__(self) -> None:
        super().__init__()
        # Create mongodb client
        self.client = pymongo.MongoClient(DB_KEY)
        self.db = self.client["myFirstDatabase"]

    #list all databases in client    
    def getDB_names(self):
        dblist  = self.client.list_database_names() 
        return dblist

    #get Books collection from database
    def getBooksDB(self):
        collections = self.db["books"]
        return collections
    
    #get TextBooks collection from database 
    def getTextBookDB(self):
        collections = self.db["TextBooks"]
        return collections

    #list all textbook Ids
    def getBookIds(self):
        
        bookIds = {'bookId':[]}
        collection = db_Connection().getTextBookDB()
        doc = collection.find({},{'BookId':1})
        for id in doc :
            bookIds['bookId'].append(id['BookId'])
        return bookIds

    #get book url filterd by book id from database
    def getBookUrl(self , bookid:str):
        bookID = bookid 

        query = {"_id": ObjectId(bookID)}
        collection = db_Connection().getBooksDB()
        doc = collection.find(query)

        for item in doc:
            bookURL = item['pdf']
        return bookURL

    #get textbook if exists
    def getTextBook(self, bookId):
        bookid = bookId
        query = {'BookId': bookid}
        collection = db_Connection().getTextBookDB()
        doc = collection.find(query)
        for item in doc :
            bid = item["BookId"]
            return bid
        return None
    
    #get textbook page 
    def getTextBookPage(self, bookId, PageNumper):

        bookid = bookId
        query = {'BookId': bookid}
        collection = db_Connection().getTextBookDB()
        doc = collection.find(query)
        for item in doc :
            page = item["Page"].get(str(PageNumper))
        return page
        
    #add textbook to database and return inserted_id 
    def addTextBook(self, document:dict):
        Doc = document
        collection = db_Connection().getTextBookDB()
        return collection.insert_one(Doc)

    #delete textBook from database
    def deleteTextBook(self, bookId):
        bookid = bookId
        query = {'BookId': bookid}
        collection = db_Connection().getTextBookDB()
        return collection.delete_one(query)


class Downloader():
    def __init__(self) -> None:
        self.base = os.getcwd()
        self.booksrepo = os.path.join(self.base+r'\Ebookapp\bookPDFs')
    def bookDownloader(self,bookURL):
        if not os.path.exists (self.booksrepo):
            os.makedirs(self.booksrepo)
            
        os.chdir(self.booksrepo)
        os.system(f'wget {bookURL} ')
        os.chdir(self.base)
        bookName = str(bookURL).split('/')[-1]

        return bookName

class PDfConverter():
    def __init__(self) -> None:
        self.base = os.getcwd()        

    def ocr(self, imgPath)  :   
        try:
            text = pytesseract.image_to_string(Image.open(imgPath),lang='eng' ) # Timeout after 2 seconds
        except RuntimeError as timeout_error:
            # Tesseract processing is terminated
            pass
        return text
                
        
    def convert2Text(self, PdfPath, BookID ):
        bookId = BookID.split('.')[0]
        textDict = {"BookId":bookId, "Page":{}}
        outputdir = os.path.join(self.base + r"\Ebookapp\bookIMGs\\")
        if not os.path.exists (outputdir):
            os.makedirs(outputdir)
        #convert the pdf to imgs
        pages = convert_from_path(PdfPath, 200)
        counter = 1
        for page in pages:
            #convert every page to img
            filePath = os.path.join(outputdir,f"{bookId +'_'+str(counter)}.jpg")
            page.save(filePath, "JPEG")

            #convert img to text by OCR
            imgText = PDfConverter().ocr(filePath) 
            #filter text from special characters
            filterdText = re.sub('[^A-Za-z0-9.,]+ ', '   ', imgText ).replace("\n"," ")
            #save the text in dictionary form
            pageDict = {str(counter):filterdText}
            textDict["Page"].update(pageDict)

            print(f"page {counter} ... ✔") # monitoring ###########################################
            counter += 1
        return textDict
