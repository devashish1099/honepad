# Chat service level 1

A team chat has channels. Users join channels and post messages.

- `create_channel(channel_id)` returns true if created, false if it
  exists.
- `join(user_id, channel_id)` returns true if the user joined. False
  if the channel is unknown or the user is already a member. Users
  need no registration.
- `post(user_id, channel_id, text)` adds a message and returns its id.
  Ids are `"m1"`, `"m2"`, ... counting every message ever created, in
  every channel. Returns null, using no id, if the user is not a
  member of a known channel or `text` is empty.
- `history(channel_id, n)` returns the last `n` messages of the
  channel, oldest first, each as `"user_id:text"`. Fewer messages than
  `n` returns them all; `n <= 0` is an empty list. Unknown channel is
  null. Anyone may read history.

## Example

```
create_channel("dev") -> true
create_channel("dev") -> false
join("ann", "dev") -> true
join("bob", "dev") -> true
join("ann", "dev") -> false
join("cat", "ops") -> false
post("ann", "dev", "hello") -> "m1"
post("cat", "dev", "hi") -> null
post("bob", "dev", "hey ann") -> "m2"
post("bob", "dev", "") -> null
post("ann", "dev", "standup at 10") -> "m3"
history("dev", 2) -> ["bob:hey ann", "ann:standup at 10"]
history("dev", 10) -> ["ann:hello", "bob:hey ann", "ann:standup at 10"]
history("dev", 0) -> []
history("ops", 1) -> null
```
