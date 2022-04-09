from passlib.context import CryptContext
crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

password = "Admin" #put your password.
print(crypt_context.hash(password))

# copy the encrypted password and paste that into initialize.py file.