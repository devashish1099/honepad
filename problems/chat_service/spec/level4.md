# Chat service level 4

Messages can have threads.

- `reply(user_id, parent_id, text)` adds a reply to a message and
  returns the reply's id from the same id sequence. Returns null if
  the parent is unknown, deleted or itself a reply, `text` is empty,
  or the user is not a member of the parent's channel.
- `thread(message_id)` returns the replies to a message, oldest first,
  formatted like `history` (edited replies are marked). Null if the
  message is unknown, deleted, or a reply.
- `unread_total(user_id)` returns the sum of `unread` over every
  channel the user is a member of. No channels is 0.

Replies never appear in `history` and never count as unread, but they
can be edited and deleted like messages and they count in `mentions`.
Deleting a message deletes its replies.

## Example

```
create_channel("dev") -> true
join("ann", "dev") -> true
join("bob", "dev") -> true
post("ann", "dev", "lunch?") -> "m1"
reply("bob", "m1", "yes @ann") -> "m2"
reply("cat", "m1", "me too") -> null
reply("ann", "m2", "nested") -> null
thread("m1") -> ["bob:yes @ann"]
history("dev", 5) -> ["ann:lunch?"]
mentions("ann") -> ["m2"]
unread_total("ann") -> 0
unread_total("bob") -> 1
delete_message("ann", "m1") -> true
thread("m1") -> null
mentions("ann") -> []
```
