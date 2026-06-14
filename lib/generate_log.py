import argparse
import json
import requests
from datetime import datetime
from typing import List, Dict, Optional

# =============================================================================
# CLASS: Book - Represents a single book in the library
# =============================================================================
class Book:
    
    def __init__(self, title: str, author: str, isbn: str, available: bool = True):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.available = available
        self.added_date = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    def to_dict(self) -> Dict:
        return {
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'available': self.available,
            'added_date': self.added_date
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Book':
        return cls(
            title=data['title'],
            author=data['author'],
            isbn=data['isbn'],
            available=data.get('available', True)
        )
    
    def __str__(self) -> str:
        status = "✓ Available" if self.available else "✗ Borrowed"
        return f"[{self.isbn}] {self.title} by {self.author} - {status}"


# =============================================================================
# CLASS: Library - Manages the collection of books
# =============================================================================
class Library:
    """Manage a library of books with add, complete (borrow), and display operations."""
    
    def __init__(self, filename: str = 'library_data.json'):
        self.filename = filename
        self.books: List[Book] = []
        self.load_books()
    
    def load_books(self) -> None:
        """Load books from JSON file."""
        try:
            with open(self.filename, 'r') as file:
                data = json.load(file)
                self.books = [Book.from_dict(book) for book in data]
        except FileNotFoundError:
            self.books = []
    
    def save_books(self) -> None:
        """Save books to JSON file."""
        data = [book.to_dict() for book in self.books]
        with open(self.filename, 'w') as file:
            json.dump(data, file, indent=2)
    
    def add_book(self, title: str, author: str, isbn: str) -> Book:
        """Add a new book to the library."""
        # Check for duplicate ISBN
        for book in self.books:
            if book.isbn == isbn:
                print(f"Error: Book with ISBN {isbn} already exists!")
                return None
        
        new_book = Book(title=title, author=author, isbn=isbn)
        self.books.append(new_book)
        self.save_books()
        print(f"✓ Book added successfully: {new_book}")
        return new_book
    
    def complete_book(self, isbn: str) -> Optional[Book]:
        """Mark a book as complete (borrowed) by ISBN."""
        for book in self.books:
            if book.isbn == isbn:
                if not book.available:
                    print(f"Error: Book '{book.title}' is already borrowed!")
                    return None
                
                book.available = False
                self.save_books()
                print(f"✓ Book marked as borrowed: {book}")
                return book
        
        print(f"Error: No book found with ISBN {isbn}")
        return None
    
    def return_book(self, isbn: str) -> Optional[Book]:
        """Return a borrowed book (make it available again)."""
        for book in self.books:
            if book.isbn == isbn:
                if book.available:
                    print(f"Error: Book '{book.title}' is already available!")
                    return None
                
                book.available = True
                self.save_books()
                print(f"✓ Book returned successfully: {book}")
                return book
        
        print(f"Error: No book found with ISBN {isbn}")
        return None
    
    def display_books(self) -> None:
        """Display all books in the library."""
        if not self.books:
            print("No books in the library yet.")
            return
        
        print("\n" + "=" * 70)
        print("LIBRARY BOOK COLLECTION")
        print("=" * 70)
        
        for i, book in enumerate(self.books, 1):
            print(f"{i}. {book}")
        
        print("=" * 70)
        total = len(self.books)
        available = len([b for b in self.books if b.available])
        borrowed = total - available
        print(f"Total: {total} books | Available: {available} | Borrowed: {borrowed}")
        print()
    
    def search_books(self, query: str) -> List[Book]:
        """Search books by title or author."""
        results = []
        query_lower = query.lower()
        
        for book in self.books:
            if query_lower in book.title.lower() or query_lower in book.author.lower():
                results.append(book)
        
        return results
    
    def fetch_book_from_api(self, title: str) -> Optional[Book]:
        """Fetch book data from external API (using JSONPlaceholder as demo)."""
        try:
            # Using JSONPlaceholder API to fetch book-like data
            response = requests.get(
                "https://jsonplaceholder.typicode.com/posts",
                params={'title': title}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    # Create book from API response
                    book_data = data[0]
                    book = Book(
                        title=book_data.get('title', title),
                        author=book_data.get('author', 'Unknown Author'),
                        isbn=f"ISBN-{datetime.now().strftime('%Y%m%d%H%M')}"
                    )
                    return book
        except requests.RequestException as e:
            print(f"API fetch error: {e}")
        
        return None


# =============================================================================
# CLASS: CLIHandler - Handles command-line interface operations
# ==============================================================================
class CLIHandler:
    """Parse and handle command-line arguments for the library CLI tool."""
    
    def __init__(self):
        self.library = Library()
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser with all commands."""
        parser = argparse.ArgumentParser(
            prog='library-cli',
            description='Library Book Manager CLI - Manage your book collection',
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        # Create subcommands
        subparsers = parser.add_subparsers(
            dest='command',
            title='commands',
            description='Available commands for library management',
            required=True
        )
        
        # --- add-task: Add a book to the library ---
        add_parser = subparsers.add_parser(
            'add-task',
            help='Add a new book to the library'
        )
        add_parser.add_argument(
            '--title',
            required=True,
            help='Book title'
        )
        add_parser.add_argument(
            '--author',
            required=True,
            help='Book author'
        )
        add_parser.add_argument(
            '--isbn',
            required=True,
            help='Book ISBN number'
        )
        add_parser.add_argument(
            '--from-api',
            action='store_true',
            help='Fetch book data from external API'
        )
        
        # --- complete-task: Mark a book as borrowed ---
        complete_parser = subparsers.add_parser(
            'complete-task',
            help='Mark a book as borrowed (complete)'
        )
        complete_parser.add_argument(
            '--isbn',
            required=True,
            help='Book ISBN to mark as borrowed'
        )
        
        # --- return-task: Return a borrowed book ---
        return_parser = subparsers.add_parser(
            'return-task',
            help='Return a borrowed book'
        )
        return_parser.add_argument(
            '--isbn',
            required=True,
            help='Book ISBN to return'
        )
        
        # --- list: Display all books ---
        list_parser = subparsers.add_parser(
            'list',
            help='Display all books in the library'
        )
        
        # --- search: Search books ---
        search_parser = subparsers.add_parser(
            'search',
            help='Search books by title or author'
        )
        search_parser.add_argument(
            '--query',
            required=True,
            help='Search query (title or author)'
        )
        
        # --- export: Export library to file ---
        export_parser = subparsers.add_parser(
            'export',
            help='Export library to TXT or CSV file'
        )
        export_parser.add_argument(
            '--format',
            choices=['txt', 'csv'],
            default='txt',
            help='Export format (default: txt)'
        )
        export_parser.add_argument(
            '--output',
            default=None,
            help='Output filename (default: auto-generated)'
        )
        
        return parser
    
    def handle_command(self, args: argparse.Namespace) -> None:
        """Handle the executed command."""
        if args.command == 'add-task':
            if args.from_api:
                # Fetch from API
                book = self.library.fetch_book_from_api(args.title)
                if book:
                    self.library.books.append(book)
                    self.library.save_books()
                    print(f"✓ Book fetched from API and added: {book}")
                else:
                    print("Failed to fetch book from API")
            else:
                # Add manually
                self.library.add_book(
                    title=args.title,
                    author=args.author,
                    isbn=args.isbn
                )
        
        elif args.command == 'complete-task':
            self.library.complete_book(isbn=args.isbn)
        
        elif args.command == 'return-task':
            self.library.return_book(isbn=args.isbn)
        
        elif args.command == 'list':
            self.library.display_books()
        
        elif args.command == 'search':
            results = self.library.search_books(query=args.query)
            if not results:
                print(f"No books found matching '{args.query}'")
            else:
                print(f"\nFound {len(results)} book(s) matching '{args.query}':\n")
                for i, book in enumerate(results, 1):
                    print(f"{i}. {book}")
                print()
        
        elif args.command == 'export':
            self.export_library(format=args.format, output=args.output)
    
    def export_library(self, format: str = 'txt', output: str = None) -> None:
        """Export library to file using File I/O."""
        if not self.library.books:
            print("No books to export.")
            return
        
        # Generate output filename
        if output is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            output = f'library_export_{timestamp}.{format}'
        
        # Write to file
        with open(output, 'w') as file:
            if format == 'csv':
                # CSV format
                file.write("title,author,isbn,available,added_date\n")
                for book in self.library.books:
                    file.write(f"{book.title},{book.author},{book.isbn},"
                               f"{book.available},{book.added_date}\n")
                print(f"✓ Library exported to CSV: {output}")
            else:
                # TXT format
                file.write("=" * 70 + "\n")
                file.write("LIBRARY BOOK EXPORT\n")
                file.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                file.write("=" * 70 + "\n\n")
                
                for i, book in enumerate(self.library.books, 1):
                    file.write(f"{i}. {book}\n")
                
                file.write("\n" + "=" * 70 + "\n")
                file.write(f"Total Books: {len(self.library.books)}\n")
                file.write("=" * 70 + "\n")
                
            print(f"✓ Library exported to: {output}")
            
        def generate_log(log_data, filename=None):
            
            if not isinstance(log_data, list):
            raise ValueError("log_data must be a list")
    
            if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d')
            filename = f"log_{timestamp}.txt"
        

            with open(filename, 'w') as file:
            for entry in log_data:
                file.write(f"{entry}\n")
        
        print(f"Log written to {filename}")
        
        return filename


if __name__ == "__main__":
    # Example usage
    log_data = ["User logged in", "User updated profile", "Report exported"]
    filename = generate_log(log_data)


def main():
    """Main entry point for the CLI tool."""
    cli = CLIHandler()
    parser = cli.create_parser()
    args = parser.parse_args()
    
    cli.handle_command(args)


if __name__ == "__main__":
    main()