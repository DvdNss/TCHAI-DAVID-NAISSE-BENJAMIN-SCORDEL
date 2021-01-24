import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa


def sign(uname, msg):
    """Returns the signature given the username and the message.

        - uname -> Str
        - msg -> Str
        """

    msg = bytes(msg, 'utf-8')  # Passes the msg into utf-8 format
    private_key = get_private_key(uname)  # Pulls the private key of user
    signature = private_key.sign(  # Builds the signature
        msg,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature  # Returns the signature


def verification(uname, signature, msg):
    """Returns true if verification is fine or false if it isn't given the username, the signature and the message.

        - uname -> Str
        - signature -> signature
        - msg -> Str
        """

    msg = bytes(msg, 'utf-8')  # Passes the msg into utf-8 format
    public_key = get_public_key(uname)  # Pulls the public key of user
    try:
        public_key.verify(  # Verifies signature
            signature,
            msg,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
    except Exception:
        return False
    return True


def generate_key(uname):
    """Generates a key given a username.

        - uname -> Str
        """

    private_key = rsa.generate_private_key(  # Generates a private key for user
        public_exponent=65537,
        key_size=512,
        backend=default_backend()
    )
    public_key = private_key.public_key()  # Generates a public key for user

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    os.mkdir('user_key/' + uname)  # Saves the private key in user_key/uname/
    with open('user_key/' + uname + '/pvk.pem', 'wb') as f:
        f.write(private_pem)

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open('user_key/' + uname + '/pbk.pem', 'wb') as f: # Saves the public key in user_key/uname/
        f.write(public_pem)


def get_private_key(uname):
    """Returns the private key of a given username.

        - uname -> Str
        """

    with open("user_key/" + uname + "/pvk.pem", "rb") as key_file:  # Open the uname's private key file
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )
        return private_key  # Returns the private key


def get_public_key(uname):
    """Returns the public key given a username.

        - uname -> Str
        """

    with open("user_key/" + uname + "/pbk.pem", "rb") as key_file:  # Open the uname's public key file
        public_key = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )
        return public_key  # Returns public key


def get_keys(uname):
    """Gets both keys of a username.

        - uname -> Str
        """

    return get_public_key(uname), get_private_key(uname)


def utf8(s: bytes):
    """Converts bytes to utf-8 format.

        - s -> bytes
        """

    return str(s, 'utf-8')
