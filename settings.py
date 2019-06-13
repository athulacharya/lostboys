# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-lostboys.json
SCOPES = ['https://www.googleapis.com/auth/gmail.compose',
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/gmail.readonly']

# Where the client secret for API access is stored
CLIENT_SECRET_FILE = 'client_secret.json'

# Sending email address. Must be a gmail account; may be different
# from the account for API access. May be a valid send-as alias
# of the account.
SENDER = 'sender@gmail.com'

# Person who's getting the emails AFAIK this can actually be the same
# as the sending account, but I haven't tested it.
RECEIVER = 'recipient@anywhere.com'

# Whose followers are you monitoring?
ACCOUNT = "YourAccountName"
