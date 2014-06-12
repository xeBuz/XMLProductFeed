#!/usr/bin/env python3
# coding: utf-8

from db import DatabaseManager
import xml.etree.ElementTree as ET
import argparse

parser = argparse.ArgumentParser(description='XML Product Feed for Olapic')
parser.add_argument('-i', '--input', action='store', dest='xml_file', default='example-product-feed.xml', help="XML file. Default: example-product-feed.xml")
parser.add_argument('-o', '--output', action='store', dest='sqlite_file', default='olapicPorductFeed.sqlite', help="SQLite file. Default: olapicPorductFeed.sqlite")
parser.add_argument('--keep', action='store_true', dest='keep', help="Keep existing database")
args = parser.parse_args()


def main():
    db = DatabaseManager(args.sqlite_file, args.keep)
    db.create_db()

    tree = ET.parse(args.xml_file)
    root = tree.getroot()

    categories = root.find('Categories')
    products = root.find('Products')

    for category in categories:
        name = category.findtext('Name')
        category_id = category.findtext('CategoryUniqueID')
        parent_id = category.findtext('CategoryParentID')

        db.add_category(name, category_id, parent_id)
    db.commit()

    for product in products:
        name = product.findtext('Name')
        product_id = product.findtext('ProductUniqueID')
        url = product.findtext('ProductUrl')
        image = product.findtext('ImageUrl')
        description = product.findtext('Description')
        price = product.findtext('Price')
        stock = product.findtext('Stock')
        availability = product.findtext('Availability')
        color = product.findtext('Color')
        parent_id = product.findtext('ParentID')

        category = product.find('CategoriesID')
        category_id = category.findtext('CategoryID') if category else ''
        eans = product.find('EANs')
        ean = fix_str(eans.findtext('EAN')) if eans else ''
        isbns = product.find('ISBNs')
        isbn = fix_str(isbns.findtext('ISBN')) if isbns else ''
        upcs = product.find('UPCs')
        upc = upcs.findtext('UPC') if upcs else ''

        db.add_product(name, product_id, url, image, description, category_id, ean, isbn, price, stock, availability, color, parent_id, upc)
    db.commit()


def fix_str(str):
    return str.strip('-').strip('~').strip()

if __name__ == '__main__':
    main()
