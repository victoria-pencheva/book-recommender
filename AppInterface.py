import wx
import wx.grid as gridlib
from Database import DataBase
import numpy as np
import re
from Recommender import Recommender



db = DataBase()
r = Recommender()
open_results = []
book = ""
user_id = 0


class Home(wx.Panel):
    def __init__(self, parent):
        pnl = wx.Panel.__init__(self, parent)
        wx.StaticText(self, -1, "Welcome to the Book Recommender!\nTo get a recommendations add at least 1 book you have already read\nand how you would rate it from 1 to 5.\nYou can do that from the My Books section.\nWhenever you're ready with filling information,\nopen the Recommendations tab to get your recomendation. ", (450,100))
        self.bitmap = wx.Bitmap("book.jpg", wx.BITMAP_TYPE_JPEG)
        self.img = wx.StaticBitmap(self, 0, self.bitmap, pos = (300,250))

class AddBookDialog(wx.Dialog):
    def __init__(self, parent, title, book): 
      super(AddBookDialog, self).__init__(parent, title = title, size = (425,200)) 
      panel = wx.Panel(self)
      wx.StaticText(panel, label = "You have chosen " + str(book) + ".\n  Please rate it from 1 to 5.", pos = (75, 10))
      self.sc = wx.SpinCtrl(panel, value = "1", pos = (125, 60))
      self.add_book = wx.Button(panel, label = "Add to my books", pos = (90, 100))
      self.add_book.Bind(wx.EVT_BUTTON, self.add_book_to_database)

      self.sc.SetRange(1,5)

      self.Show(True)

    def add_book_to_database(self, event):
        db.fill_users_books_table(user_id, book, self.sc.GetValue())
        self.Close()

class SearchResults(wx.Dialog):
  def __init__(self, parent, title): 
      super(SearchResults, self).__init__(parent, title = title, size = (250,150)) 
      self.panel = wx.Panel(self)
      self.grid = gridlib.Grid(self)  

      global open_results

      self.grid.CreateGrid(len(open_results), 4)

      self.grid.Bind(gridlib.EVT_GRID_LABEL_LEFT_DCLICK, self.chosen)
      
      # self.grid.SetColLabelValue(0, "Cover")
      self.grid.SetColLabelValue(0, "Book title")
      self.grid.SetColLabelValue(1, "Author")
      self.grid.SetColLabelValue(2, "Year")
      self.grid.SetColLabelValue(3, "Genre")
   
      if open_results:
        num_rows = len(open_results)
        num_cols = len(open_results[0])

      else:
          wx.MessageBox('No results!', 'Error', wx.OK | wx.ICON_ERROR)
          return
      
      for i in range(num_rows):
            for j in range(num_cols):
                self.grid.SetCellValue(i, j, str(open_results[i][j]))

      for i in range(0,4):
          if i<2:
            self.grid.SetColSize(i, 400)
          else: 
            self.grid.SetColSize(i,150)

      sizer = wx.BoxSizer(wx.VERTICAL)

      sizer.Add(self.grid, 1, wx.EXPAND | wx.ALL, 10)
    
      self.SetSizer(sizer)
      self.SetSize(1250, 325)
      self.Center()
      
  def chosen(self, event):
      chosen_book = event.GetRow()
      global book
      book = self.grid.GetCellValue(chosen_book, 0)
      AddBookDialog(self, "Rate the book", book)
      
class MyBooks(wx.Panel):
    def __init__(self, parent):
        self.panel = wx.Panel.__init__(self, parent)

        self.search_ctrl = wx.SearchCtrl(self)
        self.search_ctrl.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.on_search)
        self.search_ctrl.Bind(wx.EVT_TEXT_ENTER, self.on_search)

        self.grid = gridlib.Grid(self) 

        self.grid.CreateGrid(25, 3)
        self.grid.SetColLabelValue(0, "Book title")
        self.grid.SetColLabelValue(1, "Author")
        self.grid.SetColLabelValue(2, "My rating")

        self.button = wx.Button(self, label = "Update books", size=(100, 10))
        self.button.Bind(wx.EVT_BUTTON, self.update)
        
        for i in range(0,3):
                if i<2:
                    self.grid.SetColSize(i, 400)
                else: 
                    self.grid.SetColSize(i,150)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.search_ctrl, 0, wx.EXPAND | wx.ALL,10)
        sizer.Add(self.button, 1, wx.EXPAND | wx.ALL, 10)
        sizer.Add(self.grid, 0, wx.EXPAND | wx.ALL,10)
       
        self.SetSizer(sizer)
     

    def update(self,e):
        my_books = db.get_all_users_books(user_id)
        

        if my_books:
            num_rows = len(my_books)
            num_cols = len(my_books[0])
      
            for i in range(0,len(my_books)):
                for j in range(0,3):
                    self.grid.SetCellValue(i, j, str(my_books[i][j]))

        self.Show(True)


    def on_search(self, event):
        self.result_from_search = self.search_ctrl.GetValue()
        global open_results
        open_results = db.find_author_and_book(self.result_from_search)
        SearchResults(self, "Search results").ShowModal()
  
class Recommendations(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.text = wx.StaticText(self, -1, "This is the book recommender page. Click on the button below to generate suggestions.", (20, 20))
        self.buton = wx.Button(self, label="Generate recommendations", pos=(20, 50))
        self.buton.Bind(wx.EVT_BUTTON, self.generate_recommendations)
        self.grid = gridlib.Grid(self) 
        
        self.grid.CreateGrid(25, 4)
        self.grid.SetColLabelValue(0, "Book title")
        self.grid.SetColLabelValue(1, "Author")
        self.grid.SetColLabelValue(2, "Year")
        self.grid.SetColLabelValue(3, "Genres")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.text, 0, wx.EXPAND | wx.ALL,10)
        sizer.Add(self.buton, 1, wx.EXPAND | wx.ALL, 10)
        sizer.Add(self.grid, 0, wx.EXPAND | wx.ALL,10)
       
        
        self.SetSizer(sizer)

        for i in range(0,4):
                if i<2:
                    self.grid.SetColSize(i, 400)
                else: 
                    self.grid.SetColSize(i,200)

    def generate_recommendations(self,e):
        global user_id

        books = db.get_books_by_user_id(user_id)

        if len(books) == 0:
            wx.MessageBox('You have to add at least one book to get a recommendation!', 'Error', wx.OK | wx.ICON_ERROR)
            return

        recommendation_len = 10
        recommendations_indices = r.give_recommendations(books)
        arr_np = np.zeros(shape=(recommendation_len,4), dtype=object)

        for i in range(recommendation_len):
            book_id = recommendations_indices[i]
            book_info = db.get_book_by_id(book_id)
            arr_np[i][0] = book_info[0][0]
            arr_np[i][1] = book_info[0][1]
            arr_np[i][2] = book_info[0][2]
            arr_np[i][3] = book_info[0][3]
        
    
        for i in range(len(arr_np)):
                title = arr_np[i][0]
                author = arr_np[i][1]
                year = arr_np[i][2]
                genres = arr_np[i][3]
                
                self.grid.SetCellValue(i, 0, title)
                self.grid.SetCellValue(i, 1, author)
                self.grid.SetCellValue(i, 2, str(year))
                self.grid.SetCellValue(i, 3, genres)
       


     

class MainFrame(wx.Frame):
    def __init__(self, user):
        global user_id
        user_id = user

        wx.Frame.__init__(self, None, title="Book Recommendation System")
        pnl = wx.Panel(self)
        self.nb = wx.Notebook(pnl)
 
        home = Home(self.nb)
        mybooks = MyBooks(self.nb)
        recomendations = Recommendations(self.nb)

        self.nb.AddPage(home, "Home")
        self.nb.AddPage(mybooks, "My books")
        self.nb.AddPage(recomendations, "Recommendations")
    
        sizer = wx.BoxSizer()
        sizer.Add(self.nb, 1, wx.EXPAND)
        pnl.SetSizer(sizer)

        self.SetSize((1300, 700))
        self.SetTitle("Book recommendations")
        self.Center()
        self.Show(True)
       
        self.Refresh()
        self.Layout()
