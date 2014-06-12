import sqlite3
import os


class DatabaseManager():
    def __init__(self, filename='olapicPorductFeed.sqlite', keep=False):
        self.filename = filename
        self.keep = keep

    def _validateRequired(self, dictionary):
        """ Check in a dictionary for empty strings """
        error = [k for k, v in dictionary.items() if v == '']
        if len(error):
            print(str(error) + " field(s) required")
            return False
        else:
            return True

    def _validateCategory(self, categoryUniqueID):
        """ Validate exiting CategoryID """
        if categoryUniqueID is '':
            return None
        c = self.conn.cursor()
        c.execute(
            '''SELECT CategoryUniqueID FROM categories WHERE categoryUniqueID=?''',
            (categoryUniqueID,)
        )
        category = c.fetchone()
        if not bool(category):
            print("CategoryUniqueID: " + str(categoryUniqueID) + " non-existent")
        return bool(category)

    def create_db(self):
        """ Create database structure and file if it needed """
        if not self.keep:
            if os.path.isfile(self.filename):
                os.remove(self.filename)

        self.conn = sqlite3.connect(self.filename)
        c = self.conn.cursor()

        c.execute('''
            CREATE TABLE IF NOT EXISTS "categories" ("Name" NOT NULL, "CategoryUniqueID" NOT NULL, "ParentID")
            ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS "products_upc" ("key" INTEGER PRIMARY KEY AUTOINCREMENT, "product_id", "value" NUMERIC )
            ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS "products" ("Name" NOT NULL, "ProductUniqueID" NOT NULL,
                                     "ProductUrl" NOT NULL, "ImageUrl" NOT NULL,
                                     "Description", "CategoryID", "EAN", "ISBN",
                                     "Price", "Stock", "Availability",
                                     "Color", "ParentID");
            ''')
        self.commit()

    def add_category(self, name, categoryUniqueID, parentID):
        """ Add a new category """
        validate = {'Name': name, 'CategoryUniqueID': categoryUniqueID}
        if not self._validateRequired(validate):
            return None

        c = self.conn.cursor()
        c.execute(
            'INSERT INTO categories VALUES (?, ?, ?)',
            (name, categoryUniqueID, parentID)
        )

    def add_product(self, name, productUniqueID, productUrl, imageUrl, description, categoryID, ean, isbn, price, stock, availability, color, parentID, upc):
        """ Add a new product """
        validate = {'Name': name, 'productUniqueID': productUniqueID, 'productUrl': productUrl, 'imageUrl': imageUrl}
        if not self._validateRequired(validate):
            return None
        if not self._validateCategory(categoryID):
            return None

        items = [name, productUniqueID, productUrl, imageUrl, description, categoryID, ean, isbn, price, stock, availability, color, parentID]
        c = self.conn.cursor()
        c.execute('INSERT INTO products VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (items))
        if upc:
            self.add_upc(productUniqueID, upc)

    def add_upc(self, productUniqueID, upc):
        """ Add a new UPC """
        c = self.conn.cursor()
        c.execute('INSERT INTO products_upc VALUES (?, ?, ?)',
            (None, productUniqueID, upc)
        )

    def commit(self):
        """ Commit the connection on demand for better performance """
        self.conn.commit()
