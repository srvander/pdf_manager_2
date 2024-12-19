import PyPDF2

def print_bookmarks(bookmarks, level=0):
    for bookmark in bookmarks:
        print('  ' * level + bookmark.title)
        if hasattr(bookmark, 'children'):
            print_bookmarks(bookmark.children(), level + 1)

def check_markers(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        if reader.outline:
            print("Bookmarks found:")
            print_bookmarks(reader.outline)
        else:
            print("No bookmarks found.")

# Example usage
pdf_path = 'pdf_merged_1.pdf'
pdf_path = input("Enter the path to the PDF file: ")
if not pdf_path.lower().endswith('.pdf'):
    print("Error: The file must be a PDF.")
else:
    check_markers(pdf_path)
check_markers(pdf_path)
