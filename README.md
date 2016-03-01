# Sync local SSH keys with AWS EC2

Minimum working version.

## Problems

### Asks for passphrase > 1 time per key

To do: just use "ssh-add -l" in the beginning and work with that.
i.e. if no key is available -> loudly complain, prompt the user to "ssh-add" and try again?

### Only accepts basic input

If no input is provided, looks for private keys in ~/.ssh; otherwise takes multiple paths as input.

### Files shouldn't need to be present

If we need to retrive the pubkeys, we can use `ssh-add -L`
(that way, it will work if someone is using an agent.)


## To do

### Key names

Keys should be named as follows:

`<fingerprint> - <username> - <comment>`

* **fingerprint**: output of `ssh-add -l` (which is different from the fingerprint that appears in `aws ec2 describe-key-pairs`)
* **username**: `os.getenv('USER')`
* **comment**: comment that appears in `ssh-add -l`, if present

### Integration in workshop deployment

Take all this and make it a sync function in the deploy script (which is currently trainctl).
