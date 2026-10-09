import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeSet;

class Loan {
    final String bookId;
    final int start;
    Integer end;

    Loan(String bookId, int start) {
        this.bookId = bookId;
        this.start = start;
    }
}

class Book {
    int free;
    int borrows = 0;
    final Deque<String> holds = new ArrayDeque<>();

    Book(int copies) {
        this.free = copies;
    }
}

class Member {
    final List<Loan> history = new ArrayList<>();
    final Map<String, Loan> open = new HashMap<>();
    int frozenFines = 0;
    int paid = 0;
}

public class Simulation {
    static final int DAY = 86400;
    static final int LOAN_PERIOD = 14 * DAY;
    static final int FINE_PER_DAY = 10;

    private final Map<String, Book> books = new HashMap<>();
    private final Map<String, Member> members = new HashMap<>();

    public Simulation() {}

    public boolean addBook(int timestamp, String bookId, int copies) {
        if (books.containsKey(bookId) || copies <= 0) {
            return false;
        }
        books.put(bookId, new Book(copies));
        return true;
    }

    public Integer borrow(int timestamp, String memberId, String bookId) {
        Book book = books.get(bookId);
        if (book == null || book.free == 0) {
            return null;
        }
        Member member = members.get(memberId);
        if (member != null && (member.open.containsKey(bookId) || fine(member, timestamp) > 0)) {
            return null;
        }
        book.free--;
        startLoan(timestamp, memberId, book, bookId);
        return book.free;
    }

    public Integer returnBook(int timestamp, String memberId, String bookId) {
        Member member = members.get(memberId);
        if (member == null) {
            return null;
        }
        Loan loan = member.open.remove(bookId);
        if (loan == null) {
            return null;
        }
        loan.end = timestamp;
        member.frozenFines += accrued(loan.start, timestamp);
        Book book = books.get(bookId);
        if (book.holds.isEmpty()) {
            book.free++;
        } else {
            startLoan(timestamp, book.holds.pollFirst(), book, bookId);
        }
        return book.free;
    }

    public List<String> topBooks(int timestamp, int n) {
        List<String> ids = new ArrayList<>(books.keySet());
        ids.sort(
                (a, b) -> {
                    int byCount = Integer.compare(books.get(b).borrows, books.get(a).borrows);
                    return byCount != 0 ? byCount : a.compareTo(b);
                });
        List<String> out = new ArrayList<>();
        for (String id : ids.subList(0, Math.min(n, ids.size()))) {
            out.add(id + "(" + books.get(id).borrows + ")");
        }
        return out;
    }

    public Integer getFine(int timestamp, String memberId) {
        Member member = members.get(memberId);
        return member == null ? null : fine(member, timestamp);
    }

    public Integer payFine(int timestamp, String memberId, int amount) {
        Member member = members.get(memberId);
        if (member == null) {
            return null;
        }
        int owed = fine(member, timestamp);
        if (amount <= 0 || amount > owed) {
            return null;
        }
        member.paid += amount;
        return owed - amount;
    }

    public Integer reserve(int timestamp, String memberId, String bookId) {
        Book book = books.get(bookId);
        if (book == null || book.free > 0 || book.holds.contains(memberId)) {
            return null;
        }
        Member member = members.get(memberId);
        if (member != null && member.open.containsKey(bookId)) {
            return null;
        }
        members.computeIfAbsent(memberId, k -> new Member());
        book.holds.addLast(memberId);
        return book.holds.size();
    }

    public List<String> loansAt(int timestamp, String memberId, int timeAt) {
        Member member = members.get(memberId);
        if (member == null) {
            return null;
        }
        Set<String> held = new TreeSet<>();
        for (Loan loan : member.history) {
            if (loan.start <= timeAt && (loan.end == null || timeAt < loan.end)) {
                held.add(loan.bookId);
            }
        }
        return new ArrayList<>(held);
    }

    private void startLoan(int timestamp, String memberId, Book book, String bookId) {
        Member member = members.computeIfAbsent(memberId, k -> new Member());
        Loan loan = new Loan(bookId, timestamp);
        member.history.add(loan);
        member.open.put(bookId, loan);
        book.borrows++;
    }

    private static int fine(Member member, int now) {
        int total = member.frozenFines - member.paid;
        for (Loan loan : member.open.values()) {
            total += accrued(loan.start, now);
        }
        return total;
    }

    private static int accrued(int start, int now) {
        long late = (long) now - start - LOAN_PERIOD;
        if (late <= 0) {
            return 0;
        }
        return (int) ((late + DAY - 1) / DAY) * FINE_PER_DAY;
    }
}
