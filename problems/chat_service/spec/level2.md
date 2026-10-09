# Chat service level 2

Each member has a read position in each channel.

- `unread(user_id, channel_id)` counts the channel's messages created
  after the member's read position, not counting the member's own.
  Not a member is null.
- `mark_read(user_id, channel_id)` returns what `unread` would return,
  then moves the read position past every message that exists. Not a
  member is null.
- `leave(user_id, channel_id)` returns true if the user was a member.
  Leaving forgets the read position.

- `most_active(channel_id, n)` returns the top `n` posters of the
  channel as `"user_id(count)"`, most messages first, ties by user id
  A to Z. Users who left still count. `n <= 0` is an empty list.
  Unknown channel is null.

Joining puts the read position after every message that exists, so
older messages are never unread. Posting moves the poster's read
position to their new message.

## Example

```
create_channel("dev") -> true
join("ann", "dev") -> true
join("bob", "dev") -> true
post("ann", "dev", "one") -> "m1"
post("ann", "dev", "two") -> "m2"
unread("bob", "dev") -> 2
unread("ann", "dev") -> 0
post("bob", "dev", "three") -> "m3"
unread("bob", "dev") -> 0
unread("ann", "dev") -> 1
join("cat", "dev") -> true
unread("cat", "dev") -> 0
post("ann", "dev", "four") -> "m4"
mark_read("cat", "dev") -> 1
unread("cat", "dev") -> 0
leave("bob", "dev") -> true
unread("bob", "dev") -> null
most_active("dev", 2) -> ["ann(3)", "bob(1)"]
most_active("dev", 5) -> ["ann(3)", "bob(1)"]
```
