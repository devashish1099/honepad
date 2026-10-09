import java.util.List;

public class Simulation {
    public Simulation() {}

    /**
     * Add a book with {@code copies} copies. Returns false if the id exists
     * or copies is not positive.
     */
    public boolean addBook(int timestamp, String bookId, int copies) {
        return false;
    }

    /**
     * Borrow one copy. Returns copies left, or null if the book is missing,
     * none is free, or the member already holds it.
     */
    public Integer borrow(int timestamp, String memberId, String bookId) {
        return null;
    }

    /**
     * Return a held copy. Returns free copies after the return, or null if
     * the member does not hold the book.
     */
    public Integer returnBook(int timestamp, String memberId, String bookId) {
        return null;
    }

    /**
     * Top books as {@code id(count)} by total loans, then id. Example:
     * {@code ["b2(2)", "b1(1)", "b3(0)"]}.
     */
    public List<String> topBooks(int timestamp, int n) {
        return null;
    }

    /**
     * Frozen plus open-loan fines minus payments. 10 per started late day,
     * due 1209600 after the loan starts. Null if the member is unknown.
     */
    public Integer getFine(int timestamp, String memberId) {
        return null;
    }

    /**
     * Pay toward the fine. Returns what is still owed, or null if unknown,
     * not positive, or more than is owed.
     */
    public Integer payFine(int timestamp, String memberId, int amount) {
        return null;
    }

    /**
     * Join the hold queue. Returns the 1-based position, or null if the book
     * is missing, a copy is free, the member holds it, or is already queued.
     */
    public Integer reserve(int timestamp, String memberId, String bookId) {
        return null;
    }

    /**
     * Book ids held at {@code timeAt}, sorted. A loan covers
     * {@code [start, return)}. Null if the member is unknown.
     */
    public List<String> loansAt(int timestamp, String memberId, int timeAt) {
        return null;
    }
}
