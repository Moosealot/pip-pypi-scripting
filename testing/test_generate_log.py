import pytest
import json
import os
from datetime import datetime
from library_cli import Book, Library, CLIHandler


# =============================================================================
# TEST CLASS: Book Tests
# =============================================================================
class TestBook:
    """Test cases for the Book class."""
    
    def test_book_initialization(self):
        """Test that a book is created with correct attributes."""
        book = Book(title="The Great Gatsby", author="F. Scott Fitzgerald", 
                   isbn="978-0743273565")
        
        assert book.title == "The Great Gatsby"
        assert book.author == "F. Scott Fitzgerald"
        assert book.isbn == "978-0743273565"
        assert book.available == True
        assert book.added_date is not None
    
    def test_book_with_borrowed_status(self):
        """Test creating a book that is already borrowed."""
        book = Book(title="1984", author="George Orwell", 
                   isbn="978-0451524935", available=False)
        
        assert book.available == False
    
    def test_book_to_dict(self):
        """Test converting book to dictionary."""
        book = Book(title="To Kill a Mockingbird", author="Harper Lee", 
                   isbn="978-0061120084")
        
        book_dict = book.to_dict()
        
        assert book_dict['title'] == "To Kill a Mockingbird"
        assert book_dict['author'] == "Harper Lee"
        assert book_dict['isbn'] == "978-0061120084"
        assert book_dict['available'] == True
        assert 'added_date' in book_dict
    
    def test_book_from_dict(self):
        """Test creating book from dictionary."""
        book_data = {
            'title': "Pride and Prejudice",
            'author': "Jane Austen",
            'isbn': "978-0141439518",
            'available': False,
            'added_date': "2024-01-15 10:30"
        }
        
        book = Book.from_dict(book_data)
        
        assert book.title == "Pride and Prejudice"
        assert book.author == "Jane Austen"
        assert book.isbn == "978-0141439518"
        assert book.available == False
        assert book.added_date == "2024-01-15 10:30"
    
    def test_book_from_dict_default_available(self):
        """Test that available defaults to True when not in dict."""
        book_data = {
            'title': "The Catcher in the Rye",
            'author': "J.D. Salinger",
            'isbn': "978-0316769488"
        }
        
        book = Book.from_dict(book_data)
        
        assert book.available == True
    
    def test_book_string_representation(self):
        """Test the string representation of a book."""
        available_book = Book(title="Moby Dick", author="Herman Melville", 
                             isbn="978-0142437247", available=True)
        borrowed_book = Book(title="War and Peace", author="Leo Tolstoy", 
                            isbn="978-0140447934", available=False)
        
        assert "✓ Available" in str(available_book)
        assert "✗ Borrowed" in str(borrowed_book)
        assert "Moby Dick" in str(available_book)
        assert "Herman Melville" in str(available_book)


# =============================================================================
# TEST CLASS: Library Tests
# =============================================================================
class TestLibrary:
    """Test cases for the Library class."""
    
    @pytest.fixture
    def temp_library_file(self):
        """Create a temporary library file for testing."""
        filename = "test_library_temp.json"
        # Remove if exists
        if os.path.exists(filename):
            os.remove(filename)
        return filename
    
    @pytest.fixture
    def cleanup_library_file(self, temp_library_file):
        """Cleanup fixture to remove temp library file."""
        yield temp_library_file
        if os.path.exists(temp_library_file):
            os.remove(temp_library_file)
    
    def test_library_initialization_empty(self, cleanup_library_file):
        """Test that a new library starts empty."""
        temp_file = cleanup_library_file
        library = Library(filename=temp_file)
        
        assert len(library.books) == 0
    
    def test_library_add_book(self, cleanup_library_file):
        """Test adding a book to the library."""
        temp_file = cleanup_library_file
        library = Library(filename=temp_file)
        
        book = library.add_book(
            title="The Great Gatsby",
            author="F. Scott Fitzgerald",
            isbn="978-0743273565"
        )
        
        assert book is not None
        assert book.title == "The Great Gatsby"
        assert len(library.books) == 1
        assert library.books[0].isbn == "978-0743273565"
    
    def test_library_add_duplicate_isbn(self, cleanup_library_file):
        """Test that adding a book with duplicate ISBN fails."""
        temp_file = cleanup_library_file
        library = Library(filename=temp_file)
        
        # Add first book
        library.add_book(
            title="Book One",
            author="Author One",
            isbn="978-0000000001"
        )
        
        # Try to add duplicate ISBN
        book = library.add_book(
            title="Book Two",
            author="Author Two",
            isbn="978-0000000001"
        )
        
        assert book is None
        assert len(library.books) == 1
    
    def test_library_add_multiple_books(self, cleanup_library_file):
        """Test adding multiple books to the library."""
        temp_file = cleanup_library_file
        library = Library(filename=temp_file)
        
        library.add_book("Book 1", "Author 1", "ISBN-001")
        library.add_book("Book 2", "Author 2", "ISBN-002")
        library.add_book("Book 3", "Author 3", "ISBN-003")
        
        assert len(library.books) == 3
    
    def test_library_complete_book(self, cleanup_library_file):
        """Test marking a book as borrowed."""
        temp_file = cleanup_library_file
        library = Library(filename=temp_file)
        
        library.add_book("Test Book", "Test Author", "ISBN-TEST")
        
        book = library.complete_book(isbn="ISBN-TEST")
        
        assert book is not None
        assert book.available == False
    
    def test_library_complete_book_already_borrowed(self, cleanup_library_file):
        """Test that borrowing an already borrowed book fails."""
        temp_file = cleanup_library_file
        library = Library(filename=temp_file)
        
        library.add_book("Test Book", "Test Author", "ISBN-TEST")
        library.complete_book(isbn="ISBN-TEST")
        
        book = library.complete_book(isbn="ISBN-TEST")
        
        assert book is None
    
    def test_library_complete_book_not_found(self, cleanup_library_file):
        """Test that borrowing a book with invalid ISBN fails."""
        temp_file = cleanup_library_file
        library = Library(filename=temp_file)
        
        book = library.complete_book(isbn="ISBN-NOT-EXIST")
        
        assert book is None
    
    def test_library_return_book(self, cleanup_library_file):
        """Test returning a borrowed book."""
        temp_file = cleanup_library_file
        library = Library(filename=temp_file)
        
        library.add_book("Test Book", "Test Author", "ISBN-TEST")
        library.complete_book(isbn="ISBN-TEST")
        
        book = library.return_book(isbn="ISBN-TEST")
        
        assert book is not None
        assert book.available == True
    
    def test_library_return_book_already_available(self, cleanup_library_file):
        """Test that returning an available book fails."""
        temp_file = cleanup_library_file
        library = Library(filename=temp_file)
        
        library.add_book("Test Book", "Test Author", "ISBN-TEST")
        
        book = library.return_book(isbn="ISBN-TEST")
        
        assert book is None
    
    def test_library_return_book_not_found(self, cleanup_library_file):
        """Test that returning a book with invalid ISBN fails."""
        temp_file = cleanup_library_file
        library = Library(filename=temp_file)
        
        book = library.return_book(isbn="ISBN-NOT-EXIST")
        
        assert book is None
    
    def test_library_search_books_by_title(self, cleanup_library_file):
        """Test searching books by title."""
        temp_file = cleanup_library_file
        library = Library(filename=temp_file)
        
        library.add_book("The Great Gatsby", "F. Scott Fitzgerald", "ISBN-001")
        library.add_book("Gatsby's Neighbor", "Another Author", "ISBN-002")
        library.add_book("1984", "George Orwell", "ISBN-003")
        
        results = library.search_books("Gatsby")
        
        assert len(results) == 2
        assert results[0].title == "The Great Gatsby"
        assert results[1].title == "Gatsby's Neighbor"
    
    def test_library_search_books_by_author(self, cleanup_library_file):
        """Test searching books by author."""
        temp_file = cleanup_library_file
        library = Library(filename=temp_file)
        
        library.add_book("Book 1", "John Smith", "ISBN-001")
        library.add_book("Book 2", "John Doe", "ISBN-002")
        library.add_book("Book 3", "Jane Smith", "ISBN-003")
        
        results = library.search_books("Smith")
        
        assert len(results) == 2
        assert results[0].author == "John Smith"
        assert results[1].author == "Jane Smith"
    
    def test_library_search_no_results(self, cleanup_library_file):
        """Test searching for non-existent book."""
        temp_file = cleanup_library_file
        library = Library(filename=temp_file)
        
        library.add_book("Test Book", "Test Author", "ISBN-TEST")
        
        results = library.search_books("NonExistent")
        
        assert len(results) == 0
    
    def test_library_search_case_insensitive(self, cleanup_library_file):
        """Test that search is case-insensitive."""
        temp_file = cleanup_library_file
        library = Library(filename=temp_file)
        
        library.add_book("The Great Gatsby", "F. Scott Fitzgerald", "ISBN-001")
        
        results_lower = library.search_books("gatsby")
        results_upper = library.search_books("GATSBY")
        results_mixed = library.search_books("GatsBy")
        
        assert len(results_lower) == 1
        assert len(results_upper) == 1
        assert len(results_mixed) == 1
    
    def test_library_save_and_load_books(self, cleanup_library_file):
        """Test that books are saved and loaded correctly."""
        temp_file = cleanup_library_file
        library = Library(filename=temp_file)
        
        # Add books
        library.add_book("Book 1", "Author 1", "ISBN-001")
        library.add_book("Book 2", "Author 2", "ISBN-002")
        
        # Verify file was created
        assert os.path.exists(temp_file)
        
        # Load from new library instance
        library2 = Library(filename=temp_file)
        
        assert len(library2.books) == 2
        assert library2.books[0].title == "Book 1"
        assert library2.books[1].title == "Book 2"
    
    def test_library_display_books_empty(self, cleanup_library_file):
        """Test displaying an empty library."""
        temp_file = cleanup_library_file
        library = Library(filename=temp_file)
        
        # This should print "No books in the library yet"
        library.display_books()


# =============================================================================
# TEST CLASS: CLIHandler Tests
# =============================================================================
class TestCLIHandler:
    """Test cases for the CLIHandler class."""
    
    @pytest.fixture
    def temp_library_file(self):
        """Create a temporary library file for testing."""
        filename = "test_cli_temp.json"
        if os.path.exists(filename):
            os.remove(filename)
        return filename
    
    @pytest.fixture
    def cleanup_files(self, temp_library_file):
        """Cleanup fixture."""
        yield temp_library_file
        if os.path.exists(temp_library_file):
            os.remove(temp_library_file)
        
        # Remove any exported files
        for file in os.listdir('.'):
            if file.startswith('library_export_') and file.endswith('.txt'):
                os.remove(file)
            elif file.startswith('library_export_') and file.endswith('.csv'):
                os.remove(file)
    
    def test_cli_handler_initialization(self, cleanup_files):
        """Test that CLIHandler initializes correctly."""
        temp_file = cleanup_files
        cli = CLIHandler()
        
        assert cli.library is not None
        assert len(cli.library.books) == 0
    
    def test_create_parser(self, cleanup_files):
        """Test that parser is created with all commands."""
        cli = CLIHandler()
        parser = cli.create_parser()
        
        # Test that parser accepts valid commands
        args = parser.parse_args(['add-task', '--title', 'Test', 
                                '--author', 'Author', '--isbn', 'ISBN-1'])
        assert args.command == 'add-task'
        
        args = parser.parse_args(['complete-task', '--isbn', 'ISBN-1'])
        assert args.command == 'complete-task'
        
        args = parser.parse_args(['return-task', '--isbn', 'ISBN-1'])
        assert args.command == 'return-task'
        
        args = parser.parse_args(['list'])
        assert args.command == 'list'
        
        args = parser.parse_args(['search', '--query', 'Test'])
        assert args.command == 'search'
        
        args = parser.parse_args(['export', '--format', 'txt'])
        assert args.command == 'export'
    
    def test_handle_add_task(self, cleanup_files):
        """Test handling add-task command."""
        cli = CLIHandler()
        parser = cli.create_parser()
        
        args = parser.parse_args([
            'add-task',
            '--title', 'The Great Gatsby',
            '--author', 'F. Scott Fitzgerald',
            '--isbn', '978-0743273565'
        ])
        
        cli.handle_command(args)
        
        assert len(cli.library.books) == 1
        assert cli.library.books[0].title == "The Great Gatsby"
    
    def test_handle_complete_task(self, cleanup_files):
        """Test handling complete-task command."""
        cli = CLIHandler()
        parser = cli.create_parser()
        
        # Add a book first
        args = parser.parse_args([
            'add-task',
            '--title', 'Test Book',
            '--author', 'Test Author',
            '--isbn', 'ISBN-TEST'
        ])
        cli.handle_command(args)
        
        # Complete the book
        args = parser.parse_args([
            'complete-task',
            '--isbn', 'ISBN-TEST'
        ])
        cli.handle_command(args)
        
        assert cli.library.books[0].available == False
    
    def test_handle_return_task(self, cleanup_files):
        """Test handling return-task command."""
        cli = CLIHandler()
        parser = cli.create_parser()
        
        # Add and complete a book
        args = parser.parse_args([
            'add-task',
            '--title', 'Test Book',
            '--author', 'Test Author',
            '--isbn', 'ISBN-TEST'
        ])
        cli.handle_command(args)
        
        args = parser.parse_args([
            'complete-task',
            '--isbn', 'ISBN-TEST'
        ])
        cli.handle_command(args)
        
        # Return the book
        args = parser.parse_args([
            'return-task',
            '--isbn', 'ISBN-TEST'
        ])
        cli.handle_command(args)
        
        assert cli.library.books[0].available == True
    
    def test_handle_list_command(self, cleanup_files):
        """Test handling list command."""
        cli = CLIHandler()
        parser = cli.create_parser()
        
        # Add books
        for i in range(3):
            args = parser.parse_args([
                'add-task',
                '--title', f'Book {i+1}',
                '--author', f'Author {i+1}',
                '--isbn', f'ISBN-{i+1}'
            ])
            cli.handle_command(args)
        
        # List books
        args = parser.parse_args(['list'])
        cli.handle_command(args)
        
        # Should display all books
        assert len(cli.library.books) == 3
    
    def test_handle_search_command(self, cleanup_files):
        """Test handling search command."""
        cli = CLIHandler()
        parser = cli.create_parser()
        
        # Add books
        args = parser.parse_args([
            'add-task',
            '--title', 'The Great Gatsby',
            '--author', 'F. Scott Fitzgerald',
            '--isbn', 'ISBN-001'
        ])
        cli.handle_command(args)
        
        args = parser.parse_args([
            'add-task',
            '--title', 'Gatsby's Neighbor',
            '--author', 'Another Author',
            '--isbn', 'ISBN-002'
        ])
        cli.handle_command(args)