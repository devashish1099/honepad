# Chat service level 3

- `edit(user_id, message_id, text)` changes the text of a message.
  Only its author may edit it. Returns false if the message is unknown
  or deleted, the user is not the author, or `text` is empty. An
  edited message shows in `history` as `"user_id:text (edited)"`.
- `delete_message(user_id, message_id)` deletes the author's own
  message. Returns false if unknown, already deleted, or not the
  author. Deleted messages vanish from `history` and no longer count
  as unread.
- `mentions(user_id)` returns the ids of messages, oldest first, whose
  current text contains the word `"@user_id"`. Words are separated by
  single spaces and must match exactly (`"@bobby"` is not `"@bob"`).
  Only messages that are not deleted, not written by the user, and in
  a channel the user is a member of right now count.

## Example

```
create_channel("dev") -> true
join("ann", "dev") -> true
join("bob", "dev") -> true
post("ann", "dev", "helo @bob") -> "m1"
edit("bob", "m1", "hacked") -> false
edit("ann", "m1", "hello @bob") -> true
post("ann", "dev", "@bobby wrong") -> "m2"
unread("bob", "dev") -> 2
mentions("bob") -> ["m1"]
delete_message("ann", "m1") -> true
delete_message("ann", "m1") -> false
unread("bob", "dev") -> 1
mentions("bob") -> []
post("bob", "dev", "@bob me") -> "m3"
mentions("bob") -> []
history("dev", 5) -> ["ann:@bobby wrong", "bob:@bob me"]
```
